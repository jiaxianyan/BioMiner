"""
BioMiner 交互式 UI 后端
在 BioMiner 项目根目录下运行，通过 API 调用 example_open_source.py 进行推理。
"""
import os
import sys
import subprocess
import json
import yaml
import uuid
import csv
import threading
import time
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

# BioMiner 项目根目录（BioMiner_UI 的上级目录）
BIOMINER_ROOT = Path(__file__).resolve().parent.parent.parent
# 从项目根执行 `python BioMiner_UI/backend/app.py` 时，sys.path[0] 为 backend 目录，
# 无法解析顶层包 BioMiner；必须将项目根加入 path，Given SMILES 等逻辑才能 import metric_fn。
_root_str = str(BIOMINER_ROOT)
if _root_str not in sys.path:
    sys.path.insert(0, _root_str)
CONFIG_PATH_DEFAULT = BIOMINER_ROOT / "BioMiner" / "config" / "default_open_source.yaml"
EXAMPLE_SCRIPT = BIOMINER_ROOT / "example_open_source.py"
UPLOAD_FOLDER = BIOMINER_ROOT / "BioMiner_UI" / "uploads"
RESULTS_FOLDER = BIOMINER_ROOT / "tmp_output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="../frontend")
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB

# 当前推理任务状态与日志
_jobs = {}
_jobs_lock = threading.Lock()

# stage_one.pkl 缓存：避免每次请求都反序列化大文件
# key: output_dir(str)
_stage_one_cache = {}
_stage_one_cache_lock = threading.Lock()
_STAGE_ONE_CACHE_MAX = 3
_STAGE_ONE_CACHE_TTL_S = 10 * 60


def _get_stage_one_cached(output_dir: Path):
    """
    返回 (page_image_pathss, bboxes_with_pred_smiless, doc_name_to_index)。
    对 output_dir/stage_one.pkl 做带 TTL 的内存缓存，减少 I/O 与 pickle 开销。
    """
    pkl_path = output_dir / "stage_one.pkl"
    if not pkl_path.is_file():
        raise FileNotFoundError("未找到 stage_one.pkl")
    key = str(output_dir)
    now = time.time()
    with _stage_one_cache_lock:
        ent = _stage_one_cache.get(key)
        if ent and (now - ent["ts"] <= _STAGE_ONE_CACHE_TTL_S) and ent.get("pkl_mtime") == pkl_path.stat().st_mtime:
            ent["ts"] = now
            return ent["page_image_pathss"], ent["bboxes_with_pred_smiless"], ent["doc_name_to_index"]

    import pickle
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    page_image_pathss, _, _, _, _, _, _, bboxes_with_pred_smiless = data

    doc_name_to_index = {}
    for i, path_list in enumerate(page_image_pathss):
        if not path_list:
            continue
        try:
            doc_name_to_index[Path(path_list[0]).parent.name] = i
        except Exception:
            continue

    with _stage_one_cache_lock:
        _stage_one_cache[key] = {
            "ts": now,
            "pkl_mtime": pkl_path.stat().st_mtime,
            "page_image_pathss": page_image_pathss,
            "bboxes_with_pred_smiless": bboxes_with_pred_smiless,
            "doc_name_to_index": doc_name_to_index,
        }
        # 简单 LRU：按 ts 从旧到新裁剪
        if len(_stage_one_cache) > _STAGE_ONE_CACHE_MAX:
            for k, _ in sorted(_stage_one_cache.items(), key=lambda kv: kv[1].get("ts", 0))[: max(0, len(_stage_one_cache) - _STAGE_ONE_CACHE_MAX)]:
                _stage_one_cache.pop(k, None)

    return page_image_pathss, bboxes_with_pred_smiless, doc_name_to_index


