# BioMiner 交互式 UI

基于 BioMiner README 中的调用方式，提供 Web 界面：选择/上传 PDF、配置输出与 MLLM、运行推理、查看蛋白-配体-生物活性结果。

## 前置条件

- 已按 [BioMiner README](../README.md) 完成环境与模型安装。
- 已启动所需服务（在项目根目录下）：
  ```bash
  export PYTHONPATH=./
  conda activate BioMiner
  python scripts/mineru_server.py   # tmux 窗口 0
  python scripts/moldet_server.py  # tmux 窗口 1
  python scripts/ocsr_server.py    # tmux 窗口 2
  # 使用 BioMiner-Instruct 时还需：
  conda activate vllm_py310
  bash scripts/run_local_vllm_server_biominer_instruct.bash  # tmux 窗口 3
  ```

## 安装 UI 依赖

在 **BioMiner 项目根目录** 或本目录下执行：

```bash
pip install -r BioMiner_UI/requirements.txt
```

## 启动 UI

在 **BioMiner 项目根目录** 下执行（确保能正确找到 `example_open_source.py` 和 `BioMiner` 包）：

```bash
cd /path/to/BioMiner   # 项目根目录
export PYTHONPATH=./   # 可选，若已全局设置可省略
python BioMiner_UI/backend/app.py
```

浏览器访问：**http://127.0.0.1:5000**

## 使用说明

1. **输入 PDF 与预览**  
   - 填写服务端已有 PDF 路径（相对项目根，如 `example/pdfs/68_6r8r.pdf`），或点击「使用示例」自动填示例路径。  
   - 或通过「上传 PDF 文件」选择本地 PDF。  
   - 右侧为 **PDF 预览**：点击「预览 PDF」后在此查看 PDF 内容。

2. **输出与配置**  
   - **输出目录**：推理结果保存路径（相对项目根，如 `tmp_output/demo_ui`）。  
   - **配置文件路径**：默认 `BioMiner/config/default_open_source.yaml`。  
   - 使用闭源 MLLM 时，展开「API 配置」填写 `base_url`、`api_key`、`text_mllm_type`、`vision_mllm_type`，可「从配置文件加载」/「保存到配置文件」。

3. **运行推理**  
   - 点击「运行 BioMiner」，会提交任务并轮询状态与日志。  
   - 推理由项目根目录下的 `example_open_source.py` 执行，需已启动上述各 server。

4. **结果预览**  
   - 结果目录与「输出目录」一致，点击「加载结果」可拉取该目录下的合并 CSV（如 `*merged*output_unique.csv`），在页面上以表格形式展示 **protein / ligand / type / value / unit** 等列。

5. **分子可视化（Ketcher）**  
   - 集成自 `moldemo` 的 Ketcher 分子编辑器（无 Gradio 依赖）。在结果表中点击某一行的「查看分子」，可将该行 ligand 传入 Ketcher 绘制（若 ligand 为 SMILES）；也可在下方输入框中输入 SMILES 后点击「绘制」进行编辑与查看。

## 目录结构

```
BioMiner_UI/
├── backend/
│   └── app.py          # Flask 后端：提交任务、配置读写、结果列表与下载
├── frontend/
│   ├── index.html
│   └── static/
│       ├── style.css
│       ├── app.js
│       ├── ketcher_bridge.js    # Ketcher 与页面通信（无 Gradio）
│       └── ketcher-standalone-3.7.0/   # Ketcher 分子编辑器静态资源（来自 moldemo）
├── uploads/             # 上传的 PDF（运行后自动创建）
├── requirements.txt
└── README.md
```

## API 简述

- `GET /` — 前端页面  
- `GET /api/config?path=...` — 读取配置（base_url、api_key、text/vision_mllm_type）  
- `POST /api/config` — 保存上述配置到 YAML  
- `POST /api/run` — 提交推理（form: pdf 路径或 file 上传、output_dir、config_path）  
- `GET /api/job/<job_id>` — 查询任务状态与日志  
- `GET /api/results?output_dir=...` — 获取结果目录下的主 CSV 数据与文件列表  
- `GET /api/results/download?output_dir=...&file=...` — 下载结果文件  
- `GET /api/example_pdf` — 获取示例 PDF 路径（若存在）
