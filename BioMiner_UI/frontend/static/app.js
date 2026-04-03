(function () {
  const $ = (id) => document.getElementById(id);
  const tx = (k, v) =>
    (window.BioMinerI18n && window.BioMinerI18n.t(k, v)) || k;

  const pdfPath = $("pdfPath");
  const pdfFile = $("pdfFile");
  const pdfFileNameDisplay = $("pdfFileNameDisplay");
  const btnPdfFilePick = $("btnPdfFilePick");
  const outputDir = $("outputDir");
  const configPath = $("configPath");
  const baseUrl = $("baseUrl");
  const apiKey = $("apiKey");
  const textMllmType = $("textMllmType");
  const visionMllmType = $("visionMllmType");
  const btnExamplePdf = $("btnExamplePdf");
  const btnLoadConfig = $("btnLoadConfig");
  const btnSaveConfig = $("btnSaveConfig");
  const btnRun = $("btnRun");
  const jobInfo = $("jobInfo");
  const jobIdEl = $("jobId");
  const jobStatusEl = $("jobStatus");
  const btnRefreshJob = $("btnRefreshJob");
  const logOutput = $("logOutput");
  const resultsOutputDir = $("resultsOutputDir");
  const btnLoadResults = $("btnLoadResults");
  const resultsSummary = $("resultsSummary");
  const resultsDocFilterRow = $("resultsDocFilterRow");
  const resultsDocFilter = $("resultsDocFilter");
  const resultsThead = $("resultsThead");
  const resultsTbody = $("resultsTbody");
  const resultsPaginationRow = $("resultsPaginationRow");
  const resultsPaginationInfo = $("resultsPaginationInfo");
  const btnResultsFirstPage = $("btnResultsFirstPage");
  const btnResultsPrevPage = $("btnResultsPrevPage");
  const btnResultsNextPage = $("btnResultsNextPage");
  const btnResultsLastPage = $("btnResultsLastPage");
  const givenStructureOutputDir = $("givenStructureOutputDir");
  const btnLoadGivenStructure = $("btnLoadGivenStructure");
  const givenStructureSummary = $("givenStructureSummary");
  const givenStructureDocFilterRow = $("givenStructureDocFilterRow");
  const givenStructureDocFilter = $("givenStructureDocFilter");
  const givenStructureThead = $("givenStructureThead");
  const givenStructureTbody = $("givenStructureTbody");
  const givenStructurePaginationRow = $("givenStructurePaginationRow");
  const givenStructurePaginationInfo = $("givenStructurePaginationInfo");
  const btnGivenStructureFirstPage = $("btnGivenStructureFirstPage");
  const btnGivenStructurePrevPage = $("btnGivenStructurePrevPage");
  const btnGivenStructureNextPage = $("btnGivenStructureNextPage");
  const btnGivenStructureLastPage = $("btnGivenStructureLastPage");
  const givenStructureImageResultRow = $("givenStructureImageResultRow");
  const givenStructureDocPdfWrap = $("givenStructureDocPdfWrap");
  const givenStructureDocPdfIframe = $("givenStructureDocPdfIframe");
  const givenStructureDocPdfPlaceholder = $("givenStructureDocPdfPlaceholder");
  const givenStructureGivenSmilesWrap = $("givenStructureGivenSmilesWrap");
  const givenStructureGivenSmilesImg = $("givenStructureGivenSmilesImg");
  const givenStructureGivenSmilesErr = $("givenStructureGivenSmilesErr");
  const givenStructurePdbIdLine = $("givenStructurePdbIdLine");
  const givenStructurePdbIdValue = $("givenStructurePdbIdValue");
  const givenStructurePdbIdLink = $("givenStructurePdbIdLink");
  const givenStructurePdbTitleLine = $("givenStructurePdbTitleLine");
  const givenStructurePdbTitleValue = $("givenStructurePdbTitleValue");
  const btnPreviewPdf = $("btnPreviewPdf");
  const pdfPreviewPlaceholder = $("pdfPreviewPlaceholder");
  const pdfPreviewIframe = $("pdfPreviewIframe");
  const detectionOutputDir = $("detectionOutputDir");
  const btnShowMolBbox = $("btnShowMolBbox");
  const detectionDocPageRow = $("detectionDocPageRow");
  const detectionDocSelect = $("detectionDocSelect");
  const detectionPageSelect = $("detectionPageSelect");
  const detectionImageWrap = $("detectionImageWrap");
  const detectionCanvas = $("detectionCanvas");
  const detectionZoomOut = $("detectionZoomOut");
  const detectionZoomIn = $("detectionZoomIn");
  const detectionZoomReset = $("detectionZoomReset");
  const detectionZoomFit = $("detectionZoomFit");
  const detectionZoomLabel = $("detectionZoomLabel");
  const detectionBboxListWrap = $("detectionBboxListWrap");
  const detectionBboxList = $("detectionBboxList");
  const detectionKetcherCol = $("detectionKetcherCol");
  const detectionBackToBboxList = $("detectionBackToBboxList");
  const detectionPlaceholder = $("detectionPlaceholder");
  const detectionBboxCropWrap = $("detectionBboxCropWrap");
  const detectionBboxCropImg = $("detectionBboxCropImg");
  const btnSaveSmiles = $("btnSaveSmiles");
  const smilesInput = $("smiles-input");
  const markushOutputDir = $("markushOutputDir");
  const btnLoadMarkush = $("btnLoadMarkush");
  const markushDocPageRow = $("markushDocPageRow");
  const markushDocSelect = $("markushDocSelect");
  const markushPageSelect = $("markushPageSelect");
  const markushContent = $("markushContent");
  const markushPlaceholder = $("markushPlaceholder");
  const markushFullDetails = $("markushFullDetails");
  const markushFullCoref = $("markushFullCoref");
  const btnSaveMarkushFullCoref = $("btnSaveMarkushFullCoref");
  const markushFullCorefHint = $("markushFullCorefHint");
  const markushPartDetails = $("markushPartDetails");
  const markushPartCoref = $("markushPartCoref");
  const btnSaveMarkushPartCoref = $("btnSaveMarkushPartCoref");
  const markushPartCorefHint = $("markushPartCorefHint");
  const markushPartOutputDir = $("markushPartOutputDir");
  const btnLoadMarkushPart = $("btnLoadMarkushPart");
  const markushPartDocPageRow = $("markushPartDocPageRow");
  const markushPartDocSelect = $("markushPartDocSelect");
  const markushPartPageSelect = $("markushPartPageSelect");
  const markushPartContent = $("markushPartContent");
  const markushPartPlaceholder = $("markushPartPlaceholder");
  const activityOutputDir = $("activityOutputDir");
  const btnLoadActivityText = $("btnLoadActivityText");
  const activitySummary = $("activitySummary");
  const activityDocFilterRow = $("activityDocFilterRow");
  const activityDocFilter = $("activityDocFilter");
  const activityThead = $("activityThead");
  const activityTbody = $("activityTbody");
  const activityTextDocPdfWrap = $("activityTextDocPdfWrap");
  const activityTextDocPdfIframe = $("activityTextDocPdfIframe");
  const activityTextDocPdfPlaceholder = $("activityTextDocPdfPlaceholder");
  const activityImageOutputDir = $("activityImageOutputDir");
  const btnLoadActivityImage = $("btnLoadActivityImage");
  const activityDocPageRow = $("activityDocPageRow");
  const activityDocSelect = $("activityDocSelect");
  const activityPageSelect = $("activityPageSelect");
  const activityImageThead = $("activityImageThead");
  const activityImageTbody = $("activityImageTbody");
  const activityImagePlaceholder = $("activityImagePlaceholder");
  const btnSaveActivityTextEdits = $("btnSaveActivityTextEdits");
  const btnSaveActivityImageEdits = $("btnSaveActivityImageEdits");
  const activityPaginationRow = $("activityPaginationRow");
  const activityPaginationInfo = $("activityPaginationInfo");
  const btnActivityFirstPage = $("btnActivityFirstPage");
  const btnActivityPrevPage = $("btnActivityPrevPage");
  const btnActivityNextPage = $("btnActivityNextPage");
  const btnActivityLastPage = $("btnActivityLastPage");
  const markushPageImageWrap = $("markushPageImageWrap");
  const markushPageImage = $("markushPageImage");
  const markushImageResultRow = $("markushImageResultRow");
  const markushPartPageImageWrap = $("markushPartPageImageWrap");
  const markushPartPageImage = $("markushPartPageImage");
  const markushPartImageResultRow = $("markushPartImageResultRow");
  const activityImagePageImageWrap = $("activityImagePageImageWrap");
  const activityImagePageImage = $("activityImagePageImage");
  const activityImageImageResultRow = $("activityImageImageResultRow");
  const activityImageDocPdfIframe = $("activityImageDocPdfIframe");
  const activityImageDocPdfPlaceholder = $("activityImageDocPdfPlaceholder");
  const activityImageZoomOut = $("activityImageZoomOut");
  const activityImageZoomIn = $("activityImageZoomIn");
  const activityImageZoomReset = $("activityImageZoomReset");
  const activityImageZoomFit = $("activityImageZoomFit");
  const activityImageZoomLabel = $("activityImageZoomLabel");
  const markushZoomOut = $("markushZoomOut");
  const markushZoomIn = $("markushZoomIn");
  const markushZoomReset = $("markushZoomReset");
  const markushZoomFit = $("markushZoomFit");
  const markushZoomLabel = $("markushZoomLabel");
  const markushPartZoomOut = $("markushPartZoomOut");
  const markushPartZoomIn = $("markushPartZoomIn");
  const markushPartZoomReset = $("markushPartZoomReset");
  const markushPartZoomFit = $("markushPartZoomFit");
  const markushPartZoomLabel = $("markushPartZoomLabel");

  let lastPdfBlobUrl = null;
  let lastDetectionDocPages = null;
  let lastDetectionOutputDir = null;
  let currentDetectionBboxes = [];
  let currentDetectionDoc = null;
  let currentDetectionPage = null;
  let lastDetectionImageBlobUrl = null;
  let currentDetectionImage = null;
  let selectedBboxIndex = null;
  let currentDetectionCanvasW = 0;
  let currentDetectionCanvasH = 0;
  let detectionZoom = 1;
  let detectionZoomMode = "fit"; // manual | fit（默认适配宽度）
  let markushZoom = 1;
  let markushZoomMode = "fit";
  let markushPartZoom = 1;
  let markushPartZoomMode = "fit";
  let activityImageZoom = 1;
  let activityImageZoomMode = "fit";
  let lastMarkushDocPages = null;
  let lastMarkushOutputDir = null;
  let lastMarkushPartDocPages = null;
  let lastMarkushPartOutputDir = null;
  let lastActivityTextRows = null;
  let lastActivityTextOutputDir = null;
  const ACTIVITY_TEXT_PAGE_SIZE = 15;
  let activityTextCurrentPage = 1;
  let activityTextEdits = new Map(); // key -> newValue
  let lastActivityImageDocPages = null;
  let lastActivityImageOutputDir = null;
  let activityImageEdits = new Map(); // key -> newValue
  let lastResultsRows = null;
  const RESULTS_PAGE_SIZE = 10;
  let resultsCurrentPage = 1;
  let lastGivenStructureRows = null;
  let givenStructureCurrentPage = 1;
  let lastGivenStructureKetcherRow = null;
  let lastGivenSmilesByDoc = null;
  let lastPdbIdByDoc = null;
  let lastPdbTitleByDoc = null;
  const GIVEN_STRUCTURE_PAGE_SIZE = RESULTS_PAGE_SIZE;

  (function initSheets() {
    const tabs = document.querySelectorAll(".sheet-tab");
    const panels = document.querySelectorAll(".sheet-panel");
    /** 每个结果类 sheet 仅在首次进入时自动加载，再次进入保留界面状态 */
    const sheetAutoLoadedOnce = new Set();

    function autoLoadSheetData(sheetId) {
      if (sheetAutoLoadedOnce.has(sheetId)) return;
      const dir = (outputDir && outputDir.value ? String(outputDir.value).trim() : "");
      if (!dir) return;

      let didTriggerLoad = false;
      if (sheetId === "detection") {
        if (detectionOutputDir) detectionOutputDir.value = dir;
        if (btnShowMolBbox) btnShowMolBbox.click();
        didTriggerLoad = true;
      } else if (sheetId === "markushFull") {
        if (markushOutputDir) markushOutputDir.value = dir;
        if (btnLoadMarkush) btnLoadMarkush.click();
        didTriggerLoad = true;
      } else if (sheetId === "markushPart") {
        if (markushPartOutputDir) markushPartOutputDir.value = dir;
        if (btnLoadMarkushPart) btnLoadMarkushPart.click();
        didTriggerLoad = true;
      } else if (sheetId === "activity") {
        if (activityOutputDir) activityOutputDir.value = dir;
        if (btnLoadActivityText) btnLoadActivityText.click();
        didTriggerLoad = true;
      } else if (sheetId === "activityImage") {
        if (activityImageOutputDir) activityImageOutputDir.value = dir;
        if (btnLoadActivityImage) btnLoadActivityImage.click();
        didTriggerLoad = true;
      } else if (sheetId === "activityGivenStructure") {
        if (givenStructureOutputDir) givenStructureOutputDir.value = dir;
        if (btnLoadGivenStructure) btnLoadGivenStructure.click();
        didTriggerLoad = true;
      } else if (sheetId === "results") {
        if (resultsOutputDir) resultsOutputDir.value = dir;
        if (btnLoadResults) btnLoadResults.click();
        didTriggerLoad = true;
      }
      if (didTriggerLoad) sheetAutoLoadedOnce.add(sheetId);
    }

    function switchSheet(sheetId) {
      tabs.forEach(function (t) {
        const isActive = t.getAttribute("data-sheet") === sheetId;
        t.classList.toggle("active", isActive);
        t.setAttribute("aria-selected", isActive ? "true" : "false");
      });
      panels.forEach(function (p) {
        p.classList.toggle("active", p.getAttribute("data-sheet") === sheetId);
      });
      autoLoadSheetData(sheetId);
    }
    tabs.forEach(function (t) {
      t.addEventListener("click", function () {
        switchSheet(t.getAttribute("data-sheet"));
      });
    });
  })();

  function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
  }

  function formatZoom(z) {
    return String(Math.round(z * 100)) + "%";
  }

  /**
   * 指代 coreference 的展示/编辑用文本（合法 JSON，便于阅读）。
   * 保存时由后端按 indent=4 写入文件，与这里展示格式无关。
   */
  function formatCoreference(coref) {
    // [
    //   [{...},
    //    {...}],
    //   [{...}]
    // ]
    try {
      if (Array.isArray(coref)) {
        if (coref.length === 0) return "[]";
        const groupToText = function (g) {
          if (Array.isArray(g)) {
            if (g.length === 0) return "[]";
            return "[\n" + g.map(function (x) { return JSON.stringify(x); }).join(",\n") + "\n]";
          }
          return JSON.stringify(g);
        };
        return "[\n" + coref.map(function (g) { return groupToText(g); }).join(",\n") + "\n]";
      }
      return JSON.stringify(coref);
    } catch (e) {
      try {
        return String(coref);
      } catch (_) {
        return "";
      }
    }
  }

  function applyDetectionZoom() {
    if (!detectionCanvas || !currentDetectionCanvasW || !currentDetectionCanvasH) return;
    const z = clamp(detectionZoom, 0.1, 6);
    detectionZoom = z;
    // 解除 CSS 的 max-width/max-height 限制，否则放大看起来“没变化”
    detectionCanvas.style.maxWidth = "none";
    detectionCanvas.style.maxHeight = "none";
    detectionCanvas.style.width = Math.round(currentDetectionCanvasW * z) + "px";
    detectionCanvas.style.height = Math.round(currentDetectionCanvasH * z) + "px";
    if (detectionZoomLabel) detectionZoomLabel.textContent = formatZoom(z);
  }

  function fitDetectionToWidth() {
    if (!detectionCanvas || !currentDetectionCanvasW) return;
    const col = detectionCanvas.closest(".detection-canvas-col");
    if (!col) return;
    const padding = 16;
    const available = Math.max(240, col.clientWidth - padding);
    detectionZoom = clamp(available / currentDetectionCanvasW, 0.1, 6);
    detectionZoomMode = "fit";
    applyDetectionZoom();
  }

  function applyImgZoom(imgEl, zoom, labelEl) {
    if (!imgEl || !imgEl.naturalWidth || !imgEl.naturalHeight) return;
    const z = clamp(zoom, 0.1, 6);
    imgEl.style.maxWidth = "none";
    imgEl.style.width = Math.round(imgEl.naturalWidth * z) + "px";
    imgEl.style.height = Math.round(imgEl.naturalHeight * z) + "px";
    if (labelEl) labelEl.textContent = formatZoom(z);
  }

  function fitImgToWidth(imgEl, wrapEl) {
    if (!imgEl || !wrapEl || !imgEl.naturalWidth) return 1;
    const padding = 16;
    const available = Math.max(240, wrapEl.clientWidth - padding);
    return clamp(available / imgEl.naturalWidth, 0.1, 6);
  }

  function setPdfPreview(url) {
    if (lastPdfBlobUrl) {
      URL.revokeObjectURL(lastPdfBlobUrl);
      lastPdfBlobUrl = null;
    }
    if (!url) {
      pdfPreviewPlaceholder.classList.remove("hidden");
      pdfPreviewIframe.classList.add("hidden");
      pdfPreviewIframe.removeAttribute("src");
      return;
    }
    lastPdfBlobUrl = url;
    pdfPreviewPlaceholder.classList.add("hidden");
    pdfPreviewIframe.classList.remove("hidden");
    pdfPreviewIframe.src = url;
  }
  window.addEventListener("beforeunload", () => {
    if (lastPdfBlobUrl) URL.revokeObjectURL(lastPdfBlobUrl);
  });

  function showJobInfo(id, status) {
    jobInfo.classList.remove("hidden");
    jobIdEl.textContent = id;
    jobStatusEl.textContent = status;
  }

  function setLogs(text) {
    logOutput.textContent = text || "";
  }

  async function api(path, options = {}) {
    const res = await fetch(path, {
      headers: options.json ? { "Content-Type": "application/json" } : {},
      ...options,
    });
    const text = await res.text();
    if (!res.ok) throw new Error(text || res.statusText);
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }

  /** 更新「未选择任何文件」/ 文件名（原生 file 控件文案无法随站点语言切换） */
  function updatePdfFileNameDisplay() {
    if (!pdfFileNameDisplay || !pdfFile) return;
    if (pdfFile.files && pdfFile.files.length > 0) {
      pdfFileNameDisplay.textContent = pdfFile.files[0].name;
    } else {
      pdfFileNameDisplay.textContent = tx("input.noFileSelected");
    }
  }

  if (btnPdfFilePick && pdfFile) {
    btnPdfFilePick.addEventListener("click", () => pdfFile.click());
  }

  btnExamplePdf.addEventListener("click", async () => {
    try {
      const data = await api("/api/example_pdf");
      if (data.path) {
        pdfPath.value = data.path;
        pdfFile.value = "";
        updatePdfFileNameDisplay();
      } else {
        alert(data.message || tx("alert.noExamplePdf"));
      }
    } catch (e) {
      alert(tx("alert.exampleFail", { msg: e.message }));
    }
  });

  pdfFile.addEventListener("change", () => {
    if (pdfFile.files.length) pdfPath.value = "";
    setPdfPreview(null);
    updatePdfFileNameDisplay();
  });

  pdfPath.addEventListener("input", () => {
    setPdfPreview(null);
  });

  btnPreviewPdf.addEventListener("click", async () => {
    if (pdfFile.files.length) {
      const url = URL.createObjectURL(pdfFile.files[0]);
      setPdfPreview(url);
      return;
    }
    const path = pdfPath.value.trim();
    if (!path) {
      alert(tx("alert.needPdf"));
      return;
    }
    try {
      const res = await fetch("/api/pdf?path=" + encodeURIComponent(path));
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || res.statusText);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setPdfPreview(url);
    } catch (e) {
      alert(tx("alert.previewFail", { msg: e.message }));
    }
  });

  btnLoadConfig.addEventListener("click", async () => {
    const path = configPath.value.trim() || undefined;
    try {
      const data = await api("/api/config" + (path ? "?path=" + encodeURIComponent(path) : ""));
      baseUrl.value = data.base_url || "";
      apiKey.value = data.api_key || "";
      textMllmType.value = data.text_mllm_type || "";
      visionMllmType.value = data.vision_mllm_type || "";
    } catch (e) {
      alert(tx("alert.loadConfigFail", { msg: e.message }));
    }
  });

  btnSaveConfig.addEventListener("click", async () => {
    try {
      await api("/api/config", {
        method: "POST",
        json: true,
        body: JSON.stringify({
          config_path: configPath.value.trim() || undefined,
          base_url: baseUrl.value.trim() || undefined,
          api_key: apiKey.value.trim() || undefined,
          text_mllm_type: textMllmType.value.trim() || undefined,
          vision_mllm_type: visionMllmType.value.trim() || undefined,
        }),
      });
      alert(tx("alert.savedConfig"));
    } catch (e) {
      alert(tx("alert.saveConfigFail", { msg: e.message }));
    }
  });

  btnRun.addEventListener("click", async () => {
    const form = new FormData();
    if (pdfFile.files.length) {
      form.append("file", pdfFile.files[0]);
    } else if (pdfPath.value.trim()) {
      form.append("pdf", pdfPath.value.trim());
    } else {
      alert(tx("alert.needPdfRun"));
      return;
    }
    form.append("output_dir", outputDir.value.trim() || "tmp_output/demo_ui");
    form.append("config_path", configPath.value.trim() || "BioMiner/config/default_open_source.yaml");

    btnRun.disabled = true;
    setLogs(tx("log.submitting"));
    try {
      const data = await api("/api/run", { method: "POST", body: form });
      showJobInfo(data.job_id, "pending");
      resultsOutputDir.value = data.output_dir;
      if (!detectionOutputDir.value.trim()) detectionOutputDir.value = data.output_dir;
      if (activityOutputDir && !activityOutputDir.value.trim()) activityOutputDir.value = data.output_dir;
      if (activityImageOutputDir && !activityImageOutputDir.value.trim()) activityImageOutputDir.value = data.output_dir;
      if (markushOutputDir && !markushOutputDir.value.trim()) markushOutputDir.value = data.output_dir;
      if (markushPartOutputDir && !markushPartOutputDir.value.trim()) markushPartOutputDir.value = data.output_dir;
      setLogs(tx("log.submitted"));
      let interval = setInterval(pollJob, 2000);
      function pollJob() {
        fetch("/api/job/" + data.job_id)
          .then((r) => r.json())
          .then((j) => {
            jobStatusEl.textContent = j.status;
            setLogs(j.logs.join("\n"));
            if (j.status === "completed" || j.status === "failed") {
              clearInterval(interval);
              btnRun.disabled = false;
            }
          })
          .catch(() => clearInterval(interval));
      }
    } catch (e) {
      setLogs(tx("log.submitFail", { msg: e.message }));
      btnRun.disabled = false;
    }
  });

  btnRefreshJob.addEventListener("click", async () => {
    const id = jobIdEl.textContent;
    if (!id) return;
    try {
      const j = await api("/api/job/" + id);
      jobStatusEl.textContent = j.status;
      setLogs(j.logs.join("\n"));
    } catch (e) {
      setLogs(tx("log.statusFail", { msg: e.message }));
    }
  });

  function renderResultsTable(rows) {
    if (!resultsThead || !resultsTbody) return;
    const emptyHint = $("resultsTableEmptyHint");
    resultsThead.innerHTML = "";
    resultsTbody.innerHTML = "";
    if (!rows || rows.length === 0) {
      if (emptyHint) emptyHint.classList.remove("hidden");
      return;
    }
    if (emptyHint) emptyHint.classList.add("hidden");
    const actualHeaders = Object.keys(rows[0]);
    const hasLigand = actualHeaders.some((h) => h.toLowerCase() === "ligand");
    actualHeaders.forEach((h) => {
      const th = document.createElement("th");
      th.textContent = h;
      resultsThead.appendChild(th);
    });
    if (hasLigand) {
      const opTh = document.createElement("th");
      opTh.textContent = tx("common.operation");
      resultsThead.appendChild(opTh);
    }
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      actualHeaders.forEach((h) => {
        const td = document.createElement("td");
        const cellVal = row[h];
        if (String(h).toLowerCase() === "smiles") td.classList.add("smiles-cell");
        if (String(h).toLowerCase() === "similarity") {
          const n = parseFloat(cellVal);
          td.textContent = Number.isNaN(n) ? (cellVal != null ? String(cellVal) : "") : n.toFixed(2);
        } else {
          td.textContent = cellVal != null ? String(cellVal) : "";
        }
        tr.appendChild(td);
      });
      if (hasLigand) {
        const ligandVal = (row["ligand"] != null ? String(row["ligand"]) : "").trim();
        const td = document.createElement("td");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn-view-mol";
        btn.textContent = tx("common.viewMol");
        btn.addEventListener("click", () => {
          if (typeof window.biominerKetcherSetMolecule === "function") {
            window.biominerKetcherSetMolecule(ligandVal);
            if (detectionBboxListWrap && detectionKetcherCol) {
              detectionBboxListWrap.classList.add("hidden");
              detectionKetcherCol.classList.remove("hidden");
            }
            document.querySelectorAll(".sheet-tab").forEach(function (t) {
              const isDetection = t.getAttribute("data-sheet") === "detection";
              t.classList.toggle("active", isDetection);
              t.setAttribute("aria-selected", isDetection ? "true" : "false");
            });
            document.querySelectorAll(".sheet-panel").forEach(function (p) {
              p.classList.toggle("active", p.getAttribute("data-sheet") === "detection");
            });
            document.querySelector("#detectionKetcherCol")?.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
        td.appendChild(btn);
        tr.appendChild(td);
      }
      resultsTbody.appendChild(tr);
    });
  }

  function getResultsFilteredRows() {
    if (!lastResultsRows) return [];
    const doc = resultsDocFilter && resultsDocFilter.value;
    if (doc) {
      return lastResultsRows.filter((r) => String(r.doc != null ? r.doc : "") === doc);
    }
    return lastResultsRows;
  }

  function renderResultsTableWithPagination() {
    const filtered = getResultsFilteredRows();
    if (!filtered || filtered.length === 0) {
      renderResultsTable([]);
      if (resultsPaginationRow) resultsPaginationRow.classList.add("hidden");
      return;
    }
    const totalPages = Math.ceil(filtered.length / RESULTS_PAGE_SIZE) || 1;
    if (resultsCurrentPage > totalPages) resultsCurrentPage = totalPages;
    if (resultsCurrentPage < 1) resultsCurrentPage = 1;
    const start = (resultsCurrentPage - 1) * RESULTS_PAGE_SIZE;
    const pageRows = filtered.slice(start, start + RESULTS_PAGE_SIZE);
    renderResultsTable(pageRows);
    if (resultsPaginationRow) resultsPaginationRow.classList.remove("hidden");
    if (resultsPaginationInfo) {
      resultsPaginationInfo.textContent = tx("pagination.results", {
        total: filtered.length,
        cur: resultsCurrentPage,
        pages: totalPages,
        size: RESULTS_PAGE_SIZE,
      });
    }
    if (btnResultsFirstPage) btnResultsFirstPage.disabled = resultsCurrentPage <= 1;
    if (btnResultsPrevPage) btnResultsPrevPage.disabled = resultsCurrentPage <= 1;
    if (btnResultsNextPage) btnResultsNextPage.disabled = resultsCurrentPage >= totalPages;
    if (btnResultsLastPage) btnResultsLastPage.disabled = resultsCurrentPage >= totalPages;
  }

  btnLoadResults.addEventListener("click", async () => {
    const dir = resultsOutputDir.value.trim();
    if (!dir) {
      alert(tx("common.fillResultDir"));
      return;
    }
    setButtonLoading(btnLoadResults, true);
    const resultsEmptyHint = $("resultsTableEmptyHint");
    if (resultsEmptyHint) resultsEmptyHint.classList.add("hidden");
    if (resultsSummary) {
      resultsSummary.classList.remove("hidden");
      resultsSummary.textContent = tx("common.loadingLong");
    }
    try {
      const data = await api("/api/results?output_dir=" + encodeURIComponent(dir));
      lastResultsRows = data.rows || [];
      if (resultsSummary) {
        resultsSummary.classList.remove("hidden");
        resultsSummary.textContent = tx("results.summary", {
          dir: data.output_dir || "",
          total: lastResultsRows.length,
          size: RESULTS_PAGE_SIZE,
        });
      }
      if (resultsDocFilterRow) resultsDocFilterRow.classList.remove("hidden");
      if (resultsDocFilter) {
        resultsDocFilter.innerHTML = "";
        const optAll = document.createElement("option");
        optAll.value = "";
        optAll.textContent = tx("results.allDocs");
        resultsDocFilter.appendChild(optAll);
        const docs = (data.doc_names && data.doc_names.length)
          ? data.doc_names
          : lastResultsRows.length > 0 && lastResultsRows[0].hasOwnProperty("doc")
            ? [...new Set(lastResultsRows.map((r) => String(r.doc != null ? r.doc : "")))].filter(Boolean).sort()
            : [];
        docs.forEach((d) => {
          const opt = document.createElement("option");
          opt.value = d;
          opt.textContent = d;
          resultsDocFilter.appendChild(opt);
        });
        resultsDocFilter.onchange = () => {
          resultsCurrentPage = 1;
          renderResultsTableWithPagination();
        };
        resultsDocFilter.value = "";
      }
      resultsCurrentPage = 1;
      renderResultsTableWithPagination();
    } catch (e) {
      if (resultsSummary) {
        resultsSummary.classList.remove("hidden");
        resultsSummary.textContent = tx("results.loadFail", { msg: e.message });
      }
      renderResultsTable([]);
      if (resultsDocFilterRow) resultsDocFilterRow.classList.add("hidden");
      if (resultsPaginationRow) resultsPaginationRow.classList.add("hidden");
      lastResultsRows = null;
    } finally {
      setButtonLoading(btnLoadResults, false);
    }
  });

  if (btnResultsFirstPage) {
    btnResultsFirstPage.addEventListener("click", () => {
      resultsCurrentPage = 1;
      renderResultsTableWithPagination();
    });
  }
  if (btnResultsPrevPage) {
    btnResultsPrevPage.addEventListener("click", () => {
      resultsCurrentPage--;
      renderResultsTableWithPagination();
    });
  }
  if (btnResultsNextPage) {
    btnResultsNextPage.addEventListener("click", () => {
      resultsCurrentPage++;
      renderResultsTableWithPagination();
    });
  }
  if (btnResultsLastPage) {
    btnResultsLastPage.addEventListener("click", () => {
      const filtered = getResultsFilteredRows();
      const totalPages = Math.ceil(filtered.length / RESULTS_PAGE_SIZE) || 1;
      resultsCurrentPage = totalPages;
      renderResultsTableWithPagination();
    });
  }

  function fillGivenStructureKetcherHint(row) {
    const hint = $("givenStructureKetcherHint");
    if (!hint) return;
    const simV = row && row.similarity != null ? row.similarity : "";
    let simTxt = "—";
    if (simV !== "" && simV != null) {
      const n = parseFloat(simV);
      simTxt = Number.isNaN(n) ? String(simV) : n.toFixed(2);
    }
    const lig = row && row.ligand != null ? String(row.ligand) : "";
    const ligPart = lig ? tx("givenStruct.ketcherHintLig", { lig }) : "";
    hint.textContent = tx("givenStruct.ketcherHint", { sim: simTxt, lig: ligPart });
  }

  function openGivenStructureKetcherOverlay(row) {
    const overlay = $("givenStructureKetcherOverlay");
    if (!overlay) return;
    overlay.classList.remove("hidden");
    overlay.setAttribute("aria-hidden", "false");
    lastGivenStructureKetcherRow = row || null;
    fillGivenStructureKetcherHint(row);
    const smi = row && row.smiles != null ? String(row.smiles).trim() : "";
    if (smi && typeof window.biominerGivenStructureKetcherSetMolecule === "function") {
      window.biominerGivenStructureKetcherSetMolecule(smi);
    } else {
      const inp = $("givenStructureKetcherSmilesInput");
      if (inp) inp.value = "";
      if (!smi) {
        alert(tx("alert.noRowSmiles"));
      }
    }
  }

  function closeGivenStructureKetcherOverlay() {
    const overlay = $("givenStructureKetcherOverlay");
    if (overlay) {
      overlay.classList.add("hidden");
      overlay.setAttribute("aria-hidden", "true");
    }
    lastGivenStructureKetcherRow = null;
  }

  function renderGivenStructureTable(rows) {
    if (!givenStructureThead || !givenStructureTbody) return;
    givenStructureThead.innerHTML = "";
    givenStructureTbody.innerHTML = "";
    if (!rows || rows.length === 0) return;

    // 隐藏仅用于追踪来源的辅助列，以及不在表中展示的 smiles（由「查看分子」使用）
    const hiddenCols = new Set(["doc", "text_mllm_type", "source_file", "smiles"]);
    const actualHeaders = Object.keys(rows[0]).filter((h) => !hiddenCols.has(h));

    actualHeaders.forEach((h) => {
      const th = document.createElement("th");
      th.textContent = h;
      const hl = String(h).toLowerCase();
      if (hl === "type" || hl === "unit" || hl === "value") {
        th.classList.add("given-structure-col-compact");
      }
      if (hl === "similarity") {
        th.classList.add("given-structure-col-sim");
      }
      givenStructureThead.appendChild(th);
    });
    const thOp = document.createElement("th");
    thOp.textContent = tx("common.operation");
    thOp.className = "given-structure-col-op";
    givenStructureThead.appendChild(thOp);

    rows.forEach((row) => {
      const tr = document.createElement("tr");
      actualHeaders.forEach((h) => {
        const td = document.createElement("td");
        const cellVal = row[h];
        if (String(h).toLowerCase() === "similarity") {
          const n = parseFloat(cellVal);
          td.textContent = Number.isNaN(n) ? (cellVal != null ? String(cellVal) : "") : n.toFixed(2);
        } else {
          td.textContent = cellVal != null ? String(cellVal) : "";
        }
        const hl = String(h).toLowerCase();
        if (hl === "ligand") {
          td.classList.add("ligand-cell");
        }
        if (hl === "type" || hl === "unit" || hl === "value") {
          td.classList.add("given-structure-col-compact");
        }
        if (hl === "similarity") {
          td.classList.add("given-structure-col-sim");
        }
        tr.appendChild(td);
      });

      const tdOp = document.createElement("td");
      tdOp.className = "given-structure-col-op";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn small";
      btn.textContent = tx("common.viewMol");
      btn.addEventListener("click", () => {
        openGivenStructureKetcherOverlay(row);
      });
      tdOp.appendChild(btn);
      tr.appendChild(tdOp);

      givenStructureTbody.appendChild(tr);
    });
  }

  function getGivenStructureFilteredRows() {
    if (!lastGivenStructureRows) return [];
    const doc = givenStructureDocFilter && givenStructureDocFilter.value;
    if (doc) return lastGivenStructureRows.filter((r) => String(r.doc != null ? r.doc : "") === doc);
    return lastGivenStructureRows;
  }

  function renderGivenStructureTableWithPagination() {
    const filtered = getGivenStructureFilteredRows();
    if (!filtered || filtered.length === 0) {
      renderGivenStructureTable([]);
      if (givenStructurePaginationRow) givenStructurePaginationRow.classList.add("hidden");
      return;
    }
    const totalPages = Math.ceil(filtered.length / GIVEN_STRUCTURE_PAGE_SIZE) || 1;
    if (givenStructureCurrentPage > totalPages) givenStructureCurrentPage = totalPages;
    if (givenStructureCurrentPage < 1) givenStructureCurrentPage = 1;

    const start = (givenStructureCurrentPage - 1) * GIVEN_STRUCTURE_PAGE_SIZE;
    const pageRows = filtered.slice(start, start + GIVEN_STRUCTURE_PAGE_SIZE);
    renderGivenStructureTable(pageRows);

    if (givenStructurePaginationRow) givenStructurePaginationRow.classList.remove("hidden");
    if (givenStructurePaginationInfo) {
      givenStructurePaginationInfo.textContent = tx("pagination.results", {
        total: filtered.length,
        cur: givenStructureCurrentPage,
        pages: totalPages,
        size: GIVEN_STRUCTURE_PAGE_SIZE,
      });
    }
    if (btnGivenStructureFirstPage) btnGivenStructureFirstPage.disabled = givenStructureCurrentPage <= 1;
    if (btnGivenStructurePrevPage) btnGivenStructurePrevPage.disabled = givenStructureCurrentPage <= 1;
    if (btnGivenStructureNextPage) btnGivenStructureNextPage.disabled = givenStructureCurrentPage >= totalPages;
    if (btnGivenStructureLastPage) btnGivenStructureLastPage.disabled = givenStructureCurrentPage >= totalPages;
  }

  function refreshGivenStructureGivenSmilesPanel() {
    if (!givenStructureGivenSmilesWrap || !givenStructureGivenSmilesImg || !givenStructureGivenSmilesErr) return;
    if (!givenStructureImageResultRow || givenStructureImageResultRow.classList.contains("hidden")) {
      givenStructureGivenSmilesWrap.classList.add("hidden");
      if (givenStructurePdbIdLine) givenStructurePdbIdLine.classList.add("hidden");
      if (givenStructurePdbIdValue) givenStructurePdbIdValue.textContent = "";
      if (givenStructurePdbIdLink) {
        givenStructurePdbIdLink.classList.add("hidden");
        givenStructurePdbIdLink.removeAttribute("href");
        givenStructurePdbIdLink.removeAttribute("title");
      }
      if (givenStructurePdbTitleLine) givenStructurePdbTitleLine.classList.add("hidden");
      if (givenStructurePdbTitleValue) givenStructurePdbTitleValue.textContent = "";
      return;
    }
    const doc = givenStructureDocFilter && givenStructureDocFilter.value;
    if (!doc) {
      givenStructureGivenSmilesWrap.classList.add("hidden");
      givenStructureGivenSmilesImg.removeAttribute("src");
      givenStructureGivenSmilesImg.classList.add("hidden");
      givenStructureGivenSmilesErr.classList.add("hidden");
      givenStructureGivenSmilesErr.textContent = "";
      if (givenStructurePdbIdLine) givenStructurePdbIdLine.classList.add("hidden");
      if (givenStructurePdbIdValue) givenStructurePdbIdValue.textContent = "";
      if (givenStructurePdbIdLink) {
        givenStructurePdbIdLink.classList.add("hidden");
        givenStructurePdbIdLink.removeAttribute("href");
        givenStructurePdbIdLink.removeAttribute("title");
      }
      if (givenStructurePdbTitleLine) givenStructurePdbTitleLine.classList.add("hidden");
      if (givenStructurePdbTitleValue) givenStructurePdbTitleValue.textContent = "";
      return;
    }
    givenStructureGivenSmilesWrap.classList.remove("hidden");
    if (givenStructurePdbIdLine && givenStructurePdbIdValue) {
      givenStructurePdbIdLine.classList.remove("hidden");
      const pid =
        lastPdbIdByDoc && Object.prototype.hasOwnProperty.call(lastPdbIdByDoc, doc)
          ? lastPdbIdByDoc[doc]
          : null;
      const pidStr = pid != null && String(pid).trim() !== "" ? String(pid).trim() : "";
      givenStructurePdbIdValue.textContent = pidStr || "—";
      if (givenStructurePdbIdLink) {
        if (pidStr) {
          // Some doc IDs come as "<prefix>_<pdbid>" (e.g. "1_4KMN"), use the last segment for RCSB URL.
          const pdbRaw = pidStr.includes("_") ? pidStr.split("_").pop() : pidStr;
          const pdbForUrl = String(pdbRaw || "").trim().toUpperCase();
          givenStructurePdbIdLink.href = "https://www.rcsb.org/structure/" + encodeURIComponent(pdbForUrl);
          givenStructurePdbIdLink.title = "https://www.rcsb.org/structure/" + pdbForUrl;
          givenStructurePdbIdLink.classList.remove("hidden");
        } else {
          givenStructurePdbIdLink.classList.add("hidden");
          givenStructurePdbIdLink.removeAttribute("href");
          givenStructurePdbIdLink.removeAttribute("title");
        }
      }
    }
    if (givenStructurePdbTitleLine && givenStructurePdbTitleValue) {
      givenStructurePdbTitleLine.classList.remove("hidden");
      const pidForTitle =
        lastPdbIdByDoc && Object.prototype.hasOwnProperty.call(lastPdbIdByDoc, doc)
          ? lastPdbIdByDoc[doc]
          : null;
      const pidStrForTitle =
        pidForTitle != null && String(pidForTitle).trim() !== "" ? String(pidForTitle).trim() : "";
      const tit =
        lastPdbTitleByDoc && Object.prototype.hasOwnProperty.call(lastPdbTitleByDoc, doc)
          ? lastPdbTitleByDoc[doc]
          : null;
      if (tit != null && String(tit).trim() !== "") {
        givenStructurePdbTitleValue.textContent = String(tit).trim();
      } else if (pidStrForTitle) {
        givenStructurePdbTitleValue.textContent = tx("givenStruct.pdbTitleMissing");
      } else {
        givenStructurePdbTitleValue.textContent = tx("givenStruct.noPdbTitle");
      }
    }
    const smi =
      lastGivenSmilesByDoc && Object.prototype.hasOwnProperty.call(lastGivenSmilesByDoc, doc)
        ? lastGivenSmilesByDoc[doc]
        : null;
    if (smi != null && String(smi).trim() !== "") {
      const s = String(smi).trim();
      givenStructureGivenSmilesErr.classList.add("hidden");
      givenStructureGivenSmilesErr.textContent = "";
      givenStructureGivenSmilesImg.classList.remove("hidden");
      givenStructureGivenSmilesImg.alt = tx("givenStruct.givenImgAltRdkit");
      givenStructureGivenSmilesImg.title = s;
      givenStructureGivenSmilesImg.src = "/api/mol_rdkit_svg?smiles=" + encodeURIComponent(s);
    } else {
      givenStructureGivenSmilesImg.removeAttribute("src");
      givenStructureGivenSmilesImg.classList.add("hidden");
      givenStructureGivenSmilesErr.classList.remove("hidden");
      givenStructureGivenSmilesErr.textContent = tx("givenStruct.smilesErr");
    }
  }

  if (givenStructureGivenSmilesImg) {
    givenStructureGivenSmilesImg.addEventListener("error", function () {
      const smiTitle = this.title;
      this.classList.add("hidden");
      this.removeAttribute("src");
      if (givenStructureGivenSmilesErr) {
        givenStructureGivenSmilesErr.classList.remove("hidden");
        givenStructureGivenSmilesErr.textContent = tx("givenStruct.rdkitErr", {
          extra: smiTitle ? tx("givenStruct.extraSmiles", { s: smiTitle }) : "",
        });
      }
    });
  }

  function refreshGivenStructureDocPdfPreview() {
    if (!givenStructureDocPdfWrap || !givenStructureDocPdfIframe || !givenStructureDocFilter) return;

    const dir = givenStructureOutputDir && givenStructureOutputDir.value ? String(givenStructureOutputDir.value).trim() : "";
    const doc = givenStructureDocFilter.value;

    if (!dir || !doc) {
      givenStructureDocPdfWrap.classList.add("hidden");
      givenStructureDocPdfWrap.classList.remove("page-image-loaded");
      if (givenStructureDocPdfIframe) {
        givenStructureDocPdfIframe.classList.add("hidden");
        givenStructureDocPdfIframe.removeAttribute("src");
      }
      if (givenStructureDocPdfPlaceholder) givenStructureDocPdfPlaceholder.textContent = tx("common.pdfDocPreview");
      refreshGivenStructureGivenSmilesPanel();
      return;
    }

    givenStructureDocPdfWrap.classList.remove("hidden");
    givenStructureDocPdfWrap.classList.remove("page-image-loaded");
    if (givenStructureDocPdfIframe) givenStructureDocPdfIframe.classList.remove("hidden");
    if (givenStructureDocPdfPlaceholder) givenStructureDocPdfPlaceholder.textContent = tx("common.pdfLoading");

    givenStructureDocPdfIframe.onload = function () {
      if (givenStructureDocPdfWrap) givenStructureDocPdfWrap.classList.add("page-image-loaded");
      if (givenStructureDocPdfPlaceholder) givenStructureDocPdfPlaceholder.textContent = "";
    };

    givenStructureDocPdfIframe.src =
      "/api/activity_doc_pdf?output_dir=" + encodeURIComponent(dir) + "&doc=" + encodeURIComponent(doc);
    refreshGivenStructureGivenSmilesPanel();
  }

  if (btnLoadGivenStructure) {
    btnLoadGivenStructure.addEventListener("click", async () => {
      const dir = givenStructureOutputDir.value.trim();
      if (!dir) {
        alert(tx("common.fillResultDir"));
        return;
      }
      setButtonLoading(btnLoadGivenStructure, true);
      if (givenStructureSummary) {
        givenStructureSummary.classList.remove("hidden");
        givenStructureSummary.textContent = tx("common.loadingLong");
      }
      try {
        let gsUrl = "/api/activity_given_structure?output_dir=" + encodeURIComponent(dir);
        if (configPath && configPath.value && String(configPath.value).trim()) {
          gsUrl += "&config_path=" + encodeURIComponent(String(configPath.value).trim());
        }
        const data = await api(gsUrl);
        lastGivenStructureRows = data.rows || [];
        lastGivenSmilesByDoc = data.given_smiles_by_doc && typeof data.given_smiles_by_doc === "object" ? data.given_smiles_by_doc : {};
        lastPdbIdByDoc = data.pdb_id_by_doc && typeof data.pdb_id_by_doc === "object" ? data.pdb_id_by_doc : {};
        lastPdbTitleByDoc =
          data.pdb_title_by_doc && typeof data.pdb_title_by_doc === "object" ? data.pdb_title_by_doc : {};
        if (givenStructureSummary) {
          givenStructureSummary.classList.remove("hidden");
          givenStructureSummary.textContent = tx("results.summary", {
            dir: data.output_dir || "",
            total: lastGivenStructureRows.length,
            size: GIVEN_STRUCTURE_PAGE_SIZE,
          });
        }
        if (givenStructureImageResultRow) givenStructureImageResultRow.classList.remove("hidden");
        if (givenStructureDocFilterRow) givenStructureDocFilterRow.classList.remove("hidden");
        if (givenStructureDocFilter) {
          const docs =
            data.doc_names && data.doc_names.length
              ? data.doc_names
              : lastGivenStructureRows.length > 0 && lastGivenStructureRows[0].hasOwnProperty("doc")
                ? [...new Set(lastGivenStructureRows.map((r) => String(r.doc != null ? r.doc : "")))].filter(Boolean).sort()
                : [];

          // 重新渲染文档列表：清空旧 options，避免重复追加
          givenStructureDocFilter.innerHTML = "";

          docs.forEach((d) => {
            const opt = document.createElement("option");
            opt.value = d;
            opt.textContent = d;
            givenStructureDocFilter.appendChild(opt);
          });

          // 强制默认选中第一个文档并立刻预览
          if (docs.length > 0) {
            givenStructureDocFilter.value = docs[0];
          } else {
            if (givenStructureDocFilterRow) givenStructureDocFilterRow.classList.add("hidden");
          }

          givenStructureDocFilter.onchange = () => {
            givenStructureCurrentPage = 1;
            renderGivenStructureTableWithPagination();
            refreshGivenStructureDocPdfPreview();
          };
        }
        givenStructureCurrentPage = 1;
        renderGivenStructureTableWithPagination();
        refreshGivenStructureDocPdfPreview();
      } catch (e) {
        if (givenStructureSummary) {
          givenStructureSummary.classList.remove("hidden");
          givenStructureSummary.textContent = tx("results.loadFail", { msg: e.message });
        }
        if (givenStructureThead) givenStructureThead.innerHTML = "";
        if (givenStructureTbody) givenStructureTbody.innerHTML = "";
        if (givenStructureImageResultRow) givenStructureImageResultRow.classList.add("hidden");
        if (givenStructureDocFilterRow) givenStructureDocFilterRow.classList.add("hidden");
        if (givenStructurePaginationRow) givenStructurePaginationRow.classList.add("hidden");
        if (givenStructureDocPdfWrap) givenStructureDocPdfWrap.classList.add("hidden");
        if (givenStructureDocPdfIframe) {
          givenStructureDocPdfIframe.classList.add("hidden");
          givenStructureDocPdfIframe.removeAttribute("src");
        }
        lastGivenStructureRows = null;
        lastGivenSmilesByDoc = null;
        lastPdbIdByDoc = null;
        lastPdbTitleByDoc = null;
        if (givenStructureGivenSmilesWrap) givenStructureGivenSmilesWrap.classList.add("hidden");
        if (givenStructurePdbIdLine) givenStructurePdbIdLine.classList.add("hidden");
        if (givenStructurePdbIdValue) givenStructurePdbIdValue.textContent = "";
        if (givenStructurePdbIdLink) {
          givenStructurePdbIdLink.classList.add("hidden");
          givenStructurePdbIdLink.removeAttribute("href");
          givenStructurePdbIdLink.removeAttribute("title");
        }
        if (givenStructurePdbTitleLine) givenStructurePdbTitleLine.classList.add("hidden");
        if (givenStructurePdbTitleValue) givenStructurePdbTitleValue.textContent = "";
        closeGivenStructureKetcherOverlay();
      } finally {
        setButtonLoading(btnLoadGivenStructure, false);
      }
    });
  }

  const btnGivenStructureKetcherBack = $("btnGivenStructureKetcherBack");
  const btnGivenStructureKetcherLoadGiven = $("btnGivenStructureKetcherLoadGiven");
  if (btnGivenStructureKetcherBack) {
    btnGivenStructureKetcherBack.addEventListener("click", () => {
      closeGivenStructureKetcherOverlay();
    });
  }
  if (btnGivenStructureKetcherLoadGiven) {
    btnGivenStructureKetcherLoadGiven.addEventListener("click", () => {
      const doc = givenStructureDocFilter && givenStructureDocFilter.value;
      const g =
        doc && lastGivenSmilesByDoc && Object.prototype.hasOwnProperty.call(lastGivenSmilesByDoc, doc)
          ? lastGivenSmilesByDoc[doc]
          : null;
      const s = g != null ? String(g).trim() : "";
      if (s && typeof window.biominerGivenStructureKetcherSetMolecule === "function") {
        window.biominerGivenStructureKetcherSetMolecule(s);
      } else {
        alert(tx("alert.noGivenDoc"));
      }
    });
  }

  if (btnGivenStructureFirstPage) {
    btnGivenStructureFirstPage.addEventListener("click", () => {
      givenStructureCurrentPage = 1;
      renderGivenStructureTableWithPagination();
    });
  }
  if (btnGivenStructurePrevPage) {
    btnGivenStructurePrevPage.addEventListener("click", () => {
      givenStructureCurrentPage--;
      renderGivenStructureTableWithPagination();
    });
  }
  if (btnGivenStructureNextPage) {
    btnGivenStructureNextPage.addEventListener("click", () => {
      givenStructureCurrentPage++;
      renderGivenStructureTableWithPagination();
    });
  }
  if (btnGivenStructureLastPage) {
    btnGivenStructureLastPage.addEventListener("click", () => {
      const filtered = getGivenStructureFilteredRows();
      const totalPages = Math.ceil(filtered.length / GIVEN_STRUCTURE_PAGE_SIZE) || 1;
      givenStructureCurrentPage = totalPages;
      renderGivenStructureTableWithPagination();
    });
  }

  function renderActivityTextTable(rows) {
    if (!activityThead || !activityTbody) return;
    activityThead.innerHTML = "";
    activityTbody.innerHTML = "";
    if (!rows || rows.length === 0) return;
    // 右侧表格不显示筛选/保存用的字段；其它可见列都可编辑（编辑保存时写回同名列，全部当字符串处理）
    const hiddenCols = new Set(["doc", "source_suffix", "row_id"]);
    const headers = Object.keys(rows[0]).filter((h) => !hiddenCols.has(h));
    headers.forEach((h) => {
      const th = document.createElement("th");
      th.textContent = h;
      activityThead.appendChild(th);
    });
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      headers.forEach((h) => {
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.type = "text";
        input.className = "results-edit-input";
        input.value = row[h] != null ? String(row[h]) : "";
        const key =
          String(row.doc != null ? row.doc : "") +
          "__" +
          String(row.source_suffix != null ? row.source_suffix : "") +
          "__" +
          String(row.row_id != null ? row.row_id : "") +
          "__" +
          String(h);
        input.addEventListener("input", () => {
          activityTextEdits.set(key, {
            doc: row.doc,
            source_suffix: row.source_suffix,
            row_id: row.row_id,
            column: h,
            value: input.value,
          });
        });
        td.appendChild(input);
        tr.appendChild(td);
      });
      activityTbody.appendChild(tr);
    });
  }

  function getActivityTextFilteredRows() {
    if (!lastActivityTextRows) return [];
    const doc = activityDocFilter && activityDocFilter.value;
    if (doc) {
      return lastActivityTextRows.filter((r) => String(r.doc != null ? r.doc : "") === doc);
    }
    return lastActivityTextRows;
  }

  function renderActivityTextTableWithPagination() {
    const filtered = getActivityTextFilteredRows();
    if (!filtered || filtered.length === 0) {
      renderActivityTextTable([]);
      if (activityPaginationRow) activityPaginationRow.classList.add("hidden");
      return;
    }
    const totalPages = Math.ceil(filtered.length / ACTIVITY_TEXT_PAGE_SIZE) || 1;
    if (activityTextCurrentPage > totalPages) activityTextCurrentPage = totalPages;
    if (activityTextCurrentPage < 1) activityTextCurrentPage = 1;
    const start = (activityTextCurrentPage - 1) * ACTIVITY_TEXT_PAGE_SIZE;
    const pageRows = filtered.slice(start, start + ACTIVITY_TEXT_PAGE_SIZE);
    renderActivityTextTable(pageRows);
    if (activityPaginationRow) activityPaginationRow.classList.remove("hidden");
    if (activityPaginationInfo) {
      activityPaginationInfo.textContent = tx("pagination.results", {
        total: filtered.length,
        cur: activityTextCurrentPage,
        pages: totalPages,
        size: ACTIVITY_TEXT_PAGE_SIZE,
      });
    }
    if (btnActivityFirstPage) btnActivityFirstPage.disabled = activityTextCurrentPage <= 1;
    if (btnActivityPrevPage) btnActivityPrevPage.disabled = activityTextCurrentPage <= 1;
    if (btnActivityNextPage) btnActivityNextPage.disabled = activityTextCurrentPage >= totalPages;
    if (btnActivityLastPage) btnActivityLastPage.disabled = activityTextCurrentPage >= totalPages;
  }

  function refreshActivityTextDocPdfPreview() {
    if (!activityTextDocPdfWrap || !activityTextDocPdfIframe || !activityDocFilter) return;

    const dir =
      lastActivityTextOutputDir ||
      (activityOutputDir && activityOutputDir.value ? String(activityOutputDir.value).trim() : "");
    const doc = activityDocFilter.value;

    if (!dir || !doc) {
      activityTextDocPdfWrap.classList.add("hidden");
      activityTextDocPdfWrap.classList.remove("page-image-loaded");
      if (activityTextDocPdfIframe) {
        activityTextDocPdfIframe.classList.add("hidden");
        activityTextDocPdfIframe.removeAttribute("src");
      }
      if (activityTextDocPdfPlaceholder) {
        activityTextDocPdfPlaceholder.textContent = tx("common.pdfDocPreview");
      }
      return;
    }

    activityTextDocPdfWrap.classList.remove("hidden");
    activityTextDocPdfWrap.classList.remove("page-image-loaded");
    if (activityTextDocPdfIframe) activityTextDocPdfIframe.classList.remove("hidden");

    if (activityTextDocPdfPlaceholder) activityTextDocPdfPlaceholder.textContent = tx("common.pdfLoading");

    activityTextDocPdfIframe.onload = function () {
      if (activityTextDocPdfWrap) activityTextDocPdfWrap.classList.add("page-image-loaded");
      if (activityTextDocPdfPlaceholder) activityTextDocPdfPlaceholder.textContent = "";
    };

    activityTextDocPdfIframe.src =
      "/api/activity_doc_pdf?output_dir=" + encodeURIComponent(dir) + "&doc=" + encodeURIComponent(doc);
  }

  function setButtonLoading(btn, loading) {
    if (!btn) return;
    const key = btn.getAttribute("data-i18n");
    if (loading) {
      btn.disabled = true;
      btn.textContent = tx("common.loading");
    } else {
      btn.disabled = false;
      if (key) btn.textContent = tx(key);
    }
  }

  if (btnLoadActivityText) {
    btnLoadActivityText.addEventListener("click", async () => {
      const dir = (activityOutputDir && activityOutputDir.value) ? activityOutputDir.value.trim() : "";
      if (!dir) {
        alert(tx("common.fillResultDir"));
        return;
      }
      setButtonLoading(btnLoadActivityText, true);
      if (activitySummary) {
        activitySummary.classList.remove("hidden");
        activitySummary.textContent = tx("common.loadingLong");
      }
      try {
        const data = await api("/api/activity_text?output_dir=" + encodeURIComponent(dir));
        lastActivityTextRows = data.rows || [];
        lastActivityTextOutputDir = data.output_dir || dir;
        if (activitySummary) {
          activitySummary.classList.remove("hidden");
          activitySummary.textContent = tx("activity.summary", {
            dir: data.output_dir || "",
            total: lastActivityTextRows.length,
            size: ACTIVITY_TEXT_PAGE_SIZE,
          });
        }
        if (activityDocFilterRow) activityDocFilterRow.classList.remove("hidden");
        if (activityDocFilter) {
          activityDocFilter.innerHTML = "";
          const docs = (data.doc_names && data.doc_names.length)
            ? data.doc_names
            : (lastActivityTextRows.length > 0 && lastActivityTextRows[0].hasOwnProperty("doc")
              ? [...new Set(lastActivityTextRows.map((r) => String(r.doc != null ? r.doc : "")))].filter(Boolean).sort()
              : []);
          docs.forEach((d) => {
            const opt = document.createElement("option");
            opt.value = d;
            opt.textContent = d;
            activityDocFilter.appendChild(opt);
          });
          activityDocFilter.onchange = () => {
            activityTextCurrentPage = 1;
            renderActivityTextTableWithPagination();
            refreshActivityTextDocPdfPreview();
          };
          if (docs.length > 0) {
            activityDocFilter.value = docs[0];
          } else if (activityDocFilterRow) {
            activityDocFilterRow.classList.add("hidden");
          }
          refreshActivityTextDocPdfPreview();
        }
        activityTextCurrentPage = 1;
        renderActivityTextTableWithPagination();
      } catch (e) {
        if (activitySummary) {
          activitySummary.classList.remove("hidden");
          activitySummary.textContent = tx("results.loadFail", { msg: e.message });
        }
        if (activityThead) activityThead.innerHTML = "";
        if (activityTbody) activityTbody.innerHTML = "";
        if (activityDocFilterRow) activityDocFilterRow.classList.add("hidden");
        if (activityPaginationRow) activityPaginationRow.classList.add("hidden");
        lastActivityTextRows = null;
        lastActivityTextOutputDir = null;
        if (activityTextDocPdfWrap) activityTextDocPdfWrap.classList.add("hidden");
        if (activityTextDocPdfIframe) {
          activityTextDocPdfIframe.classList.add("hidden");
          activityTextDocPdfIframe.removeAttribute("src");
        }
      } finally {
        setButtonLoading(btnLoadActivityText, false);
      }
    });
  }

  if (btnActivityFirstPage) {
    btnActivityFirstPage.addEventListener("click", () => {
      activityTextCurrentPage = 1;
      renderActivityTextTableWithPagination();
    });
  }
  if (btnActivityPrevPage) {
    btnActivityPrevPage.addEventListener("click", () => {
      activityTextCurrentPage--;
      renderActivityTextTableWithPagination();
    });
  }
  if (btnActivityNextPage) {
    btnActivityNextPage.addEventListener("click", () => {
      activityTextCurrentPage++;
      renderActivityTextTableWithPagination();
    });
  }
  if (btnActivityLastPage) {
    btnActivityLastPage.addEventListener("click", () => {
      const filtered = getActivityTextFilteredRows();
      const totalPages = Math.ceil(filtered.length / ACTIVITY_TEXT_PAGE_SIZE) || 1;
      activityTextCurrentPage = totalPages;
      renderActivityTextTableWithPagination();
    });
  }

  function buildDetectionQuery(dir, doc, page) {
    if (!dir || !doc || !page) return null;
    return { dir, doc, page };
  }

  function loadPageImageForDocPage(wrap, imgEl, dir, doc, page, placeholderDefault) {
    const defaultText = placeholderDefault || tx("markush.pagePdfDefault");
    if (!wrap || !imgEl) return;
    if (!dir || !doc || !page) {
      wrap.classList.add("hidden");
      wrap.classList.remove("page-image-loaded");
      imgEl.removeAttribute("src");
      imgEl.style.width = "";
      imgEl.style.height = "";
      imgEl.style.maxWidth = "";
      const ph = wrap.querySelector(".page-image-placeholder");
      if (ph) ph.textContent = defaultText;
      return;
    }
    wrap.classList.remove("hidden");
    wrap.classList.remove("page-image-loaded");
    const ph = wrap.querySelector(".page-image-placeholder");
    if (ph) ph.textContent = tx("common.pdfLoading");
    imgEl.removeAttribute("src");
    const url = "/api/page_image?output_dir=" + encodeURIComponent(dir) + "&doc=" + encodeURIComponent(doc) + "&page=" + encodeURIComponent(page);
    imgEl.onload = function () {
      wrap.classList.add("page-image-loaded");
      if (ph) ph.textContent = defaultText;
      if (typeof imgEl._onPageImageLoaded === "function") imgEl._onPageImageLoaded();
    };
    imgEl.onerror = function () {
      wrap.classList.remove("page-image-loaded");
      if (ph) ph.textContent = tx("markush.pageMissing");
    };
    imgEl.src = url;
  }

  /**
   * Full / Part Markush 左侧页图：md_merge_*_yolo_distinguish_full_markush_after_ocsr 下的
   * merge_full / merge_part 可视化 PNG（非 page_images 原页图）。
   * 注意：merge_part 仅在本页存在含 * 的 Part 结构时才会生成；否则接口 404 属正常。
   * @param {"full"|"part"} kind
   */
  function loadMarkushVizPageImage(wrap, imgEl, dir, doc, page, kind, placeholderDefault) {
    const k = kind === "part" ? "part" : "full";
    const defaultText =
      placeholderDefault ||
      (k === "part" ? tx("markush.partPlaceholder") : tx("markush.fullPlaceholder"));
    if (!wrap || !imgEl) return;
    if (!dir || !doc || !page) {
      wrap.classList.add("hidden");
      wrap.classList.remove("page-image-loaded");
      imgEl.removeAttribute("src");
      imgEl.style.width = "";
      imgEl.style.height = "";
      imgEl.style.maxWidth = "";
      const ph = wrap.querySelector(".page-image-placeholder");
      if (ph) ph.textContent = defaultText;
      return;
    }
    wrap.classList.remove("hidden");
    wrap.classList.remove("page-image-loaded");
    const ph = wrap.querySelector(".page-image-placeholder");
    if (ph) ph.textContent = tx("common.pdfLoading");
    imgEl.removeAttribute("src");
    const url =
      "/api/markush_viz_page_image?output_dir=" +
      encodeURIComponent(dir) +
      "&doc=" +
      encodeURIComponent(doc) +
      "&page=" +
      encodeURIComponent(page) +
      "&kind=" +
      encodeURIComponent(k);
    imgEl.onload = function () {
      wrap.classList.add("page-image-loaded");
      if (ph) ph.textContent = defaultText;
      if (typeof imgEl._onPageImageLoaded === "function") imgEl._onPageImageLoaded();
    };
    imgEl.onerror = function () {
      wrap.classList.remove("page-image-loaded");
      imgEl.removeAttribute("src");
      imgEl.style.width = "";
      imgEl.style.height = "";
      imgEl.style.maxWidth = "";
      if (ph) {
        ph.textContent = k === "part" ? tx("markush.noPartViz") : tx("markush.noFullViz");
      }
    };
    imgEl.src = url;
  }

  // 缩放控件绑定（Detection canvas）
  if (detectionZoomOut) detectionZoomOut.addEventListener("click", () => { detectionZoomMode = "manual"; detectionZoom = detectionZoom / 1.15; applyDetectionZoom(); });
  if (detectionZoomIn) detectionZoomIn.addEventListener("click", () => { detectionZoomMode = "manual"; detectionZoom = detectionZoom * 1.15; applyDetectionZoom(); });
  if (detectionZoomReset) detectionZoomReset.addEventListener("click", () => { detectionZoomMode = "manual"; detectionZoom = 1; applyDetectionZoom(); });
  if (detectionZoomFit) detectionZoomFit.addEventListener("click", () => { fitDetectionToWidth(); });

  // 缩放控件绑定（Markush Full image）
  if (markushPageImage) {
    markushPageImage._onPageImageLoaded = function () {
      if (markushZoomMode === "fit") markushZoom = fitImgToWidth(markushPageImage, markushPageImageWrap || markushPageImage.parentElement);
      applyImgZoom(markushPageImage, markushZoom, markushZoomLabel);
    };
  }
  if (markushZoomOut) markushZoomOut.addEventListener("click", () => { markushZoomMode = "manual"; markushZoom = markushZoom / 1.15; applyImgZoom(markushPageImage, markushZoom, markushZoomLabel); });
  if (markushZoomIn) markushZoomIn.addEventListener("click", () => { markushZoomMode = "manual"; markushZoom = markushZoom * 1.15; applyImgZoom(markushPageImage, markushZoom, markushZoomLabel); });
  if (markushZoomReset) markushZoomReset.addEventListener("click", () => { markushZoomMode = "manual"; markushZoom = 1; applyImgZoom(markushPageImage, markushZoom, markushZoomLabel); });
  if (markushZoomFit) markushZoomFit.addEventListener("click", () => { markushZoomMode = "fit"; markushZoom = fitImgToWidth(markushPageImage, markushPageImageWrap || markushPageImage.parentElement); applyImgZoom(markushPageImage, markushZoom, markushZoomLabel); });

  // 缩放控件绑定（Markush Part image）
  if (markushPartPageImage) {
    markushPartPageImage._onPageImageLoaded = function () {
      if (markushPartZoomMode === "fit") markushPartZoom = fitImgToWidth(markushPartPageImage, markushPartPageImageWrap || markushPartPageImage.parentElement);
      applyImgZoom(markushPartPageImage, markushPartZoom, markushPartZoomLabel);
    };
  }
  if (markushPartZoomOut) markushPartZoomOut.addEventListener("click", () => { markushPartZoomMode = "manual"; markushPartZoom = markushPartZoom / 1.15; applyImgZoom(markushPartPageImage, markushPartZoom, markushPartZoomLabel); });
  if (markushPartZoomIn) markushPartZoomIn.addEventListener("click", () => { markushPartZoomMode = "manual"; markushPartZoom = markushPartZoom * 1.15; applyImgZoom(markushPartPageImage, markushPartZoom, markushPartZoomLabel); });
  if (markushPartZoomReset) markushPartZoomReset.addEventListener("click", () => { markushPartZoomMode = "manual"; markushPartZoom = 1; applyImgZoom(markushPartPageImage, markushPartZoom, markushPartZoomLabel); });
  if (markushPartZoomFit) markushPartZoomFit.addEventListener("click", () => { markushPartZoomMode = "fit"; markushPartZoom = fitImgToWidth(markushPartPageImage, markushPartPageImageWrap || markushPartPageImage.parentElement); applyImgZoom(markushPartPageImage, markushPartZoom, markushPartZoomLabel); });

  // 缩放控件绑定（ActivityImage 页图）
  if (activityImagePageImage) {
    activityImagePageImage._onPageImageLoaded = function () {
      if (activityImageZoomMode === "fit") activityImageZoom = fitImgToWidth(activityImagePageImage, activityImageImageResultRow || activityImagePageImageWrap || activityImagePageImage.parentElement);
      applyImgZoom(activityImagePageImage, activityImageZoom, activityImageZoomLabel);
    };
  }
  if (activityImageZoomOut) activityImageZoomOut.addEventListener("click", () => { activityImageZoomMode = "manual"; activityImageZoom = activityImageZoom / 1.15; applyImgZoom(activityImagePageImage, activityImageZoom, activityImageZoomLabel); });
  if (activityImageZoomIn) activityImageZoomIn.addEventListener("click", () => { activityImageZoomMode = "manual"; activityImageZoom = activityImageZoom * 1.15; applyImgZoom(activityImagePageImage, activityImageZoom, activityImageZoomLabel); });
  if (activityImageZoomReset) activityImageZoomReset.addEventListener("click", () => { activityImageZoomMode = "manual"; activityImageZoom = 1; applyImgZoom(activityImagePageImage, activityImageZoom, activityImageZoomLabel); });
  if (activityImageZoomFit) activityImageZoomFit.addEventListener("click", () => { activityImageZoomMode = "fit"; activityImageZoom = fitImgToWidth(activityImagePageImage, activityImageImageResultRow || activityImagePageImageWrap || activityImagePageImage.parentElement); applyImgZoom(activityImagePageImage, activityImageZoom, activityImageZoomLabel); });

  window.addEventListener("resize", function () {
    if (detectionZoomMode === "fit") fitDetectionToWidth();
    if (markushZoomMode === "fit") {
      markushZoom = fitImgToWidth(markushPageImage, markushPageImageWrap || (markushPageImage && markushPageImage.parentElement));
      applyImgZoom(markushPageImage, markushZoom, markushZoomLabel);
    }
    if (markushPartZoomMode === "fit") {
      markushPartZoom = fitImgToWidth(markushPartPageImage, markushPartPageImageWrap || (markushPartPageImage && markushPartPageImage.parentElement));
      applyImgZoom(markushPartPageImage, markushPartZoom, markushPartZoomLabel);
    }
    if (activityImageZoomMode === "fit") {
      activityImageZoom = fitImgToWidth(activityImagePageImage, activityImageImageResultRow || activityImagePageImageWrap || (activityImagePageImage && activityImagePageImage.parentElement));
      applyImgZoom(activityImagePageImage, activityImageZoom, activityImageZoomLabel);
    }
  });

  function drawBboxesOnCanvas(ctx, bboxes, width, height, selectedIndex) {
    const lineWidth = Math.max(2, Math.min(width, height) / 400);
    const fontPx = Math.max(14, height / 40);
    ctx.font = "bold " + fontPx + "px sans-serif";
    bboxes.forEach(function (b) {
      const [x, y, w, h] = b.bbox;
      const px = x * width;
      const py = y * height;
      const pw = w * width;
      const ph = h * height;
      const isSelected = selectedIndex != null && b.index === selectedIndex;
      const molType = (b && b.mol_type != null) ? String(b.mol_type) : "";
      // 颜色规则：
      // - part -> 紫色
      // - invalid -> 灰色
      // - 其余（full/Markush）-> 红色
      const baseColor =
        molType === "part"
          ? "rgba(160, 32, 240, 0.95)"
          : (molType === "invalid" ? "rgba(140, 140, 140, 0.95)" : "rgba(255, 0, 0, 0.9)");
      ctx.strokeStyle = isSelected ? "rgba(255, 200, 0, 1)" : baseColor;
      ctx.lineWidth = isSelected ? lineWidth * 2.5 : lineWidth;
      ctx.strokeRect(px, py, pw, ph);
      ctx.fillStyle = "white";
      ctx.fillRect(px, py - 2, ctx.measureText(String(b.index)).width + 8, 22);
      ctx.fillStyle = isSelected ? "rgba(255, 200, 0, 1)" : baseColor;
      ctx.fillText(String(b.index), px + 4, py + 16);
    });
  }

  function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function renderDetectionBboxList(bboxes) {
    if (!detectionBboxList) return;
    bboxes = bboxes || [];
    detectionBboxList.innerHTML = "";
    const emptyHint = $("detectionBboxListEmptyHint");
    if (emptyHint) {
      emptyHint.classList.toggle("hidden", bboxes.length > 0);
    }
    bboxes.forEach(function (b) {
      const row = document.createElement("div");
      row.className = "detection-bbox-row";
      row.dataset.index = String(b.index);
      const smiles = b.smiles != null ? String(b.smiles) : "";
      const bboxStr = b.bbox.map(function (v) {
        return Number(v).toFixed(4);
      }).join(", ");
      row.innerHTML =
        "<span class=\"detection-row-index\">#" + escapeHtml(String(b.index)) + "</span>" +
        "page " + b.page +
        "<div class=\"detection-row-bbox\">bbox [" + escapeHtml(bboxStr) + "]</div>" +
        "<div class=\"detection-row-smiles\">" + escapeHtml(smiles) + "</div>";
      row.addEventListener("click", function () {
        setDetectionSelection(b.index);
      });
      detectionBboxList.appendChild(row);
    });
  }

  function setDetectionSelection(index) {
    selectedBboxIndex = index;
    if (detectionBboxListWrap && detectionKetcherCol) {
      detectionBboxListWrap.classList.toggle("hidden", index != null);
      detectionKetcherCol.classList.toggle("hidden", index == null);
    }
    if (detectionBboxCropWrap && detectionBboxCropImg) {
      if (index == null) {
        detectionBboxCropWrap.classList.add("hidden");
        detectionBboxCropImg.removeAttribute("src");
      } else {
        const qDir = lastDetectionOutputDir || (detectionOutputDir && detectionOutputDir.value ? detectionOutputDir.value.trim() : "");
        const qDoc = currentDetectionDoc || (detectionDocSelect && detectionDocSelect.value);
        const qPage = currentDetectionPage || (detectionPageSelect && detectionPageSelect.value);
        if (qDir && qDoc && qPage != null) {
          const url =
            "/api/detection_bbox_crop?output_dir=" + encodeURIComponent(qDir) +
            "&doc=" + encodeURIComponent(qDoc) +
            "&page=" + encodeURIComponent(String(qPage)) +
            "&index=" + encodeURIComponent(String(index));
          detectionBboxCropImg.src = url;
          detectionBboxCropWrap.classList.remove("hidden");
        } else {
          detectionBboxCropWrap.classList.add("hidden");
          detectionBboxCropImg.removeAttribute("src");
        }
      }
    }
    if (index != null) {
      const bboxItem = currentDetectionBboxes.find(function (b) {
        return b.index === index;
      });
      if (bboxItem && bboxItem.smiles != null && String(bboxItem.smiles).trim()) {
        if (typeof window.biominerKetcherSetMolecule === "function") {
          window.biominerKetcherSetMolecule(String(bboxItem.smiles).trim());
        }
      }
    }
    if (currentDetectionImage && currentDetectionCanvasW && currentDetectionCanvasH) {
      const ctx = detectionCanvas.getContext("2d");
      ctx.drawImage(currentDetectionImage, 0, 0);
      drawBboxesOnCanvas(ctx, currentDetectionBboxes, currentDetectionCanvasW, currentDetectionCanvasH, index);
    }
  }

  function refreshDetectionImage() {
    const q = buildDetectionQuery(
      lastDetectionOutputDir || detectionOutputDir.value.trim(),
      detectionDocSelect.value,
      detectionPageSelect.value
    );
    if (!q) {
      detectionImageWrap.classList.add("hidden");
      detectionPlaceholder.classList.remove("hidden");
      detectionCanvas.getContext("2d").clearRect(0, 0, detectionCanvas.width, detectionCanvas.height);
      currentDetectionBboxes = [];
      currentDetectionImage = null;
      selectedBboxIndex = null;
      if (detectionBboxListWrap && detectionKetcherCol) {
        detectionBboxListWrap.classList.remove("hidden");
        detectionKetcherCol.classList.add("hidden");
      }
      renderDetectionBboxList([]);
      return;
    }
    detectionPlaceholder.classList.add("hidden");
    detectionImageWrap.classList.remove("hidden");
    currentDetectionBboxes = [];
    currentDetectionDoc = q.doc;
    currentDetectionPage = q.page;
    selectedBboxIndex = null;

    const base = "/api/";
    const pageImageUrl = base + "page_image?output_dir=" + encodeURIComponent(q.dir) + "&doc=" + encodeURIComponent(q.doc) + "&page=" + encodeURIComponent(q.page);
    const bboxesUrl = base + "detection_bboxes?output_dir=" + encodeURIComponent(q.dir) + "&doc=" + encodeURIComponent(q.doc) + "&page=" + encodeURIComponent(q.page);

    if (lastDetectionImageBlobUrl) {
      URL.revokeObjectURL(lastDetectionImageBlobUrl);
      lastDetectionImageBlobUrl = null;
    }
    Promise.all([
      fetch(pageImageUrl).then(function (r) {
        if (!r.ok) throw new Error(tx("detection.pageImageFail"));
        return r.blob();
      }),
      fetch(bboxesUrl).then(function (r) {
        if (!r.ok) throw new Error(tx("detection.genericLoadFail"));
        return r.json();
      }),
    ])
      .then(function ([blob, data]) {
        currentDetectionBboxes = data.bboxes || [];
        renderDetectionBboxList(currentDetectionBboxes);
        setDetectionSelection(null);
        const img = new Image();
        img.onload = function () {
          const w = img.naturalWidth;
          const h = img.naturalHeight;
          detectionCanvas.width = w;
          detectionCanvas.height = h;
          currentDetectionCanvasW = w;
          currentDetectionCanvasH = h;
          currentDetectionImage = img;
          const ctx = detectionCanvas.getContext("2d");
          ctx.drawImage(img, 0, 0);
          drawBboxesOnCanvas(ctx, currentDetectionBboxes, w, h, null);
          if (detectionZoomMode === "fit") {
            fitDetectionToWidth();
          } else {
            applyDetectionZoom();
          }
          if (lastDetectionImageBlobUrl) URL.revokeObjectURL(lastDetectionImageBlobUrl);
          lastDetectionImageBlobUrl = img.src;
        };
        img.onerror = function () {
          alert(tx("detection.pageImageFail"));
        };
        img.src = URL.createObjectURL(blob);
      })
      .catch(function (e) {
        alert(e.message || tx("detection.genericLoadFail"));
      });

    detectionCanvas.onclick = function (e) {
      if (currentDetectionBboxes.length === 0) return;
      const rect = detectionCanvas.getBoundingClientRect();
      const normX = (e.clientX - rect.left) / rect.width;
      const normY = (e.clientY - rect.top) / rect.height;
      for (let i = 0; i < currentDetectionBboxes.length; i++) {
        const b = currentDetectionBboxes[i];
        const [x, y, w, h] = b.bbox;
        if (normX >= x && normX <= x + w && normY >= y && normY <= y + h) {
          setDetectionSelection(b.index);
          return;
        }
      }
      setDetectionSelection(null);
    };
  }

  if (detectionBackToBboxList) {
    detectionBackToBboxList.addEventListener("click", function () {
      setDetectionSelection(null);
    });
  }

  if (btnSaveSmiles) {
    btnSaveSmiles.addEventListener("click", async function () {
      if (selectedBboxIndex == null) {
        alert(tx("detection.alertSelectBbox"));
        return;
      }
      const dir = lastDetectionOutputDir || (detectionOutputDir && detectionOutputDir.value ? String(detectionOutputDir.value).trim() : "");
      const doc = currentDetectionDoc || (detectionDocSelect && detectionDocSelect.value);
      const page = currentDetectionPage != null ? currentDetectionPage : (detectionPageSelect && detectionPageSelect.value);
      if (!dir || !doc || page === null || page === undefined || page === "") {
        alert(tx("detection.alertLoadPageFirst"));
        return;
      }
      const smiles = smilesInput ? String(smilesInput.value || "").trim() : "";
      if (!smiles) {
        alert(tx("detection.smilesEmpty"));
        return;
      }

      setButtonLoading(btnSaveSmiles, true);
      try {
        await api("/api/detection_smiles_override_save", {
          method: "POST",
          json: true,
          body: JSON.stringify({
            output_dir: dir,
            doc: doc,
            page: page,
            bbox_index: selectedBboxIndex,
            smiles: smiles,
          }),
        });

        // 只刷新当前页 bbox 列表与画面（不重载图片 blob）
        const updated = await api(
          "/api/detection_bboxes?output_dir=" +
            encodeURIComponent(dir) +
            "&doc=" +
            encodeURIComponent(doc) +
            "&page=" +
            encodeURIComponent(String(page))
        );
        currentDetectionBboxes = updated.bboxes || [];
        renderDetectionBboxList(currentDetectionBboxes);
        setDetectionSelection(selectedBboxIndex);
      } catch (e) {
        let msg = e.message || String(e);
        try {
          const j = JSON.parse(msg);
          if (j && j.error) msg = j.error;
        } catch (_) { /* keep msg */ }
        alert(tx("save.failWithMsg", { msg }));
      } finally {
        setButtonLoading(btnSaveSmiles, false);
      }
    });
  }

  btnShowMolBbox.addEventListener("click", async () => {
    const dir = detectionOutputDir.value.trim() || resultsOutputDir.value.trim();
    if (!dir) {
      alert(tx("detection.needDirOrRun"));
      return;
    }
    setButtonLoading(btnShowMolBbox, true);
    if (detectionPlaceholder) {
      detectionPlaceholder.classList.remove("hidden");
      detectionPlaceholder.textContent = tx("common.loadingLong");
    }
    try {
      let data = await api("/api/detection_pages?output_dir=" + encodeURIComponent(dir));
      if (!data.doc_pages || Object.keys(data.doc_pages).length === 0) {
        const drawn = await api("/api/draw_detection_bbox", {
          method: "POST",
          json: true,
          body: JSON.stringify({ output_dir: dir }),
        });
        if (drawn.error) {
          alert(drawn.error);
          return;
        }
        data = { output_dir: drawn.output_dir, merge_dir: drawn.merge_dir, doc_pages: drawn.doc_pages || {} };
      }
      lastDetectionDocPages = data.doc_pages;
      lastDetectionOutputDir = data.output_dir;
      detectionOutputDir.value = data.output_dir;

      detectionDocPageRow.classList.remove("hidden");
      detectionDocSelect.innerHTML = '<option value="">' + escapeHtml(tx("detection.selectDocOption")) + "</option>";
      detectionPageSelect.innerHTML = '<option value="">' + escapeHtml(tx("detection.selectPageOption")) + "</option>";
      const docNames = Object.keys(data.doc_pages || {}).sort();
      docNames.forEach((name) => {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        detectionDocSelect.appendChild(opt);
      });

      function onDocChange() {
        const name = detectionDocSelect.value;
        const pages = (lastDetectionDocPages && lastDetectionDocPages[name]) || [];
        detectionPageSelect.innerHTML = '<option value="">' + escapeHtml(tx("detection.selectPageOption")) + "</option>";
        pages.forEach((p) => {
          const opt = document.createElement("option");
          opt.value = String(p);
          opt.textContent = tx("detection.pageN", { n: p });
          detectionPageSelect.appendChild(opt);
        });
        refreshDetectionImage();
      }
      detectionDocSelect.onchange = onDocChange;
      detectionPageSelect.onchange = refreshDetectionImage;
      onDocChange();
      if (docNames.length > 0) detectionDocSelect.value = docNames[0];
      onDocChange();
      if (detectionPageSelect.options.length > 1) detectionPageSelect.value = detectionPageSelect.options[1].value;
      refreshDetectionImage();
    } catch (e) {
      alert(tx("detection.loadDrawFail", { msg: e.message }));
      if (detectionPlaceholder) detectionPlaceholder.textContent = tx("detection.placeholderAfterFail");
    } finally {
      setButtonLoading(btnShowMolBbox, false);
    }
  });

  function refreshMarkushPageData() {
    const dir = lastMarkushOutputDir || (markushOutputDir && markushOutputDir.value.trim());
    const doc = markushDocSelect && markushDocSelect.value;
    const page = markushPageSelect && markushPageSelect.value;
    if (markushFullCorefHint) {
      markushFullCorefHint.classList.add("hidden");
      markushFullCorefHint.textContent = "";
      markushFullCorefHint.classList.remove("markush-coref-hint--ok");
    }
    loadMarkushVizPageImage(markushPageImageWrap, markushPageImage, dir, doc, page, "full");
    if (!dir || !doc || !page) {
      if (markushContent) markushContent.classList.add("hidden");
      if (markushPlaceholder) {
        markushPlaceholder.classList.remove("hidden");
        markushPlaceholder.textContent = tx("markush.selectDocPagePrompt");
      }
      return;
    }
    markushPlaceholder.classList.remove("hidden");
    markushPlaceholder.textContent = tx("common.pdfLoading");
    markushContent.classList.add("hidden");
    const url = "/api/markush_page_data?output_dir=" + encodeURIComponent(dir) + "&doc=" + encodeURIComponent(doc) + "&page=" + encodeURIComponent(page);
    fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error(tx("markush.loadPageDataFail"));
        return r.json();
      })
      .then(function (data) {
        if (data.full && data.full.coreference != null) {
          markushFullDetails.classList.remove("hidden");
          if (markushFullCoref) {
            try {
              markushFullCoref.value = formatCoreference(data.full.coreference);
            } catch (e) {
              markushFullCoref.value = String(data.full.coreference);
            }
          }
          markushContent.classList.remove("hidden");
          markushPlaceholder.classList.add("hidden");
        } else {
          markushFullDetails.classList.add("hidden");
          if (markushFullCoref) markushFullCoref.value = "";
          markushContent.classList.add("hidden");
          markushPlaceholder.classList.remove("hidden");
          markushPlaceholder.textContent = data.full ? tx("markush.noCoref") : tx("markush.noFullFile");
        }
      })
      .catch(function (e) {
        markushContent.classList.add("hidden");
        markushPlaceholder.classList.remove("hidden");
        markushPlaceholder.textContent = tx("markush.loadFailWithMsg", {
          msg: e.message || tx("error.unknown"),
        });
      });
  }

  if (btnSaveMarkushFullCoref && markushFullCoref) {
    btnSaveMarkushFullCoref.addEventListener("click", async function () {
      const dir = lastMarkushOutputDir || (markushOutputDir && markushOutputDir.value.trim());
      const doc = markushDocSelect && markushDocSelect.value;
      const page = markushPageSelect && markushPageSelect.value;
      if (!dir || !doc || !page) {
        alert(tx("markush.needDirDocPage"));
        return;
      }
      let parsed;
      try {
        parsed = JSON.parse(markushFullCoref.value);
      } catch (e) {
        alert(tx("markush.invalidJson", { msg: e.message || e }));
        return;
      }
      setButtonLoading(btnSaveMarkushFullCoref, true);
      try {
        const out = await api("/api/markush_coreference_save", {
          method: "POST",
          json: true,
          body: JSON.stringify({
            output_dir: dir,
            doc: doc,
            page: page,
            kind: "full",
            content: parsed,
          }),
        });
        if (out && out.backup) {
          if (markushFullCorefHint) {
            markushFullCorefHint.textContent = tx("markush.saveBackup", { path: out.backup });
            markushFullCorefHint.classList.add("markush-coref-hint--ok");
            markushFullCorefHint.classList.remove("hidden");
          }
        } else if (markushFullCorefHint) {
          markushFullCorefHint.textContent = tx("markush.saveNoBackup");
          markushFullCorefHint.classList.add("markush-coref-hint--ok");
          markushFullCorefHint.classList.remove("hidden");
        }
        markushFullCoref.value = formatCoreference(parsed);
      } catch (e) {
        let msg = e.message || String(e);
        try {
          const j = JSON.parse(msg);
          if (j && j.error) msg = j.error;
        } catch (_) { /* keep msg */ }
        alert(tx("save.failWithMsg", { msg }));
      } finally {
        setButtonLoading(btnSaveMarkushFullCoref, false);
      }
    });
  }

  function refreshMarkushPartPageData() {
    const dir = lastMarkushPartOutputDir || (markushPartOutputDir && markushPartOutputDir.value.trim());
    const doc = markushPartDocSelect && markushPartDocSelect.value;
    const page = markushPartPageSelect && markushPartPageSelect.value;
    if (markushPartCorefHint) {
      markushPartCorefHint.classList.add("hidden");
      markushPartCorefHint.textContent = "";
      markushPartCorefHint.classList.remove("markush-coref-hint--ok");
    }
    loadMarkushVizPageImage(markushPartPageImageWrap, markushPartPageImage, dir, doc, page, "part");
    if (!dir || !doc || !page) {
      if (markushPartContent) markushPartContent.classList.add("hidden");
      if (markushPartPlaceholder) {
        markushPartPlaceholder.classList.remove("hidden");
        markushPartPlaceholder.textContent = tx("markush.selectDocPagePrompt");
      }
      return;
    }
    markushPartPlaceholder.classList.remove("hidden");
    markushPartPlaceholder.textContent = tx("common.pdfLoading");
    markushPartContent.classList.add("hidden");
    const url = "/api/markush_page_data?output_dir=" + encodeURIComponent(dir) + "&doc=" + encodeURIComponent(doc) + "&page=" + encodeURIComponent(page);
    fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error(tx("markush.loadPageDataFail"));
        return r.json();
      })
      .then(function (data) {
        if (data.part && data.part.coreference != null) {
          markushPartDetails.classList.remove("hidden");
          if (markushPartCoref) {
            try {
              markushPartCoref.value = formatCoreference(data.part.coreference);
            } catch (e) {
              markushPartCoref.value = String(data.part.coreference);
            }
          }
          markushPartContent.classList.remove("hidden");
          markushPartPlaceholder.classList.add("hidden");
        } else {
          markushPartDetails.classList.add("hidden");
          if (markushPartCoref) markushPartCoref.value = "";
          markushPartContent.classList.add("hidden");
          markushPartPlaceholder.classList.remove("hidden");
          markushPartPlaceholder.textContent = data.part ? tx("markush.noCoref") : tx("markush.noPartFile");
        }
      })
      .catch(function (e) {
        markushPartContent.classList.add("hidden");
        markushPartPlaceholder.classList.remove("hidden");
        markushPartPlaceholder.textContent = tx("markush.loadFailWithMsg", {
          msg: e.message || tx("error.unknown"),
        });
      });
  }

  if (btnSaveMarkushPartCoref && markushPartCoref) {
    btnSaveMarkushPartCoref.addEventListener("click", async function () {
      const dir = lastMarkushPartOutputDir || (markushPartOutputDir && markushPartOutputDir.value.trim());
      const doc = markushPartDocSelect && markushPartDocSelect.value;
      const page = markushPartPageSelect && markushPartPageSelect.value;
      if (!dir || !doc || !page) {
        alert(tx("markush.needDirDocPage"));
        return;
      }
      let parsed;
      try {
        parsed = JSON.parse(markushPartCoref.value);
      } catch (e) {
        alert(tx("markush.invalidJson", { msg: e.message || e }));
        return;
      }
      setButtonLoading(btnSaveMarkushPartCoref, true);
      try {
        const out = await api("/api/markush_coreference_save", {
          method: "POST",
          json: true,
          body: JSON.stringify({
            output_dir: dir,
            doc: doc,
            page: page,
            kind: "part",
            content: parsed,
          }),
        });
        if (out && out.backup) {
          if (markushPartCorefHint) {
            markushPartCorefHint.textContent = tx("markush.saveBackup", { path: out.backup });
            markushPartCorefHint.classList.add("markush-coref-hint--ok");
            markushPartCorefHint.classList.remove("hidden");
          }
        } else if (markushPartCorefHint) {
          markushPartCorefHint.textContent = tx("markush.saveNoBackup");
          markushPartCorefHint.classList.add("markush-coref-hint--ok");
          markushPartCorefHint.classList.remove("hidden");
        }
        markushPartCoref.value = formatCoreference(parsed);
      } catch (e) {
        let msg = e.message || String(e);
        try {
          const j = JSON.parse(msg);
          if (j && j.error) msg = j.error;
        } catch (_) { /* keep msg */ }
        alert(tx("save.failWithMsg", { msg }));
      } finally {
        setButtonLoading(btnSaveMarkushPartCoref, false);
      }
    });
  }

  if (btnLoadMarkush) {
    btnLoadMarkush.addEventListener("click", async function () {
      const dir = (markushOutputDir && markushOutputDir.value) ? String(markushOutputDir.value).trim() : "";
      if (!dir) {
        alert(tx("common.fillResultDir"));
        return;
      }
      setButtonLoading(btnLoadMarkush, true);
      if (markushPlaceholder) {
        markushPlaceholder.classList.remove("hidden");
        markushPlaceholder.textContent = tx("common.loadingLong");
      }
      try {
        const data = await api("/api/markush_pages?output_dir=" + encodeURIComponent(dir));
        const mapFull =
          data.doc_pages_full && Object.keys(data.doc_pages_full).length > 0 ? data.doc_pages_full : data.doc_pages || {};
        const docsFull = Object.keys(mapFull).sort();
        if (!docsFull.length) {
          if (markushDocPageRow) markushDocPageRow.classList.add("hidden");
          if (markushImageResultRow) markushImageResultRow.classList.add("hidden");
          if (markushContent) markushContent.classList.add("hidden");
          loadMarkushVizPageImage(markushPageImageWrap, markushPageImage, "", "", "", "full");
          if (markushPlaceholder) {
            markushPlaceholder.classList.remove("hidden");
            markushPlaceholder.textContent = data.message || tx("markush.notFound");
          }
          return;
        }
        lastMarkushDocPages = mapFull;
        lastMarkushOutputDir = data.output_dir;
        if (markushOutputDir) markushOutputDir.value = data.output_dir;
        if (markushDocPageRow) markushDocPageRow.classList.remove("hidden");
        if (markushImageResultRow) markushImageResultRow.classList.remove("hidden");
        if (markushDocSelect) {
          markushDocSelect.innerHTML = "<option value=\"\">" + escapeHtml(tx("detection.selectDocOption")) + "</option>";
          docsFull.forEach(function (name) {
            const opt = document.createElement("option");
            opt.value = name;
            opt.textContent = name;
            markushDocSelect.appendChild(opt);
          });
        }
        function onMarkushDocChange() {
          const name = markushDocSelect ? markushDocSelect.value : "";
          const pages = (lastMarkushDocPages && name && lastMarkushDocPages[name]) || [];
          if (markushPageSelect) {
            markushPageSelect.innerHTML = "<option value=\"\">" + escapeHtml(tx("detection.selectPageOption")) + "</option>";
            pages.forEach(function (p) {
              const opt = document.createElement("option");
              opt.value = String(p);
              opt.textContent = tx("detection.pageN", { n: p });
              markushPageSelect.appendChild(opt);
            });
          }
          refreshMarkushPageData();
        }
        if (markushDocSelect) markushDocSelect.onchange = onMarkushDocChange;
        if (markushPageSelect) markushPageSelect.onchange = refreshMarkushPageData;
        onMarkushDocChange();
        if (docsFull.length > 0 && markushDocSelect) markushDocSelect.value = docsFull[0];
        onMarkushDocChange();
        if (markushPageSelect && markushPageSelect.options.length > 1) markushPageSelect.value = markushPageSelect.options[1].value;
        refreshMarkushPageData();
      } catch (e) {
        alert(tx("markush.loadPagesFail", { msg: e.message }));
        if (markushPlaceholder) markushPlaceholder.textContent = tx("markush.waitLoadHint");
      } finally {
        setButtonLoading(btnLoadMarkush, false);
      }
    });
  }

  if (btnLoadMarkushPart) {
    btnLoadMarkushPart.addEventListener("click", async function () {
      const dir = (markushPartOutputDir && markushPartOutputDir.value) ? String(markushPartOutputDir.value).trim() : "";
      if (!dir) {
        alert(tx("common.fillResultDir"));
        return;
      }
      setButtonLoading(btnLoadMarkushPart, true);
      if (markushPartPlaceholder) {
        markushPartPlaceholder.classList.remove("hidden");
        markushPartPlaceholder.textContent = tx("common.loadingLong");
      }
      try {
        const data = await api("/api/markush_pages?output_dir=" + encodeURIComponent(dir));
        const mapPart = data.doc_pages_part || {};
        const docsPart = Object.keys(mapPart).sort();
        if (!data.docs || data.docs.length === 0) {
          if (markushPartDocPageRow) markushPartDocPageRow.classList.add("hidden");
          if (markushPartImageResultRow) markushPartImageResultRow.classList.add("hidden");
          if (markushPartContent) markushPartContent.classList.add("hidden");
          loadMarkushVizPageImage(markushPartPageImageWrap, markushPartPageImage, "", "", "", "part");
          if (markushPartPlaceholder) {
            markushPartPlaceholder.classList.remove("hidden");
            markushPartPlaceholder.textContent = data.message || tx("markush.notFound");
          }
          return;
        }
        if (!docsPart.length) {
          if (markushPartDocPageRow) markushPartDocPageRow.classList.add("hidden");
          if (markushPartImageResultRow) markushPartImageResultRow.classList.add("hidden");
          if (markushPartContent) markushPartContent.classList.add("hidden");
          loadMarkushVizPageImage(markushPartPageImageWrap, markushPartPageImage, "", "", "", "part");
          if (markushPartPlaceholder) {
            markushPartPlaceholder.classList.remove("hidden");
            markushPartPlaceholder.textContent = tx("markush.partNoPartPages");
          }
          return;
        }
        lastMarkushPartDocPages = mapPart;
        lastMarkushPartOutputDir = data.output_dir;
        if (markushPartOutputDir) markushPartOutputDir.value = data.output_dir;
        if (markushPartDocPageRow) markushPartDocPageRow.classList.remove("hidden");
        if (markushPartImageResultRow) markushPartImageResultRow.classList.remove("hidden");
        if (markushPartDocSelect) {
          markushPartDocSelect.innerHTML = "<option value=\"\">" + escapeHtml(tx("detection.selectDocOption")) + "</option>";
          docsPart.forEach(function (name) {
            const opt = document.createElement("option");
            opt.value = name;
            opt.textContent = name;
            markushPartDocSelect.appendChild(opt);
          });
        }
        function onMarkushPartDocChange() {
          const name = markushPartDocSelect ? markushPartDocSelect.value : "";
          const pages = (lastMarkushPartDocPages && name && lastMarkushPartDocPages[name]) || [];
          if (markushPartPageSelect) {
            markushPartPageSelect.innerHTML = "<option value=\"\">" + escapeHtml(tx("detection.selectPageOption")) + "</option>";
            pages.forEach(function (p) {
              const opt = document.createElement("option");
              opt.value = String(p);
              opt.textContent = tx("detection.pageN", { n: p });
              markushPartPageSelect.appendChild(opt);
            });
          }
          refreshMarkushPartPageData();
        }
        if (markushPartDocSelect) markushPartDocSelect.onchange = onMarkushPartDocChange;
        if (markushPartPageSelect) markushPartPageSelect.onchange = refreshMarkushPartPageData;
        onMarkushPartDocChange();
        if (docsPart.length > 0 && markushPartDocSelect) markushPartDocSelect.value = docsPart[0];
        onMarkushPartDocChange();
        if (markushPartPageSelect && markushPartPageSelect.options.length > 1) markushPartPageSelect.value = markushPartPageSelect.options[1].value;
        refreshMarkushPartPageData();
      } catch (e) {
        alert(tx("markush.loadPagesFail", { msg: e.message }));
        if (markushPartPlaceholder) markushPartPlaceholder.textContent = tx("markush.waitLoadHint");
      } finally {
        setButtonLoading(btnLoadMarkushPart, false);
      }
    });
  }

  function renderActivityImageTable(rows) {
    activityImageThead.innerHTML = "";
    activityImageTbody.innerHTML = "";
    if (!rows || rows.length === 0) {
      const th = document.createElement("th");
      th.textContent = tx("activityImg.resultCol");
      activityImageThead.appendChild(th);
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.textContent = tx("activityImg.noDataRow");
      tr.appendChild(td);
      activityImageTbody.appendChild(tr);
      return;
    }
    const hiddenCols = new Set(["source_idx", "source_suffix", "row_id"]);
    const headers = Object.keys(rows[0]).filter((h) => !hiddenCols.has(h));
    headers.forEach((h) => {
      const th = document.createElement("th");
      th.textContent = h;
      activityImageThead.appendChild(th);
    });
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      headers.forEach((h) => {
        const td = document.createElement("td");
        // page_index 是 UI 额外字段，不一定在原 CSV 中；这里不参与保存（只显示）
        if (h === "page_index") {
          td.textContent = row[h] != null ? String(row[h]) : "";
        } else {
          const input = document.createElement("input");
          input.type = "text";
          input.className = "results-edit-input";
          input.value = row[h] != null ? String(row[h]) : "";
          const key =
            String(row.source_idx != null ? row.source_idx : "") +
            "__" +
            String(row.source_suffix != null ? row.source_suffix : "") +
            "__" +
            String(row.row_id != null ? row.row_id : "") +
            "__" +
            String(h);
          input.addEventListener("input", () => {
            activityImageEdits.set(key, {
              doc: activityDocSelect ? activityDocSelect.value : "",
              source_idx: row.source_idx,
              source_suffix: row.source_suffix,
              row_id: row.row_id,
              column: h,
              value: input.value,
            });
          });
          td.appendChild(input);
        }
        tr.appendChild(td);
      });
      activityImageTbody.appendChild(tr);
    });
  }

  function refreshActivityImagePage() {
    const dir = lastActivityImageOutputDir || (activityImageOutputDir && activityImageOutputDir.value.trim());
    const doc = activityDocSelect && activityDocSelect.value;
    if (!dir || !doc) {
      if (activityImagePageImageWrap) activityImagePageImageWrap.classList.add("hidden");
      if (activityImageDocPdfIframe) {
        activityImageDocPdfIframe.classList.add("hidden");
        activityImageDocPdfIframe.removeAttribute("src");
      }
      if (activityImageDocPdfPlaceholder) {
        activityImageDocPdfPlaceholder.textContent = tx("activityImg.pdfSelectDoc");
      }
      activityImageThead.innerHTML = "";
      activityImageTbody.innerHTML = "";
      activityImagePlaceholder.classList.remove("hidden");
      activityImagePlaceholder.textContent = tx("activityImg.pickDocOrEmpty");
      return;
    }

    // 左侧：直接预览该文档 PDF（与 page 无关）
    if (activityImagePageImageWrap) activityImagePageImageWrap.classList.remove("hidden");
    if (activityImagePageImageWrap) activityImagePageImageWrap.classList.remove("page-image-loaded");
    if (activityImageDocPdfPlaceholder) {
      activityImageDocPdfPlaceholder.textContent = tx("common.pdfLoading");
    }
    if (activityImageDocPdfIframe) {
      activityImageDocPdfIframe.classList.remove("hidden");
      activityImageDocPdfIframe.onload = function () {
        if (activityImagePageImageWrap) activityImagePageImageWrap.classList.add("page-image-loaded");
        if (activityImageDocPdfPlaceholder) activityImageDocPdfPlaceholder.textContent = "";
      };
      activityImageDocPdfIframe.src =
        "/api/activity_doc_pdf?output_dir=" + encodeURIComponent(dir) + "&doc=" + encodeURIComponent(doc);
    }

    activityImagePlaceholder.classList.add("hidden");

    const url =
      "/api/activity_doc_all_data?output_dir=" +
      encodeURIComponent(dir) +
      "&doc=" +
      encodeURIComponent(doc);

    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(tx("activityImg.fetchFail"));
        return r.json();
      })
      .then((data) => {
        renderActivityImageTable(data.rows || []);
      })
      .catch((e) => {
        activityImagePlaceholder.classList.remove("hidden");
        activityImagePlaceholder.textContent = tx("activityImg.loadFailWithMsg", {
          msg: e.message || tx("error.unknown"),
        });
        activityImageThead.innerHTML = "";
        activityImageTbody.innerHTML = "";
      });
  }

  if (btnLoadActivityImage) {
    btnLoadActivityImage.addEventListener("click", async () => {
      const dir = (activityImageOutputDir && activityImageOutputDir.value) ? String(activityImageOutputDir.value).trim() : "";
      if (!dir) {
        alert(tx("common.fillResultDir"));
        return;
      }
      setButtonLoading(btnLoadActivityImage, true);
      if (activityImagePlaceholder) {
        activityImagePlaceholder.classList.remove("hidden");
        activityImagePlaceholder.textContent = tx("common.loadingLong");
      }
      try {
        const data = await api("/api/activity_image_pages?output_dir=" + encodeURIComponent(dir));
        if (!data.docs || data.docs.length === 0) {
          if (activityDocPageRow) activityDocPageRow.classList.add("hidden");
          if (activityImageImageResultRow) activityImageImageResultRow.classList.add("hidden");
          if (activityImagePageImageWrap) activityImagePageImageWrap.classList.add("hidden");
          if (activityImageDocPdfIframe) {
            activityImageDocPdfIframe.classList.add("hidden");
            activityImageDocPdfIframe.removeAttribute("src");
          }
          if (activityImagePlaceholder) {
            activityImagePlaceholder.classList.remove("hidden");
            activityImagePlaceholder.textContent = data.message || tx("activityImg.notFoundRun");
          }
          if (activityImageThead) activityImageThead.innerHTML = "";
          if (activityImageTbody) activityImageTbody.innerHTML = "";
          return;
        }
        lastActivityImageDocPages = data.doc_pages;
        lastActivityImageOutputDir = data.output_dir;
        if (activityImageOutputDir) activityImageOutputDir.value = data.output_dir;
        if (activityDocPageRow) activityDocPageRow.classList.remove("hidden");
        if (activityImageImageResultRow) activityImageImageResultRow.classList.remove("hidden");
        if (activityDocSelect) {
          activityDocSelect.innerHTML = "<option value=\"\">" + escapeHtml(tx("detection.selectDocOption")) + "</option>";
          data.docs.forEach((name) => {
            const opt = document.createElement("option");
            opt.value = name;
            opt.textContent = name;
            activityDocSelect.appendChild(opt);
          });
        }
        function onActivityDocChange() {
          refreshActivityImagePage();
        }
        if (activityDocSelect) activityDocSelect.onchange = onActivityDocChange;
        if (data.docs.length > 0 && activityDocSelect) activityDocSelect.value = data.docs[0];
        onActivityDocChange();
      } catch (e) {
        alert(tx("activityImg.loadPagesFail", { msg: e.message }));
        if (activityImagePlaceholder) activityImagePlaceholder.textContent = tx("activityImg.waitHint");
      } finally {
        setButtonLoading(btnLoadActivityImage, false);
      }
    });
  }

  // 保存：文本活性抽取结果（value）
  if (btnSaveActivityTextEdits) {
    btnSaveActivityTextEdits.addEventListener("click", async () => {
      const outDir =
        lastActivityTextOutputDir || (activityOutputDir && activityOutputDir.value ? String(activityOutputDir.value).trim() : "");
      if (!outDir) {
        alert(tx("alert.needActivityDir"));
        return;
      }
      if (!activityTextEdits || activityTextEdits.size === 0) {
        alert(tx("alert.noEdits"));
        return;
      }
      setButtonLoading(btnSaveActivityTextEdits, true);
      try {
        const edits = Array.from(activityTextEdits.values());
        const res = await api("/api/activity_text_overrides_save", {
          method: "POST",
          json: true,
          body: JSON.stringify({ output_dir: outDir, edits: edits }),
        });
        if (res && res.ok) {
          activityTextEdits = new Map();
          // 重新加载表格数据（保持当前 doc 过滤）
          const data = await api("/api/activity_text?output_dir=" + encodeURIComponent(outDir));
          lastActivityTextRows = data.rows || [];
          lastActivityTextOutputDir = data.output_dir || outDir;
          activityTextCurrentPage = 1;
          renderActivityTextTableWithPagination();
          alert(tx("alert.savedOk"));
        } else {
          alert((res && res.error) || tx("alert.saveFailGeneric"));
        }
      } catch (e) {
        let msg = e.message || String(e);
        try {
          const j = JSON.parse(msg);
          if (j && j.error) msg = j.error;
        } catch (_) { /* keep */ }
        alert(tx("save.failWithMsg", { msg }));
      } finally {
        setButtonLoading(btnSaveActivityTextEdits, false);
      }
    });
  }

  // 保存：图表活性抽取结果（value）
  if (btnSaveActivityImageEdits) {
    btnSaveActivityImageEdits.addEventListener("click", async () => {
      const outDir =
        lastActivityImageOutputDir || (activityImageOutputDir && activityImageOutputDir.value ? String(activityImageOutputDir.value).trim() : "");
      const doc = activityDocSelect && activityDocSelect.value;
      if (!outDir || !doc) {
        alert(tx("alert.needLoadImageDoc"));
        return;
      }
      if (!activityImageEdits || activityImageEdits.size === 0) {
        alert(tx("alert.noEdits"));
        return;
      }
      setButtonLoading(btnSaveActivityImageEdits, true);
      try {
        const edits = Array.from(activityImageEdits.values());
        const res = await api("/api/activity_image_overrides_save", {
          method: "POST",
          json: true,
          body: JSON.stringify({ output_dir: outDir, edits: edits }),
        });
        if (res && res.ok) {
          activityImageEdits = new Map();
          refreshActivityImagePage();
          alert(tx("alert.savedOk"));
        } else {
          alert((res && res.error) || tx("alert.saveFailGeneric"));
        }
      } catch (e) {
        let msg = e.message || String(e);
        try {
          const j = JSON.parse(msg);
          if (j && j.error) msg = j.error;
        } catch (_) { /* keep */ }
        alert(tx("save.failWithMsg", { msg }));
      } finally {
        setButtonLoading(btnSaveActivityImageEdits, false);
      }
    });
  }

  function refreshDynamicUiAfterLangChange() {
    renderResultsTableWithPagination();
    if (lastResultsRows !== null && resultsSummary) {
      const dir = resultsOutputDir ? resultsOutputDir.value.trim() : "";
      resultsSummary.textContent = tx("results.summary", {
        dir,
        total: lastResultsRows.length,
        size: RESULTS_PAGE_SIZE,
      });
    }
    renderGivenStructureTableWithPagination();
    if (lastGivenStructureRows !== null && givenStructureSummary) {
      const dir = givenStructureOutputDir ? givenStructureOutputDir.value.trim() : "";
      givenStructureSummary.textContent = tx("results.summary", {
        dir,
        total: lastGivenStructureRows.length,
        size: GIVEN_STRUCTURE_PAGE_SIZE,
      });
    }
    renderActivityTextTableWithPagination();
    if (lastActivityTextRows !== null && activitySummary) {
      const dir = lastActivityTextOutputDir || "";
      activitySummary.textContent = tx("activity.summary", {
        dir,
        total: lastActivityTextRows.length,
        size: ACTIVITY_TEXT_PAGE_SIZE,
      });
    }
    if (lastGivenStructureKetcherRow) {
      const ov = $("givenStructureKetcherOverlay");
      if (ov && !ov.classList.contains("hidden")) {
        fillGivenStructureKetcherHint(lastGivenStructureKetcherRow);
      }
    }
    updatePdfFileNameDisplay();
  }

  document.addEventListener("biominer:langchange", refreshDynamicUiAfterLangChange);
  updatePdfFileNameDisplay();
})();