def _run_inference(pdf_path: str, output_dir: str, config_path: str, job_id: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BIOMINER_ROOT)
    cmd = [
        sys.executable,
        str(EXAMPLE_SCRIPT),
        "--config_path", config_path,
        "--pdf", pdf_path,
        "--output_dir", output_dir,
    ]
    try:
        with _jobs_lock:
            _jobs[job_id]["status"] = "running"
        proc = subprocess.Popen(
            cmd,
            cwd=str(BIOMINER_ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip("\n\r")
            if line:
                with _jobs_lock:
                    _jobs[job_id]["logs"].append(line)
        proc.wait()
        with _jobs_lock:
            _jobs[job_id]["status"] = "completed" if proc.returncode == 0 else "failed"
            _jobs[job_id]["returncode"] = proc.returncode
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["logs"].append(str(e))


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/static/<path:filename>")
def static_file(filename):
    return send_from_directory(Path(app.static_folder) / "static", filename)


@app.route("/api/logo", methods=["GET"])
def platform_logo():
    """返回平台 logo（visualization/logo.jpg）。"""
    logo_path = BIOMINER_ROOT / "visualization" / "logo.jpg"
    if not logo_path.exists() or not logo_path.is_file():
        return jsonify({"error": "logo 不存在"}), 404
    return send_file(logo_path, mimetype="image/jpeg", as_attachment=False)


@app.route("/api/mol_rdkit_svg", methods=["GET"])
def mol_rdkit_svg():
    """
    使用 RDKit 将 SMILES 绘制为 2D 结构图（SVG），供前端 <img src=...> 展示。
    """
    smiles = request.args.get("smiles", "")
    if not smiles or not str(smiles).strip():
        return jsonify({"error": "缺少 smiles"}), 400
    smiles = str(smiles).strip()
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        from rdkit.Chem.Draw import rdMolDraw2D

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return jsonify({"error": "无法解析 SMILES"}), 400
        mol = Chem.Mol(mol)
        AllChem.Compute2DCoords(mol)
        w, h = 380, 260
        d2d = rdMolDraw2D.MolDraw2DSVG(w, h)
        d2d.DrawMolecule(mol)
        d2d.FinishDrawing()
        svg = d2d.GetDrawingText()
        return Response(svg, mimetype="image/svg+xml; charset=utf-8")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config", methods=["GET"])
def get_config():
    """读取当前使用的配置文件内容（用于 API 模式的关键字段）。"""
    path = request.args.get("path") or str(CONFIG_PATH_DEFAULT)
    path = Path(path)
    if not path.is_absolute():
        path = BIOMINER_ROOT / path
    if not path.exists():
        return jsonify({"error": "Config file not found"}), 404
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        # 只暴露前端需要的字段
        model = data.get("model", {})
        return jsonify({
            "config_path": str(path),
            "base_url": model.get("base_url", ""),
            "api_key": model.get("api_key", ""),
            "text_mllm_type": model.get("text_mllm_type", ""),
            "vision_mllm_type": model.get("vision_mllm_type", ""),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config", methods=["POST"])
def save_config():
    """更新配置文件中的 api_key、base_url、text_mllm_type、vision_mllm_type。"""
    path = request.json.get("config_path") or str(CONFIG_PATH_DEFAULT)
    path = Path(path)
    if not path.is_absolute():
        path = BIOMINER_ROOT / path
    if not path.exists():
        return jsonify({"error": "Config file not found"}), 404
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if "model" not in data:
            data["model"] = {}
        for key in ("base_url", "api_key", "text_mllm_type", "vision_mllm_type"):
            if key in request.json:
                data["model"][key] = request.json[key]
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/run", methods=["POST"])
def run_inference():
    """
    提交推理任务。
    支持：
    - pdf: 服务端已有 PDF 路径（相对项目根或绝对路径）
    - 或通过 form 上传 PDF 文件（字段名 file）
    - output_dir: 输出目录，默认 tmp_output/<job_id>
    - config_path: 配置文件路径，默认 default_open_source.yaml
    """
    job_id = str(uuid.uuid4())[:8]
    pdf_path = request.form.get("pdf") or request.json and request.json.get("pdf")
    output_dir = request.form.get("output_dir") or (request.json and request.json.get("output_dir"))
    config_path = request.form.get("config_path") or (request.json and request.json.get("config_path")) or str(CONFIG_PATH_DEFAULT)

    if not output_dir:
        output_dir = str(RESULTS_FOLDER / job_id)
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = BIOMINER_ROOT / output_dir

    # 上传文件
    if "file" in request.files and request.files["file"].filename:
        f = request.files["file"]
        filename = secure_filename(f.filename) or "uploaded.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        pdf_path = str(UPLOAD_FOLDER / f"{job_id}_{filename}")
        f.save(pdf_path)
    elif not pdf_path:
        return jsonify({"error": "请提供 PDF 路径 (pdf) 或上传 PDF 文件 (file)"}), 400

    pdf_path = Path(pdf_path)
    if not pdf_path.is_absolute():
        pdf_path = BIOMINER_ROOT / pdf_path
    if not pdf_path.exists():
        return jsonify({"error": f"PDF 不存在: {pdf_path}"}), 400

    config_path_resolved = Path(config_path)
    if not config_path_resolved.is_absolute():
        config_path_resolved = BIOMINER_ROOT / config_path_resolved
    if not config_path_resolved.exists():
        return jsonify({"error": f"配置文件不存在: {config_path_resolved}"}), 400

    with _jobs_lock:
        _jobs[job_id] = {
            "status": "pending",
            "pdf": str(pdf_path),
            "output_dir": str(output_dir),
            "config_path": str(config_path_resolved),
            "logs": [],
            "returncode": None,
        }

    thread = threading.Thread(
        target=_run_inference,
        args=(str(pdf_path), str(output_dir), str(config_path_resolved), job_id),
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        "job_id": job_id,
        "output_dir": str(output_dir),
        "message": "任务已提交，请通过 /api/job/<job_id> 查询状态与日志",
    })


@app.route("/api/job/<job_id>", methods=["GET"])
def job_status(job_id):
    with _jobs_lock:
        if job_id not in _jobs:
            return jsonify({"error": "任务不存在"}), 404
        j = _jobs[job_id].copy()
    j["logs"] = j["logs"][-500:]  # 最近 500 行
    return jsonify(j)


def _find_merged_output_unique_csv(doc_dir: Path):
    """在文档目录下查找 merged *output_unique.csv，返回第一个匹配的文件路径，未找到则返回 None。"""
    for f in doc_dir.iterdir():
        if not f.is_file() or not f.name.endswith(".csv"):
            continue
        if "merged" in f.name and "output_unique" in f.name:
            return f
    for f in doc_dir.iterdir():
        if not f.is_file() or not f.name.endswith(".csv"):
            continue
        if "output_unique" in f.name:
            return f
    for f in doc_dir.iterdir():
        if not f.is_file() or not f.name.endswith(".csv"):
            continue
        if "merged" in f.name:
            return f
    return None


@app.route("/api/results", methods=["GET"])
def list_results():
    """汇总 output_dir 下各文档的 merged *output_unique.csv，返回带 doc 列的表格数据（与 extraction 结构一致，避免全盘 walk）。"""
    output_dir = request.args.get("output_dir")
    if not output_dir:
        return jsonify({"error": "缺少 output_dir"}), 400
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = BIOMINER_ROOT / output_dir
    if not output_dir.exists():
        return jsonify({"rows": [], "doc_names": [], "message": "输出目录不存在"})

    extraction_dirs = _get_extraction_dirs(output_dir)
    rows = []
    doc_names_with_file = set()
    for ext_dir in extraction_dirs:
        for doc_dir in ext_dir.iterdir():
            if not doc_dir.is_dir():
                continue
            doc_name = doc_dir.name
            csv_path = _find_merged_output_unique_csv(doc_dir)
            if not csv_path:
                continue
            doc_names_with_file.add(doc_name)
            try:
                with open(csv_path, "r", encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        r_with_doc = dict(r)
                        r_with_doc["doc"] = doc_name
                        rows.append(r_with_doc)
            except Exception:
                continue

    return jsonify({
        "output_dir": str(output_dir),
        "rows": rows,
        "doc_names": sorted(doc_names_with_file),
    })


def _get_pdb_structure_path_from_config(config_path_arg: str | None) -> Path | None:
    """从 YAML 配置读取 data.pdb_structure_path，并解析为绝对路径。"""
    path = CONFIG_PATH_DEFAULT
    if config_path_arg:
        p = Path(config_path_arg)
        if not p.is_absolute():
            p = BIOMINER_ROOT / p
        if p.is_file():
            path = p
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        pdb_rel = (data or {}).get("data", {}).get("pdb_structure_path")
        if not pdb_rel:
            return None
        pdb_path = Path(str(pdb_rel).strip())
        if not pdb_path.is_absolute():
            pdb_path = BIOMINER_ROOT / pdb_path
        return pdb_path
    except Exception:
        return None


def _given_smiles_for_doc(doc_name: str, pdb_structure_path: Path | None) -> str | None:
    """与 extractor.extraction_specific_structure_bioactivity 一致：从 PDB 配套配体文件得到参考 SMILES。"""
    if not pdb_structure_path:
        return None
    try:
        from BioMiner.runner.metric_fn import load_pdb_protein_name_ligand_smiles

        given_smiles, _ = load_pdb_protein_name_ligand_smiles(doc_name, str(pdb_structure_path))
        return given_smiles
    except Exception:
        return None


_PDB_TITLES_CACHE: dict | None = None
_PDB_TITLES_CACHE_MTIME: float | None = None


def _get_pdb_titles_dict() -> dict:
    """
    读取 BioVista/pdb_titles.json；key 为小写 PDB ID（如 6qhr），带 mtime 缓存。
    """
    global _PDB_TITLES_CACHE, _PDB_TITLES_CACHE_MTIME
    path = BIOMINER_ROOT / "BioVista" / "pdb_titles.json"
    if not path.is_file():
        return {}
    try:
        mtime = path.stat().st_mtime
        if _PDB_TITLES_CACHE is not None and _PDB_TITLES_CACHE_MTIME == mtime:
            return _PDB_TITLES_CACHE
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        _PDB_TITLES_CACHE = data
        _PDB_TITLES_CACHE_MTIME = mtime
        return _PDB_TITLES_CACHE
    except Exception:
        return {}


def _pdb_title_for_pdb_id(pdb_id: str | None, titles: dict) -> str | None:
    """
    按 pdb_titles.json 查找 title；key 为小写 PDB ID。
    PoseBuster 等数据下文档/目录名为「序号_8C3N」，而 JSON 仅有「8c3n」键；
    若整串未命中，则从下划线分段中自右向左尝试 4 字符 RCSB 式 ID（首位数字）。
    """
    if not pdb_id or not titles:
        return None
    key = str(pdb_id).strip().lower()
    if not key:
        return None

    def _pick(k: str) -> str | None:
        v = titles.get(k)
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None

    hit = _pick(key)
    if hit is not None:
        return hit

    for part in reversed(key.split("_")):
        pl = part.lower()
        if len(pl) == 4 and pl[0].isdigit() and pl.isalnum():
            hit = _pick(pl)
            if hit is not None:
                return hit
    return None


def _resolve_pdb_id_for_doc(doc_name: str, pdb_structure_path: Path | None) -> str | None:
    """
    与 metric_fn.load_pdb_protein_name_ligand_smiles 中目录名解析一致：
    优先使用 doc 作为 pdb_structure_path 下子目录名；若不存在则取 doc.split('_')[1]（如 106_6qhr -> 6qhr）。
    未配置 pdb_structure_path 时仍从文档名推断，便于界面展示。
    """
    if not doc_name:
        return None
    if not pdb_structure_path:
        parts = doc_name.split("_")
        if len(parts) >= 2:
            return parts[1]
        return doc_name
    base = str(pdb_structure_path)
    pdb_name = doc_name
    if not os.path.exists(os.path.join(base, pdb_name)):
        parts = doc_name.split("_")
        if len(parts) >= 2:
            pdb_name = parts[1]
    return pdb_name


@app.route("/api/activity_given_structure", methods=["GET"])
def activity_given_structure():
    """
    汇总 interface.py 中 `extraction_specific_structure_bioactivity(...)` 生成的：
      {output_dir}/extraction_*/{doc}/*bioactivity_given_structure_*.csv
    返回带 doc 列的行数据，用于新 sheet 展示（分页由前端完成）。
    """
    output_dir = request.args.get("output_dir")
    if not output_dir:
        return jsonify({"error": "缺少 output_dir"}), 400
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = BIOMINER_ROOT / output_dir
    if not output_dir.exists():
        return jsonify({
            "rows": [],
            "doc_names": [],
            "message": "输出目录不存在",
            "given_smiles_by_doc": {},
            "pdb_id_by_doc": {},
            "pdb_title_by_doc": {},
            "pdb_structure_path": None,
        })

    extraction_dirs = _get_extraction_dirs(output_dir)
    rows = []
    doc_names_with_file = set()

    for ext_dir in extraction_dirs:
        # ext_dir.name: extraction_<text_mllm_type>
        text_mllm_type = (
            ext_dir.name[len("extraction_") :]
            if ext_dir.name.startswith("extraction_")
            else ext_dir.name
        )
        for doc_dir in ext_dir.iterdir():
            if not doc_dir.is_dir():
                continue
            doc_name = doc_dir.name
            for f in doc_dir.iterdir():
                if not f.is_file():
                    continue
                if "bioactivity_given_structure" not in f.name:
                    continue
                if not f.name.endswith(".csv"):
                    continue

                try:
                    with open(f, "r", encoding="utf-8", newline="") as fp:
                        reader = csv.DictReader(fp)
                        for r in reader:
                            cleaned = {}
                            for k, v in r.items():
                                if k is None:
                                    continue
                                k_str = str(k).strip()
                                if not k_str:
                                    continue
                                if k_str.lower().startswith("unnamed"):
                                    continue
                                cleaned[k_str] = v
                            if not cleaned:
                                continue
                            cleaned["doc"] = doc_name
                            cleaned["text_mllm_type"] = text_mllm_type
                            cleaned["source_file"] = f.name
                            rows.append(cleaned)
                    doc_names_with_file.add(doc_name)
                except Exception:
                    continue

    config_path_arg = request.args.get("config_path")
    pdb_structure_path = _get_pdb_structure_path_from_config(config_path_arg)
    doc_list = sorted(doc_names_with_file)
    given_smiles_by_doc = {}
    pdb_id_by_doc = {}
    pdb_title_by_doc = {}
    titles_map = _get_pdb_titles_dict()
    for doc_name in doc_list:
        given_smiles_by_doc[doc_name] = _given_smiles_for_doc(doc_name, pdb_structure_path)
        pid = _resolve_pdb_id_for_doc(doc_name, pdb_structure_path)
        pdb_id_by_doc[doc_name] = pid
        pdb_title_by_doc[doc_name] = _pdb_title_for_pdb_id(pid, titles_map)

    return jsonify({
        "output_dir": str(output_dir),
        "rows": rows,
        "doc_names": doc_list,
        "given_smiles_by_doc": given_smiles_by_doc,
        "pdb_id_by_doc": pdb_id_by_doc,
        "pdb_title_by_doc": pdb_title_by_doc,
        "pdb_structure_path": str(pdb_structure_path) if pdb_structure_path else None,
    })


@app.route("/api/results/download", methods=["GET"])
def download_result():
    """下载结果目录中的某个文件。"""
    output_dir = request.args.get("output_dir")
    file_path = request.args.get("file")
    if not output_dir or not file_path:
        return jsonify({"error": "缺少 output_dir 或 file"}), 400
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = BIOMINER_ROOT / output_dir
    full = (output_dir / file_path).resolve()
    if not str(full).startswith(str(output_dir.resolve())):
        return jsonify({"error": "非法路径"}), 403
    if not full.exists() or not full.is_file():
        return jsonify({"error": "文件不存在"}), 404
    return send_file(full, as_attachment=True, download_name=os.path.basename(full))


@app.route("/api/pdf", methods=["GET"])
def serve_pdf():
    """返回指定路径的 PDF 文件（用于预览）。path 为相对项目根的路径，或 uploads/xxx 表示上传文件。"""
    path = request.args.get("path")
    if not path or not path.strip():
        return jsonify({"error": "缺少 path 参数"}), 400
    path = path.strip().lstrip("/")
    if path.startswith("uploads/"):
        full = (UPLOAD_FOLDER / path[8:]).resolve()
        allowed_root = UPLOAD_FOLDER.resolve()
    else:
        full = (BIOMINER_ROOT / path).resolve()
        allowed_root = BIOMINER_ROOT.resolve()
    if not str(full).startswith(str(allowed_root)):
        return jsonify({"error": "非法路径"}), 403
    if not full.exists() or not full.is_file():
        return jsonify({"error": "文件不存在"}), 404
    if full.suffix.lower() != ".pdf":
        return jsonify({"error": "仅支持 PDF 文件"}), 400
    return send_file(full, mimetype="application/pdf", as_attachment=False)


@app.route("/api/activity_doc_pdf", methods=["GET"])
def activity_doc_pdf():
    """
    图表活性抽取结果 sheet 左侧：直接返回某文档的 PDF（用于 iframe 预览）。
    搜索目录：{output_dir}/mineru/{doc}/auto/
    候选文件优先级：origin -> layout -> spans -> middle -> model -> 其它第一个 pdf
    """
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    if not output_dir or doc is None or doc == "":
        return jsonify({"error": "缺少 output_dir 或 doc"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    pdf_auto_dir = output_dir / "mineru" / doc / "auto"
    if not pdf_auto_dir.is_dir():
        return jsonify({"error": "未找到该文档的 mineru/auto 目录"}), 404

    candidates = [
        f"{doc}_origin.pdf",
        f"{doc}_layout.pdf",
        f"{doc}_spans.pdf",
        f"{doc}_middle.pdf",
        f"{doc}_model.pdf",
    ]
    for name in candidates:
        p = pdf_auto_dir / name
        if p.is_file():
            return send_file(p, mimetype="application/pdf", as_attachment=False)

    pdfs = list(pdf_auto_dir.glob("*.pdf"))
    if pdfs:
        return send_file(pdfs[0], mimetype="application/pdf", as_attachment=False)

    return jsonify({"error": "该文档下未找到任何 pdf"}), 404


def _get_merge_detection_dirs(output_dir: Path):
    """
    在 output_dir 下查找分子检测框可视化图目录。
    优先返回 md_merge_*_yolo（无 distinguish），若无则返回 md_merge_*_yolo_distinguish*。
    """
    if not output_dir.exists():
        return []
    dirs = []
    for p in output_dir.iterdir():
        if not p.is_dir() or not p.name.startswith("md_merge_") or "_yolo" not in p.name:
            continue
        if "distinguish" not in p.name:
            dirs.insert(0, p)  # 无 distinguish 的放前面
        else:
            dirs.append(p)
    return dirs


def _get_markush_after_ocsr_viz_dirs(output_dir: Path):
    """
    Markush/OCSR 后可视化目录：md_merge_*_yolo_distinguish_full_markush_after_ocsr
    （prepare_full_markush_process 写入 *_image_merge_full_*.png / *_image_merge_part_*.png）
    """
    if not output_dir.exists():
        return []
    dirs = []
    for p in output_dir.iterdir():
        if not p.is_dir() or not p.name.startswith("md_merge_"):
            continue
        if p.name.endswith("_yolo_distinguish_full_markush_after_ocsr"):
            dirs.append(p)
    return sorted(dirs)


def _collect_doc_pages(merge_dir: Path, pattern_all_bboxes, pattern_merge_full):
    """从 merge_dir 下按文档收集页码（支持 all_bboxes 与 merge_full 两种文件名）。"""
    import re
    doc_pages = {}
    for doc_dir in merge_dir.iterdir():
        if not doc_dir.is_dir():
            continue
        doc_name = doc_dir.name
        pages = []
        for f in doc_dir.iterdir():
            if not f.is_file():
                continue
            m = pattern_all_bboxes.match(f.name) or pattern_merge_full.match(f.name)
            if m:
                pages.append(int(m.group(2)))
        if pages:
            doc_pages[doc_name] = sorted(set(pages))
    return doc_pages


def _doc_pages_from_stage_one(output_dir: Path):
    """从 stage_one.pkl 解析出 doc_pages（基于 bboxes_with_pred_smiless，与可点击框数据一致）。"""
    pkl_path = output_dir / "stage_one.pkl"
    if not pkl_path.is_file():
        return None
    try:
        import pickle
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        (
            page_image_pathss,
            _,
            _,
            _,
            _,
            _,
            _,
            bboxes_with_pred_smiless,
        ) = data
        doc_pages = {}
        for path_list, bboxes in zip(page_image_pathss, bboxes_with_pred_smiless):
            if not path_list:
                continue
            name = Path(path_list[0]).parent.name
            pages = sorted(set(b["page"] for b in bboxes))
            if pages:
                doc_pages[name] = pages
        return doc_pages if doc_pages else None
    except Exception:
        return None


@app.route("/api/detection_pages", methods=["GET"])
def detection_pages():
    """列出某 output_dir 下分子检测框：优先从 stage_one.pkl 解析（可点击模式），否则扫描 md_merge_*_yolo 目录。"""
    import re
    output_dir = request.args.get("output_dir")
    if not output_dir or not str(output_dir).strip():
        return jsonify({"error": "缺少 output_dir"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if not output_dir.exists():
        return jsonify({"doc_pages": {}, "message": "结果目录不存在，请先运行推理并确认输出目录正确"}), 200
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    doc_pages = _doc_pages_from_stage_one(output_dir)
    if doc_pages is not None:
        return jsonify({"output_dir": str(output_dir), "from_pkl": True, "doc_pages": doc_pages})

    merge_dirs = _get_merge_detection_dirs(output_dir)
    if not merge_dirs:
        return jsonify({"doc_pages": {}, "message": "未找到 stage_one.pkl 或分子检测结果目录 md_merge_*_yolo"})
    pattern_all_bboxes = re.compile(r"^(.+)_image_merge_all_bboxes_(\d+)\.png$")
    pattern_merge_full = re.compile(r"^(.+)_image_merge_full_(\d+)\.png$")
    doc_pages = {}
    used_merge_dir = None
    for merge_dir in merge_dirs:
        doc_pages = _collect_doc_pages(merge_dir, pattern_all_bboxes, pattern_merge_full)
        if doc_pages:
            used_merge_dir = merge_dir
            break
    if not used_merge_dir:
        return jsonify({"doc_pages": {}, "message": "未找到分子检测结果目录 md_merge_*_yolo 或其中无有效页图"})
    return jsonify({"output_dir": str(output_dir), "merge_dir": used_merge_dir.name, "from_pkl": False, "doc_pages": doc_pages})


@app.route("/api/page_image", methods=["GET"])
def page_image():
    """返回原始页图（无检测框），用于前端自行绘制可点击框。路径: page_images/<doc>/<doc>_image_<page>.png"""
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    page = request.args.get("page")
    if not output_dir or doc is None or doc == "" or page is None or page == "":
        return jsonify({"error": "缺少 output_dir、doc 或 page"}), 400
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = BIOMINER_ROOT / output_dir
    try:
        page_num = int(page)
    except ValueError:
        return jsonify({"error": "page 须为整数"}), 400
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    img_path = output_dir / "page_images" / doc / f"{doc}_image_{page_num}.png"
    if not img_path.is_file():
        return jsonify({"error": "该页原始图不存在"}), 404
    return send_file(img_path, mimetype="image/png", as_attachment=False)


@app.route("/api/markush_viz_page_image", methods=["GET"])
def markush_viz_page_image():
    """
    Full / Part Markush sheet 左侧页图：来自 md_merge_*_yolo_distinguish_full_markush_after_ocsr
    参数 kind=full -> {doc}_image_merge_full_{page}.png
         kind=part -> {doc}_image_merge_part_{page}.png
    """
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    page = request.args.get("page")
    kind = (request.args.get("kind") or "full").strip().lower()
    if not output_dir or doc is None or doc == "" or page is None or page == "":
        return jsonify({"error": "缺少 output_dir、doc 或 page"}), 400
    if kind not in ("full", "part"):
        return jsonify({"error": "kind 须为 full 或 part"}), 400

    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if not output_dir.exists():
        return jsonify({"error": "输出目录不存在"}), 404
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    try:
        page_num = int(page)
    except ValueError:
        return jsonify({"error": "page 须为整数"}), 400
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403

    suffix = "full" if kind == "full" else "part"
    filename = f"{doc}_image_merge_{suffix}_{page_num}.png"

    viz_dirs = _get_markush_after_ocsr_viz_dirs(output_dir)
    if not viz_dirs:
        return jsonify({"error": "未找到 md_merge_*_yolo_distinguish_full_markush_after_ocsr 目录"}), 404

    for root in viz_dirs:
        img_path = root / doc / filename
        if img_path.is_file():
            return send_file(img_path, mimetype="image/png", as_attachment=False)

    return jsonify({"error": f"该页可视化图不存在: {filename}"}), 404


@app.route("/api/detection_bboxes", methods=["GET"])
def detection_bboxes():
    """从 stage_one.pkl 的 bboxes_with_pred_smiless 返回指定 doc、page 的分子框列表，每项 {index, page, bbox, smiles}。"""
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    page = request.args.get("page")
    if not output_dir or doc is None or doc == "" or page is None or page == "":
        return jsonify({"error": "缺少 output_dir、doc 或 page"}), 400
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    try:
        page_num = int(page)
    except ValueError:
        return jsonify({"error": "page 须为整数"}), 400
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    try:
        page_image_pathss, bboxes_with_pred_smiless, doc_name_to_index = _get_stage_one_cached(output_dir)
    except FileNotFoundError:
        return jsonify({"error": "未找到 stage_one.pkl"}), 404
    except Exception as e:
        return jsonify({"error": f"读取 stage_one.pkl 失败: {e}"}), 500

    doc_index = doc_name_to_index.get(doc)
    if doc_index is None:
        return jsonify({"error": "未找到该文档"}), 404

    # 允许对某一页、某个 bbox 的 smiles 做增量覆盖（不修改/不备份 stage_one.pkl）
    overrides = {}
    override_path = output_dir / "user_overrides_detection_smiles" / doc / f"page_{page_num}.json"
    if override_path.is_file():
        try:
            with open(override_path, "r", encoding="utf-8") as f:
                obj = json.load(f)
            b = obj.get("bboxes", {})
            if isinstance(b, dict):
                overrides = b
        except Exception:
            overrides = {}

    # smiles -> mol_type 缓存，避免同一页/多次切页重复解析
    _mol_type_cache = {}

    def _determine_mol_type(smi):
        """
        与 BioMiner.commons.ocsr.determine_mol_type 保持一致：
        - SMILES 无效/不可解析 -> invalid
        - 含 '*' -> part
        - 其余 -> full
        """
        if smi in _mol_type_cache:
            return _mol_type_cache[smi]
        if smi is None:
            _mol_type_cache[smi] = "invalid"
            return "invalid"
        smi = str(smi)
        if not smi.strip():
            _mol_type_cache[smi] = "invalid"
            return "invalid"
        # 优先复用项目内实现（依赖 rdkit）
        try:
            import sys as _sys
            _root = str(BIOMINER_ROOT)
            if _root not in _sys.path:
                _sys.path.insert(0, _root)
            from BioMiner.commons.ocsr import determine_mol_type as _det
            t = _det(smi)
            _mol_type_cache[smi] = t
            return t
        except Exception:
            # fallback：尽量不因环境缺少 rdkit 导致接口失败
            t = "part" if "*" in smi else "full"
            _mol_type_cache[smi] = t
            return t

    # 先筛选该页，再并行 determine_mol_type（框很多时明显加速）
    page_items = []
    for b in bboxes_with_pred_smiless[doc_index]:
        if b.get("page") == page_num:
            idx = b.get("index")
            idx_key = str(idx) if idx is not None else None
            smi = b.get("smiles", "") or ""
            if idx_key and idx_key in overrides:
                o = overrides.get(idx_key)
                if o is not None:
                    smi = str(o)
            page_items.append((b, smi))

    mol_types = []
    try:
        from concurrent.futures import ThreadPoolExecutor
        # 仅在数量较多时启用并行，避免小页额外开销
        if len(page_items) >= 64:
            max_workers = min(32, (os.cpu_count() or 8))
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                mol_types = list(ex.map(lambda it: _determine_mol_type(it[1]), page_items))
        else:
            mol_types = [_determine_mol_type(smi) for _, smi in page_items]
    except Exception:
        mol_types = [_determine_mol_type(smi) for _, smi in page_items]

    page_bboxes = []
    for (b, smi), t in zip(page_items, mol_types):
        page_bboxes.append(
            {
                "index": b.get("index"),
                "page": b.get("page"),
                "bbox": list(b.get("bbox", [])),
                "smiles": smi,
                "mol_type": t,
            }
        )
    return jsonify({"output_dir": str(output_dir), "doc": doc, "page": page_num, "bboxes": page_bboxes})


@app.route("/api/detection_smiles_override_save", methods=["POST"])
def detection_smiles_override_save():
    """
    保存用户对 detection smiles 的增量覆盖（只覆盖某个 bbox 的 smiles）。
    - 不修改/不备份 stage_one.pkl
    - 覆盖文件：{output_dir}/user_overrides_detection_smiles/{doc}/page_{page}.json
    - 若覆盖文件已存在：重命名为 {stem}_older_version_{时间戳}{suffix}
    """
    payload = request.get_json(silent=True) or {}
    output_dir = payload.get("output_dir")
    doc = payload.get("doc")
    page = payload.get("page")
    bbox_index = payload.get("bbox_index")
    smiles = payload.get("smiles")

    if not output_dir or doc is None or doc == "" or page is None or page == "" or bbox_index is None or bbox_index == "" or smiles is None:
        return jsonify({"error": "缺少 output_dir、doc、page、bbox_index 或 smiles"}), 400

    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if "/" in str(doc) or "\\" in str(doc) or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    try:
        page_num = int(page)
        bbox_idx = int(bbox_index)
    except ValueError:
        return jsonify({"error": "page 与 bbox_index 须为整数"}), 400
    smiles = str(smiles).strip()
    if not smiles:
        return jsonify({"error": "smiles 为空"}), 400

    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403
    if not output_dir.exists():
        return jsonify({"error": "结果目录不存在"}), 404

    def _rel_to_root(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(BIOMINER_ROOT.resolve()))
        except ValueError:
            return str(p)

    override_dir = output_dir / "user_overrides_detection_smiles" / str(doc)
    override_dir.mkdir(parents=True, exist_ok=True)
    override_path = override_dir / f"page_{page_num}.json"

    existing = {}
    backup_path = None
    if override_path.is_file():
        try:
            with open(override_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = override_dir / f"{override_path.stem}_older_version_{ts}{override_path.suffix}"
        shutil.move(str(override_path), str(backup_path))

    bboxes = existing.get("bboxes", {})
    if not isinstance(bboxes, dict):
        bboxes = {}
    bboxes[str(bbox_idx)] = smiles

    data = {
        "doc": str(doc),
        "page": page_num,
        "bboxes": bboxes,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    try:
        with open(override_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        return jsonify({"error": f"写入失败: {e}"}), 500

    return jsonify(
        {
            "ok": True,
            "path": _rel_to_root(override_path),
            "backup": _rel_to_root(backup_path) if backup_path else None,
        }
    )


@app.route("/api/detection_image", methods=["GET"])
def detection_image():
    """返回指定文档、指定页的分子检测框可视化图。支持 all_bboxes 与 merge_full 两种文件名。"""
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    page = request.args.get("page")
    if not output_dir or doc is None or doc == "" or page is None or page == "":
        return jsonify({"error": "缺少 output_dir、doc 或 page"}), 400
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = BIOMINER_ROOT / output_dir
    merge_dirs = _get_merge_detection_dirs(output_dir)
    if not merge_dirs:
        return jsonify({"error": "未找到分子检测结果目录"}), 404
    try:
        page_num = int(page)
    except ValueError:
        return jsonify({"error": "page 须为整数"}), 400
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    candidates = [
        f"{doc}_image_merge_all_bboxes_{page_num}.png",
        f"{doc}_image_merge_full_{page_num}.png",
    ]
    for merge_dir in merge_dirs:
        doc_dir = merge_dir / doc
        if not doc_dir.is_dir():
            continue
        for name in candidates:
            img_path = doc_dir / name
            if img_path.is_file():
                return send_file(img_path, mimetype="image/png", as_attachment=False)
    return jsonify({"error": "该页检测图不存在"}), 404


@app.route("/api/detection_bbox_crop", methods=["GET"])
def detection_bbox_crop():
    """
    返回某个分子框的原图（裁剪图）。
    文件来自 visualize_all_box 保存的：
      md_merge_*_yolo/<doc>/<doc>_image_merge_bbox_<page>-<index>.png
    """
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    page = request.args.get("page")
    index = request.args.get("index")
    if not output_dir or doc is None or doc == "" or page is None or page == "" or index is None or index == "":
        return jsonify({"error": "缺少 output_dir、doc、page 或 index"}), 400

    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if not output_dir.exists():
        return jsonify({"error": "输出目录不存在"}), 404
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    try:
        page_num = int(page)
        bbox_index = int(index)
    except ValueError:
        return jsonify({"error": "page/index 须为整数"}), 400

    merge_dirs = _get_merge_detection_dirs(output_dir)
    if not merge_dirs:
        return jsonify({"error": "未找到分子检测结果目录"}), 404

    filename = f"{doc}_image_merge_bbox_{page_num}-{bbox_index}.png"
    for merge_dir in merge_dirs:
        doc_dir = merge_dir / doc
        if not doc_dir.is_dir():
            continue
        img_path = doc_dir / filename
        if img_path.is_file():
            return send_file(img_path, mimetype="image/png", as_attachment=False)

    return jsonify({"error": "该分子框原图不存在（可能尚未生成 md_merge_*_yolo，或 index/page 不匹配）"}), 404


@app.route("/api/draw_detection_bbox", methods=["POST"])
def draw_detection_bbox():
    """
    根据 stage_one.pkl 中的 merge_pdf_bboxess 与 page_image_pathss，
    调用 visualize_all_box 绘制分子检测框并保存到 md_merge_*_yolo 目录。
    若该目录下已有图则跳过；若无 stage_one.pkl 或无 merge 目录则尝试创建并绘图。
    """
    output_dir = request.json and request.json.get("output_dir")
    if not output_dir or not str(output_dir).strip():
        return jsonify({"error": "缺少 output_dir"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if not output_dir.exists():
        return jsonify({"error": "输出目录不存在"}), 400
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    stage_one_path = output_dir / "stage_one.pkl"
    if not stage_one_path.is_file():
        return jsonify({"error": "未找到 stage_one.pkl，请先运行推理完成分子检测阶段"}), 404

    try:
        import pickle
        import sys
        _root = str(BIOMINER_ROOT)
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from BioMiner.commons.ocsr import visualize_all_box
    except Exception as e:
        return jsonify({"error": f"导入绘图模块失败: {e}"}), 500

    try:
        with open(stage_one_path, "rb") as f:
            data = pickle.load(f)
        # 与 interface.py 738-740 一致：8 个元素
        (
            page_image_pathss,
            _mineru_texts,
            _mineru_table_body_bboxs,
            _mineru_complete_figure_table_bboxs,
            _pages_images_contain_tables_and_figures_pathss,
            merge_pdf_bboxess,
            _all_segmented_box_pathss,
            _bboxes_with_pred_smiless,
        ) = data
    except Exception as e:
        return jsonify({"error": f"读取 stage_one.pkl 失败: {e}"}), 500

    # 从 page_image_pathss 推断 page_image_dir 与文档名
    # 路径格式: .../page_images/<name>/<name>_image_<page>.png
    page_image_dir = output_dir / "page_images"
    if not page_image_dir.exists():
        return jsonify({"error": "未找到 page_images 目录"}), 404

    merge_dirs = _get_merge_detection_dirs(output_dir)
    if merge_dirs:
        merge_detection_path = merge_dirs[0]
    else:
        merge_detection_path = output_dir / "md_merge_moldetv2_yolo"
    merge_detection_path.mkdir(parents=True, exist_ok=True)

    names = []
    for path_list in page_image_pathss:
        if not path_list:
            names.append(None)
            continue
        first_path = path_list[0]
        # .../page_images/name/name_image_0.png -> name
        name = Path(first_path).parent.name
        names.append(name)

    for name, merge_pdf_bboxes in zip(names, merge_pdf_bboxess):
        if name is None or not merge_pdf_bboxes:
            continue
        try:
            visualize_all_box(
                name,
                merge_pdf_bboxes,
                str(page_image_dir),
                str(merge_detection_path),
            )
        except Exception as e:
            return jsonify({"error": f"绘制文档 {name} 时失败: {e}"}), 500

    # 返回与 detection_pages 一致的结构，便于前端直接刷新列表
    import re
    pattern_all_bboxes = re.compile(r"^(.+)_image_merge_all_bboxes_(\d+)\.png$")
    pattern_merge_full = re.compile(r"^(.+)_image_merge_full_(\d+)\.png$")
    doc_pages = _collect_doc_pages(merge_detection_path, pattern_all_bboxes, pattern_merge_full)
    return jsonify({
        "output_dir": str(output_dir),
        "merge_dir": merge_detection_path.name,
        "doc_pages": doc_pages,
        "message": "分子检测框已绘制",
    })


def _get_extraction_dirs(output_dir: Path):
    """
    在 output_dir 下查找 extraction_* 目录（分子指代/Markush/活性结果所在）。
    兼容两种传参方式：
    1）output_dir = 结果根目录（例如 tmp_output/demo_ui_2）
    2）output_dir = 某个具体的 extraction_* 目录（例如 tmp_output/demo_ui_2/extraction_local-biominer-instruct）
    """
    if not output_dir.exists():
        return []
    dirs = []
    # 情况 1：output_dir 本身就是 extraction_* 目录
    if output_dir.is_dir() and output_dir.name.startswith("extraction_"):
        dirs.append(output_dir)
    # 情况 2：output_dir 下的子目录中有 extraction_*
    for p in output_dir.iterdir():
        if p.is_dir() and p.name.startswith("extraction_"):
            dirs.append(p)
    # 去重
    unique_dirs = []
    seen = set()
    for d in dirs:
        key = str(d.resolve())
        if key in seen:
            continue
        seen.add(key)
        unique_dirs.append(d)
    return unique_dirs


def _get_markush_doc_pages_and_suffixes(output_dir: Path):
    """
    扫描 extraction_* 下各文档目录，收集有分子指代/Markush 结果的文档与页码，
    并解析 full_suffix / part_suffix。
    返回:
      doc_pages: {doc: [pages]} — full 与 part 页码并集（兼容旧前端）
      doc_pages_full: {doc: [pages]} — 仅有 Full 结果的页
      doc_pages_part: {doc: [pages]} — 仅有 Part 结果的页
      full_suffix_per_doc, part_suffix_per_doc
    """
    import re
    doc_pages = {}
    doc_pages_full = {}
    doc_pages_part = {}
    full_suffix_per_doc = {}
    part_suffix_per_doc = {}
    extraction_dirs = _get_extraction_dirs(output_dir)
    if not extraction_dirs:
        return doc_pages, doc_pages_full, doc_pages_part, full_suffix_per_doc, part_suffix_per_doc

    pattern_full_output = re.compile(r"^(.+)_structure_full_output_(.+)\.csv$")
    pattern_part_output = re.compile(r"^(.+)_structure_part_output_(.+)\.csv$")
    pattern_full_page = re.compile(r"^(.+)_image_merge_full_(\d+)_")
    pattern_part_page = re.compile(r"^(.+)_image_merge_part_(\d+)_")

    for ext_dir in extraction_dirs:
        for doc_dir in ext_dir.iterdir():
            if not doc_dir.is_dir():
                continue
            doc_name = doc_dir.name
            full_suffix = None
            part_suffix = None
            pages_full = set()
            pages_part = set()
            for f in doc_dir.iterdir():
                if not f.is_file():
                    continue
                name = f.name
                m = pattern_full_output.match(name)
                if m:
                    full_suffix = m.group(2)
                    continue
                m = pattern_part_output.match(name)
                if m:
                    part_suffix = m.group(2)
                    continue
                m = pattern_full_page.match(name)
                if m:
                    pages_full.add(int(m.group(2)))
                    continue
                m = pattern_part_page.match(name)
                if m:
                    pages_part.add(int(m.group(2)))
            if full_suffix is not None:
                full_suffix_per_doc[doc_name] = full_suffix
            if part_suffix is not None:
                part_suffix_per_doc[doc_name] = part_suffix
            if pages_full:
                doc_pages_full[doc_name] = sorted(pages_full)
            if pages_part:
                doc_pages_part[doc_name] = sorted(pages_part)
            all_pages = sorted(pages_full | pages_part)
            if all_pages:
                doc_pages[doc_name] = all_pages
    return doc_pages, doc_pages_full, doc_pages_part, full_suffix_per_doc, part_suffix_per_doc


def _get_markush_extraction_root(output_dir: Path):
    """返回第一个 extraction_* 目录的路径，用于读取 Markush 结果文件。"""
    extraction_dirs = _get_extraction_dirs(output_dir)
    return extraction_dirs[0] if extraction_dirs else None


@app.route("/api/markush_pages", methods=["GET"])
def markush_pages():
    """
    列出某 output_dir 下分子指代识别与 Markush 处理结果的文档与页码。
    结果来自 interface.opensource 流程中 extractor 保存的 per-page full/part 文件。
    """
    output_dir = request.args.get("output_dir")
    if not output_dir or not str(output_dir).strip():
        return jsonify({"error": "缺少 output_dir"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if not output_dir.exists():
        return jsonify({"doc_pages": {}, "docs": [], "message": "结果目录不存在"}), 200
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    doc_pages, doc_pages_full, doc_pages_part, full_suffix_per_doc, part_suffix_per_doc = _get_markush_doc_pages_and_suffixes(
        output_dir
    )
    ext_root = _get_markush_extraction_root(output_dir)
    return jsonify({
        "output_dir": str(output_dir),
        "extraction_root": str(ext_root) if ext_root else None,
        "docs": sorted(doc_pages.keys()),
        "doc_pages": doc_pages,
        "doc_pages_full": doc_pages_full,
        "doc_pages_part": doc_pages_part,
        "docs_full": sorted(doc_pages_full.keys()),
        "docs_part": sorted(doc_pages_part.keys()),
        "full_suffix_per_doc": full_suffix_per_doc,
        "part_suffix_per_doc": part_suffix_per_doc,
    })


@app.route("/api/markush_page_data", methods=["GET"])
def markush_page_data():
    """
    返回指定文档、指定页的分子指代/Markush 结果：该页的 full 与 part 分开展示。
    读取 extractor 保存的 {name}_image_merge_full_{page}_{suffix}.csv/.json 与
    {name}_image_merge_part_{page}_{suffix}.csv/.json 以及 coreference JSON。
    """
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    page = request.args.get("page")
    if not output_dir or doc is None or doc == "" or page is None or page == "":
        return jsonify({"error": "缺少 output_dir、doc 或 page"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    try:
        page_num = int(page)
    except ValueError:
        return jsonify({"error": "page 须为整数"}), 400
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    ext_root = _get_markush_extraction_root(output_dir)
    if not ext_root or not (ext_root / doc).is_dir():
        return jsonify({"error": "未找到该文档的分子指代结果目录"}), 404

    doc_dir = ext_root / doc
    _, _, _, full_suffix_per_doc, part_suffix_per_doc = _get_markush_doc_pages_and_suffixes(output_dir)
    full_suffix = full_suffix_per_doc.get(doc)
    part_suffix = part_suffix_per_doc.get(doc)
    base_full = f"{doc}_image_merge_full_{page_num}"
    base_part = f"{doc}_image_merge_part_{page_num}"

    result = {"doc": doc, "page": page_num, "full": None, "part": None}

    def read_section(base, suffix):
        if not suffix:
            return None
        csv_path = doc_dir / f"{base}_{suffix}.csv"
        json_path = doc_dir / f"{base}_{suffix}.json"
        coref_path = doc_dir / f"{base}_coreference_{suffix}.json"
        section = {"csv_rows": [], "json_data": None, "coreference": None}

        # 兜底：某些目录同时存在 *_clean_new 与非 clean_new 的输出，
        # 若 suffix 解析为 clean_new 但对应 per-page 文件不存在，则回退匹配同页其它同名文件。
        def _pick_fallback(path_obj, pattern):
            if path_obj.is_file():
                return path_obj
            candidates = [p for p in doc_dir.glob(pattern) if p.is_file()]
            if not candidates:
                return path_obj
            # 优先不带 clean_new 的文件，再按文件名排序取第一个
            candidates.sort(key=lambda p: ("clean_new" in p.name, p.name))
            return candidates[0]

        csv_path = _pick_fallback(csv_path, f"{base}_*.csv")
        # 避免把 coreference json 误当作数据 json
        json_path = _pick_fallback(json_path, f"{base}_*.json")
        if "coreference_" in json_path.name:
            raw_json_candidates = [p for p in doc_dir.glob(f"{base}_*.json") if "coreference_" not in p.name and p.is_file()]
            if raw_json_candidates:
                raw_json_candidates.sort(key=lambda p: ("clean_new" in p.name, p.name))
                json_path = raw_json_candidates[0]
        coref_path = _pick_fallback(coref_path, f"{base}_coreference_*.json")

        if csv_path.is_file():
            try:
                with open(csv_path, "r", encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)
                    section["csv_rows"] = list(reader)
            except Exception:
                pass
        if json_path.is_file():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    section["json_data"] = json.load(f)
            except Exception:
                pass
        if coref_path.is_file():
            try:
                with open(coref_path, "r", encoding="utf-8") as f:
                    section["coreference"] = json.load(f)
            except Exception:
                pass
        return section

    result["full"] = read_section(base_full, full_suffix)
    result["part"] = read_section(base_part, part_suffix)
    return jsonify(result)


@app.route("/api/markush_coreference_save", methods=["POST"])
def markush_coreference_save():
    """
    保存 Full 或 Part 的 coreference JSON（写入时使用 indent=4）。
    若目标文件已存在：先将其重命名为 {stem}_older_version_{时间戳}.json（同目录），再写入新内容到原文件名。
    """
    payload = request.get_json(silent=True) or {}
    output_dir = payload.get("output_dir")
    doc = payload.get("doc")
    page = payload.get("page")
    kind = str(payload.get("kind") or "full").lower()
    content = payload.get("content")
    if not output_dir or doc is None or doc == "" or page is None or page == "" or content is None:
        return jsonify({"error": "缺少 output_dir、doc、page 或 content"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    try:
        page_num = int(page)
    except ValueError:
        return jsonify({"error": "page 须为整数"}), 400
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    if isinstance(content, (dict, list)):
        parsed = content
    else:
        if not isinstance(content, str):
            return jsonify({"error": "content 须为 JSON 字符串或对象"}), 400
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"JSON 解析失败: {e}"}), 400

    ext_root = _get_markush_extraction_root(output_dir)
    if not ext_root or not (ext_root / doc).is_dir():
        return jsonify({"error": "未找到该文档的分子指代结果目录"}), 404

    doc_dir = ext_root / doc
    _, _, _, full_suffix_per_doc, part_suffix_per_doc = _get_markush_doc_pages_and_suffixes(output_dir)
    if kind == "part":
        suffix = part_suffix_per_doc.get(doc)
        base = f"{doc}_image_merge_part_{page_num}"
    else:
        suffix = full_suffix_per_doc.get(doc)
        base = f"{doc}_image_merge_full_{page_num}"
    if not suffix:
        return jsonify({"error": "未找到该文档的 suffix，无法确定 coreference 文件路径"}), 400

    coref_path = doc_dir / f"{base}_coreference_{suffix}.json"
    backup_path = None
    if coref_path.is_file():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = coref_path.parent / f"{coref_path.stem}_older_version_{ts}{coref_path.suffix}"
        shutil.move(str(coref_path), str(backup_path))

    try:
        with open(coref_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)
    except OSError as e:
        return jsonify({"error": f"写入失败: {e}"}), 500

    def _rel_to_root(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(BIOMINER_ROOT.resolve()))
        except ValueError:
            return str(p)

    return jsonify({
        "ok": True,
        "path": _rel_to_root(coref_path),
        "backup": _rel_to_root(backup_path) if backup_path else None,
    })


@app.route("/api/activity_text", methods=["GET"])
def activity_text():
    """
    汇总某 output_dir 下各文档的文本活性抽取结果。
    结果来自 extractor.save_bioactivity_results 写入的 {name}_text{suffix}_output.csv。
    """
    import re
    output_dir = request.args.get("output_dir")
    if not output_dir or not str(output_dir).strip():
        return jsonify({"error": "缺少 output_dir"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if not output_dir.exists():
        return jsonify({"rows": [], "message": "结果目录不存在"}), 200
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    extraction_dirs = _get_extraction_dirs(output_dir)
    pattern_text = re.compile(r"^(.+)_text(.+)_output\.csv$")
    rows = []
    doc_names_with_file = set()  # 有文本活性文件的文档名（即使 CSV 无数据行也记录，供前端下拉）
    for ext_dir in extraction_dirs:
        for doc_dir in ext_dir.iterdir():
            if not doc_dir.is_dir():
                continue
            doc_name = doc_dir.name
            for f in doc_dir.iterdir():
                if not f.is_file():
                    continue
                m = pattern_text.match(f.name)
                if not m:
                    continue
                doc_names_with_file.add(doc_name)
                suffix = m.group(2)
                try:
                    with open(f, "r", encoding="utf-8", newline="") as csv_f:
                        reader = csv.DictReader(csv_f)
                        for row_id, r in enumerate(reader):
                            r_with_doc = dict(r)
                            r_with_doc["doc"] = doc_name
                            r_with_doc["source_suffix"] = suffix
                            r_with_doc["row_id"] = row_id
                            rows.append(r_with_doc)
                except Exception:
                    continue
    return jsonify({
        "output_dir": str(output_dir),
        "rows": rows,
        "doc_names": sorted(doc_names_with_file),
    })


@app.route("/api/activity_image_pages", methods=["GET"])
def activity_image_pages():
    """
    列出某 output_dir 下基于图表抽取的活性结果的文档与“图表索引”（类似分页）。
    结果来自 extractor.save_image_bioactivity_result_individually 写入的
    {name}_image_ctimg_{idx}__{suffix}.csv。
    """
    import re
    output_dir = request.args.get("output_dir")
    if not output_dir or not str(output_dir).strip():
        return jsonify({"error": "缺少 output_dir"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    if not output_dir.exists():
        return jsonify({"docs": [], "doc_pages": {}, "message": "结果目录不存在"}), 200
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    extraction_dirs = _get_extraction_dirs(output_dir)
    # 文件名形如: 68_6r8r_image_ctimg_4__updated_v3_imgmuc.csv
    pattern_img = re.compile(r"^(.+)_image_ctimg_(\d+)__.+\.csv$")
    doc_pages = {}
    for ext_dir in extraction_dirs:
        for doc_dir in ext_dir.iterdir():
            if not doc_dir.is_dir():
                continue
            doc_name = doc_dir.name
            indices = set(doc_pages.get(doc_name, []))
            for f in doc_dir.iterdir():
                if not f.is_file():
                    continue
                # 跳过备份文件：避免 older_version 参与“存在性/分页”统计
                if "_older_version_" in f.name:
                    continue
                m = pattern_img.match(f.name)
                if not m:
                    continue
                try:
                    idx = int(m.group(2))
                except ValueError:
                    continue
                indices.add(idx)
            if indices:
                doc_pages[doc_name] = sorted(indices)
    return jsonify({"output_dir": str(output_dir), "docs": sorted(doc_pages.keys()), "doc_pages": doc_pages})


@app.route("/api/activity_doc_all_data", methods=["GET"])
def activity_doc_all_data():
    """
    返回某文档（doc）下所有图表活性抽取结果（合并所有图表索引）。

    读取 {name}_image_ctimg_{idx}__{suffix}.csv 文件，合并所有 rows，并附加列：
    - page_index：该条记录来自的图表索引（用于显示；与 idx 存在偏移）
    - source_idx：用于落盘的原始 idx
    - source_suffix：用于落盘的文件后缀 suffix
    - row_id：行号（从 0 开始，用于覆盖 value）
    """
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    if not output_dir or doc is None or doc == "":
        return jsonify({"error": "缺少 output_dir 或 doc"}), 400

    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()

    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    ext_root = _get_markush_extraction_root(output_dir)
    if not ext_root or not (ext_root / doc).is_dir():
        return jsonify({"doc": doc, "rows": []}), 200

    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403

    doc_dir = ext_root / doc
    import re
    pattern_img = re.compile(rf"^{re.escape(doc)}_image_ctimg_(\d+)__(.+)\.csv$")

    items = []
    for f in doc_dir.iterdir():
        if not f.is_file():
            continue
        # 跳过备份文件：避免 older_version 行也被合并展示
        if "_older_version_" in f.name:
            continue
        m = pattern_img.match(f.name)
        if not m:
            continue
        try:
            idx = int(m.group(1))
        except ValueError:
            continue
        suffix = m.group(2)
        items.append((idx, suffix, f))

    items.sort(key=lambda t: t[0])

    rows = []
    for idx, suffix, csv_path in items:
        try:
            with open(csv_path, "r", encoding="utf-8", newline="") as csv_f:
                reader = csv.DictReader(csv_f)
                for row_id, r in enumerate(reader):
                    r_with = dict(r)
                    # 前端显示映射：ctimg_{idx} 对应 PDF viewer 的“页码”（通常多一个偏移）。
                    # 当前实现：显示为 idx + 1（你看到第几页与当前映射一致为准）。
                    r_with["page_index"] = idx + 1
                    # 用于保存的元信息
                    r_with["source_idx"] = idx
                    r_with["source_suffix"] = suffix
                    r_with["row_id"] = row_id
                    rows.append(r_with)
        except Exception:
            continue

    return jsonify({"doc": doc, "rows": rows})


def _backup_and_write_csv(csv_path: Path, rows: list[dict], fieldnames: list[str]):
    """备份已有 csv 文件并写回（indent/encoding 保持原样即可）。"""
    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = csv_path.parent / f"{csv_path.stem}_older_version_{ts}{csv_path.suffix}"
    shutil.move(str(csv_path), str(backup_path))
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return backup_path


@app.route("/api/activity_text_overrides_save", methods=["POST"])
def activity_text_overrides_save():
    """
    保存文本活性抽取结果：将编辑的指定列覆盖到小文件。
    不修改 stage_one.pkl。所有写入内容按字符串处理。
    """
    payload = request.get_json(silent=True) or {}
    output_dir = payload.get("output_dir")
    edits = payload.get("edits") or []
    if not output_dir or not isinstance(edits, list):
        return jsonify({"error": "缺少 output_dir 或 edits"}), 400

    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    extraction_dirs = _get_extraction_dirs(output_dir)

    def _find_text_csv(doc: str, suffix: str) -> Path | None:
        for ext_dir in extraction_dirs:
            doc_dir = ext_dir / doc
            if not doc_dir.is_dir():
                continue
            candidate = doc_dir / f"{doc}_text{suffix}_output.csv"
            if candidate.is_file():
                return candidate
        return None

    # group edits by csv_path
    grouped = {}
    for e in edits:
        try:
            doc = str(e.get("doc") or "").strip()
            suffix = str(e.get("source_suffix") or "").strip()
            row_id = int(e.get("row_id"))
            column = str(e.get("column") or e.get("col") or "value").strip()
            value = e.get("value")
        except Exception:
            continue
        if not doc or not suffix or not column:
            continue
        csv_path = _find_text_csv(doc, suffix)
        if not csv_path:
            continue
        key = str(csv_path)
        grouped.setdefault(key, {"csv_path": csv_path, "edit_by_row_col": {}})
        grouped[key]["edit_by_row_col"].setdefault(row_id, {})[column] = "" if value is None else str(value)

    if not grouped:
        return jsonify({"error": "未找到可保存的编辑目标"}), 400

    backups = []
    for g in grouped.values():
        csv_path = g["csv_path"]
        edit_by_row_col = g["edit_by_row_col"]
        try:
            with open(csv_path, "r", encoding="utf-8", newline="") as csv_f:
                reader = csv.DictReader(csv_f)
                fieldnames = reader.fieldnames or []
                rows = list(reader)
        except Exception as ex:
            return jsonify({"error": f"读取失败: {ex}"}), 500

        fieldname_set = set(fieldnames)
        for rid, col_map in edit_by_row_col.items():
            if 0 <= rid < len(rows):
                for col, v in col_map.items():
                    # 只写回原 CSV 已存在的列，避免写入无效字段
                    if col in fieldname_set:
                        rows[rid][col] = v

        # 写回需要备份
        try:
            backup_path = _backup_and_write_csv(csv_path, rows, fieldnames)
            backups.append(str(backup_path))
        except Exception as ex:
            return jsonify({"error": f"写入失败: {ex}"}), 500

    return jsonify({"ok": True, "backups": backups})


@app.route("/api/activity_image_overrides_save", methods=["POST"])
def activity_image_overrides_save():
    """
    保存图表活性抽取结果：将编辑的指定列覆盖到小文件。
    根据 source_idx / source_suffix / row_id 定位文件与行。
    """
    payload = request.get_json(silent=True) or {}
    output_dir = payload.get("output_dir")
    edits = payload.get("edits") or []
    if not output_dir or not isinstance(edits, list):
        return jsonify({"error": "缺少 output_dir 或 edits"}), 400

    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    try:
        output_dir.resolve().relative_to(BIOMINER_ROOT.resolve())
    except ValueError:
        return jsonify({"error": "结果目录必须在项目根目录下"}), 403

    ext_root = _get_markush_extraction_root(output_dir)
    if not ext_root:
        return jsonify({"error": "未找到分子指代结果目录"}), 404

    grouped = {}
    for e in edits:
        try:
            doc = str(e.get("doc") or "").strip()
            src_idx = int(e.get("source_idx"))
            suffix = str(e.get("source_suffix") or "").strip()
            row_id = int(e.get("row_id"))
            column = str(e.get("column") or e.get("col") or "value").strip()
            value = e.get("value")
        except Exception:
            continue
        if not doc or not suffix or not column:
            continue
        doc_dir = ext_root / doc
        if not doc_dir.is_dir():
            continue
        csv_path = doc_dir / f"{doc}_image_ctimg_{src_idx}__{suffix}.csv"
        if not csv_path.is_file():
            continue
        key = str(csv_path)
        grouped.setdefault(key, {"csv_path": csv_path, "edit_by_row_col": {}})
        grouped[key]["edit_by_row_col"].setdefault(row_id, {})[column] = "" if value is None else str(value)

    if not grouped:
        return jsonify({"error": "未找到可保存的编辑目标"}), 400

    backups = []
    for g in grouped.values():
        csv_path = g["csv_path"]
        edit_by_row_col = g["edit_by_row_col"]
        try:
            with open(csv_path, "r", encoding="utf-8", newline="") as csv_f:
                reader = csv.DictReader(csv_f)
                fieldnames = reader.fieldnames or []
                rows = list(reader)
        except Exception as ex:
            return jsonify({"error": f"读取失败: {ex}"}), 500

        fieldname_set = set(fieldnames)
        for rid, col_map in edit_by_row_col.items():
            if 0 <= rid < len(rows):
                for col, v in col_map.items():
                    if col in fieldname_set:
                        rows[rid][col] = v

        try:
            backup_path = _backup_and_write_csv(csv_path, rows, fieldnames)
            backups.append(str(backup_path))
        except Exception as ex:
            return jsonify({"error": f"写入失败: {ex}"}), 500

    return jsonify({"ok": True, "backups": backups})


@app.route("/api/activity_image_page_data", methods=["GET"])
def activity_image_page_data():
    """
    返回指定文档、指定图表索引的活性结果（来自图表），用于类似分子结果的分页展示。
    读取 {name}_image_ctimg_{idx}__{suffix}.csv/.json/.txt。
    """
    import re
    output_dir = request.args.get("output_dir")
    doc = request.args.get("doc")
    page = request.args.get("page")
    if not output_dir or doc is None or doc == "" or page is None or page == "":
        return jsonify({"error": "缺少 output_dir、doc 或 page"}), 400
    output_dir = Path(str(output_dir).strip())
    if not output_dir.is_absolute():
        output_dir = (BIOMINER_ROOT / output_dir).resolve()
    try:
        idx = int(page)
    except ValueError:
        return jsonify({"error": "page 须为整数"}), 400
    if "/" in doc or "\\" in doc or doc in (".", ".."):
        return jsonify({"error": "非法 doc"}), 403

    ext_root = _get_markush_extraction_root(output_dir)
    if not ext_root or not (ext_root / doc).is_dir():
        return jsonify({"error": "未找到该文档的活性结果目录"}), 404
    doc_dir = ext_root / doc

    # 与 activity_image_pages 中的 pattern 一致，只是 doc 与 idx 已知
    pattern_img = re.compile(rf"^{re.escape(doc)}_image_ctimg_{idx}__(.+)\.csv$")
    target_csv = None
    suffix = None
    for f in doc_dir.iterdir():
        if not f.is_file():
            continue
        # 跳过备份文件：确保加载最新的原始 CSV
        if "_older_version_" in f.name:
            continue
        m = pattern_img.match(f.name)
        if m:
            target_csv = f
            suffix = m.group(1)
            break
    if not target_csv:
        return jsonify({"doc": doc, "page": idx, "rows": [], "json_data": None, "api_output": None})

    base = target_csv.name[:-4]  # remove .csv
    json_path = doc_dir / f"{base}.json"
    txt_path = doc_dir / f"{base}.txt"

    rows = []
    try:
        with open(target_csv, "r", encoding="utf-8", newline="") as csv_f:
            reader = csv.DictReader(csv_f)
            rows = list(reader)
    except Exception:
        rows = []

    json_data = None
    if json_path.is_file():
        try:
            with open(json_path, "r", encoding="utf-8") as jf:
                json_data = json.load(jf)
        except Exception:
            json_data = None

    api_output = None
    if txt_path.is_file():
        try:
            with open(txt_path, "r", encoding="utf-8") as tf:
                api_output = tf.read()
        except Exception:
            api_output = None

    return jsonify({"doc": doc, "page": idx, "rows": rows, "json_data": json_data, "api_output": api_output})


@app.route("/api/example_pdf", methods=["GET"])
def example_pdf():
    """返回示例 PDF 路径（若存在）。"""
    example_dir = BIOMINER_ROOT / "example" / "pdfs"
    if not example_dir.exists():
        return jsonify({"path": None, "message": "example/pdfs 不存在"})
    pdfs = list(example_dir.glob("*.pdf"))
    if not pdfs:
        return jsonify({"path": None, "message": "无示例 PDF"})
    return jsonify({"path": str(pdfs[0].relative_to(BIOMINER_ROOT))})


if __name__ == "__main__":
    print("BioMiner 项目根目录:", BIOMINER_ROOT)
    print("默认配置文件:", CONFIG_PATH_DEFAULT)
    print("本地访问: http://127.0.0.1:5000")
    print("外网访问: http://<本机IP>:5000 （需开放防火墙 5000 端口）")
    app.run(host="0.0.0.0", port=5000, debug=False)
