# BioMiner Interactive UI

This UI provides a web interface for running BioMiner following the invocation pattern in the main BioMiner README: select/upload a PDF, configure output and MLLM settings, run inference, and view the extracted protein–ligand–bioactivity results.

## Prerequisites

- Complete the environment and model setup as described in the [BioMiner README](../README.md).
- Start the required services (from the project root directory):
  ```bash
  export PYTHONPATH=./
  conda activate BioMiner
  python scripts/mineru_server.py   # tmux window 0
  python scripts/moldet_server.py  # tmux window 1
  python scripts/ocsr_server.py    # tmux window 2
  # If you use BioMiner-Instruct, also run:
  conda activate vllm_py310
  bash scripts/run_local_vllm_server_biominer_instruct.bash  # tmux window 3
  ```

## Install UI dependencies

Run from the **BioMiner project root** or from this directory:

```bash
pip install -r BioMiner_UI/requirements.txt
```

## Start the UI

Run from the **BioMiner project root** (so `example_open_source.py` and the `BioMiner` package can be resolved correctly):

```bash
cd /path/to/BioMiner   # project root
export PYTHONPATH=./   # optional; omit if already set globally
python BioMiner_UI/backend/app.py
```

Open in your browser: **http://127.0.0.1:5000**

## Usage

1. **PDF input and preview**  
   - Enter an existing PDF path on the server (relative to the project root, e.g. `example/pdfs/68_6r8r.pdf`), or click "Use example" to autofill a sample path.  
   - Or choose a local PDF via "Upload PDF".  
   - On the right is the **PDF preview**: click "Preview PDF" to render and view the PDF.

2. **Output and configuration**  
   - **Output directory**: where inference results will be saved (relative to the project root, e.g. `tmp_output/demo_ui`).  
   - **Config file path**: default is `BioMiner/config/default_open_source.yaml`.  
   - If using a closed-source MLLM API, expand "API settings" and fill in `base_url`, `api_key`, `text_mllm_type`, `vision_mllm_type`. You can "Load from config" / "Save to config".

3. **Run inference**  
   - Click "Run BioMiner" to submit a job; the UI will poll job status and logs.  
   - Inference is executed via `example_open_source.py` in the project root, and requires the servers above to be running.

4. **Preview results**  
   - The results directory is the same as the "Output directory". Click "Load results" to fetch a merged CSV from that directory (e.g. `*merged*output_unique.csv`) and display it as a table with columns such as **protein / ligand / type / value / unit**.

5. **Molecule visualization (Ketcher)**  
   - Includes the Ketcher molecule editor integrated from `moldemo` (no Gradio dependency). In the results table, click "View molecule" on a row to pass the row's ligand into Ketcher (if the ligand is SMILES). You can also paste a SMILES string into the input box below and click "Draw" to edit and view it.

## Directory structure

```
BioMiner_UI/
├── backend/
│   └── app.py          # Flask backend: job submission, config I/O, results listing/download
├── frontend/
│   ├── index.html
│   └── static/
│       ├── style.css
│       ├── app.js
│       ├── ketcher_bridge.js    # Ketcher <-> page bridge (no Gradio)
│       └── ketcher-standalone-3.7.0/   # Ketcher static assets (from moldemo)
├── uploads/             # Uploaded PDFs (auto-created at runtime)
├── requirements.txt
└── README.md
```

## API overview

- `GET /` — Frontend page  
- `GET /api/config?path=...` — Read config (`base_url`, `api_key`, `text_mllm_type`, `vision_mllm_type`)  
- `POST /api/config` — Save the above settings back to YAML  
- `POST /api/run` — Submit an inference job (form: PDF path or uploaded file, `output_dir`, `config_path`)  
- `GET /api/job/<job_id>` — Query job status and logs  
- `GET /api/results?output_dir=...` — Fetch the primary merged CSV data and file list from the results directory  
- `GET /api/results/download?output_dir=...&file=...` — Download a result file  
- `GET /api/example_pdf` — Get the example PDF path (if available)
