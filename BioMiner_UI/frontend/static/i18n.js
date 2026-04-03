/**
 * BioMiner UI 中英文切换（静态文案 + app.js 通过 BioMinerI18n.t 调用）
 */
(function () {
  const STORAGE_KEY = "biominer_lang";

  const STRINGS = {
    zh: {
      "meta.pageTitle": "BioMiner 交互式界面",
      "header.subtitle": "从文献中自动挖掘蛋白-配体生物活性数据",
      "nav.tablist": "功能切换",
      "nav.input": "输入",
      "nav.run": "运行推理",
      "nav.detection": "化学结构识别",
      "nav.markushFull": "Full 分子结构",
      "nav.markushPart": "Part Markush",
      "nav.activityText": "文本活性抽取",
      "nav.activityImage": "图表活性抽取",
      "nav.activityGivenStructure": "结构条件活性抽取",
      "nav.results": "结果预览",
      "lang.label": "语言",
      "lang.zh": "中文",
      "lang.en": "English",

      "input.h1pdf": "1. 输入 PDF",
      "input.pdfPath": "PDF 路径（相对项目根）",
      "input.useExample": "使用示例",
      "input.uploadPdf": "或上传 PDF 文件",
      "input.chooseFile": "选择文件",
      "input.noFileSelected": "未选择任何文件",
      "input.previewPdf": "预览 PDF",
      "input.placeholderPreview": "选择或输入 PDF 路径后点击「预览 PDF」",
      "input.h2out": "2. 输出与配置",
      "input.outputDir": "输出目录（相对项目根）",
      "input.configPath": "配置文件路径",
      "input.apiSummary": "API 配置（使用闭源 MLLM 时填写）",
      "input.loadConfig": "从配置文件加载",
      "input.saveConfig": "保存到配置文件",

      "run.title": "运行推理",
      "run.hint": "请确保已按 README 启动 mineru_server、moldet_server、ocsr_server；使用 BioMiner-Instruct 时还需启动 vllm 服务。",
      "run.btn": "运行 BioMiner",
      "run.jobId": "任务 ID:",
      "run.status": "状态:",
      "run.refresh": "刷新状态",

      "detection.title": "化学结构识别",
      "detection.hint": "运行完样例后，点击「展示分子检测框」从 stage_one.pkl 加载页图与 bboxes_with_pred_smiless，在画布上绘制；点击图中分子框可查看 page、index、bbox、smiles。",
      "detection.resultDir": "结果目录（与上面一致）",
      "detection.showBbox": "展示分子检测框",
      "detection.docPage": "文档 / 页码",
      "detection.selectDoc": "选择文档",
      "detection.selectPage": "选择页码",
      "detection.zoomAria": "页图缩放",
      "detection.zoomOut": "缩小",
      "detection.zoomIn": "放大",
      "detection.zoomReset": "重置为 100%",
      "detection.zoomFit": "适配当前列宽",
      "detection.zoomFitBtn": "适配宽度",
      "detection.bboxListEmpty": "当前页无分子框",
      "detection.canvasAria": "页图与分子框",
      "detection.bboxListTitle": "所有框的基本信息",
      "detection.backList": "返回「所有框的基本信息」",
      "detection.cropTitle": "分子框原图",
      "detection.draw": "绘制",
      "detection.saveSmiles": "保存SMILES",
      "detection.ketcherTitle": "Ketcher 分子编辑器",
      "detection.placeholder": "请先点击「展示分子检测框」加载页图与分子框（点击框可在右侧查看结构）。",

      "markushFull.title": "Full 数据（完整分子结构）",
      "markushFull.hint": "运行推理后，从结果目录加载分子指代与 Markush 抽取结果，按页分开展示完整分子结构（Full）数据。",
      "markushFull.hiddenDir": "结果目录（与运行推理输出目录一致）",
      "markushFull.load": "加载分子指代/Markush 结果",
      "markushFull.placeholder": "选择文档与页码后显示 Full 可视化（md_merge_*_yolo_distinguish_full_markush_after_ocsr）",
      "markushFull.pageImgAlt": "Full 分子可视化页图",
      "markushFull.pageScrollAria": "Full 可视化页图",
      "markushFull.corefLabel": "指代 (coreference)",
      "markushFull.saveCoref": "保存指代",
      "markushFull.corefAria": "指代 coreference JSON 编辑",
      "markushFull.wait": "请先点击「加载分子指代/Markush 结果」并选择文档与页码。",

      "markushPart.title": "Part 数据（Markush scaffold/取代基）",
      "markushPart.hint": "运行推理后，从结果目录加载分子指代与 Markush 抽取结果，按页分开展示 Part（scaffold/取代基）数据。",
      "markushPart.placeholder": "选择文档与页码后显示 Part Markush 可视化（md_merge_*_yolo_distinguish_full_markush_after_ocsr）",
      "markushPart.pageImgAlt": "Part Markush 可视化页图",
      "markushPart.pageScrollAria": "Part Markush 可视化页图",
      "markushPart.corefAria": "Part 指代 coreference JSON 编辑",
      "markushPart.wait": "请先点击「加载分子指代/Markush 结果」并选择文档与页码。",

      "activityText.title": "文本活性抽取（整体）",
      "activityText.hint": "从全文文本中抽取的蛋白-配体活性结果，以整体表格形式查看。",
      "activityText.resultDir": "结果目录（与运行推理输出目录一致）",
      "activityText.load": "加载文本活性结果",
      "activityText.doc": "文档",
      "activityText.allDocs": "全部",
      "activityText.pdfPreviewAria": "该文档 PDF 预览",
      "activityText.pdfPlaceholder": "选择文档后预览该文档 PDF",
      "activityText.saveEdits": "保存修改",

      "activityImg.title": "图表活性抽取（按文档展示全部）",
      "activityImg.hint": "选择文档后直接合并显示该文档下所有图表/表格的活性抽取结果。",
      "activityImg.load": "加载图表活性结果",
      "activityImg.saveEdits": "保存修改",
      "activityImg.placeholder": "请先点击「加载图表活性结果」，然后选择文档。",

      "givenStruct.title": "结构条件活性抽取",
      "givenStruct.resultDir": "结果目录（与运行推理输出目录一致后点“加载结果”）",
      "givenStruct.load": "加载结果",
      "givenStruct.doc": "文档",
      "givenStruct.givenHead": "Given 配体结构（RDKit 2D，用于相似度计算的参考 SMILES）",
      "givenStruct.pdbIdLabel": "Complex PDB ID",
      "givenStruct.rcsbLink": "RCSB 结构页",
      "givenStruct.pdbTitleLabel": "PDB Title",
      "givenStruct.givenImgAlt": "Given 配体 2D 结构",
      "givenStruct.simHint": "相似度匹配结果（与上方 Given 对照；点「查看分子」在 Ketcher 中查看识别 SMILES，可与 Given 切换对比）",
      "givenStruct.ketcherBack": "返回「相似度结果表」",
      "givenStruct.smilesPh": "识别的 SMILES（可编辑）",
      "givenStruct.smilesAria": "识别的 SMILES",
      "givenStruct.draw": "绘制",
      "givenStruct.loadGiven": "载入 Given 到 Ketcher",
      "givenStruct.ketcherIframeTitle": "Ketcher 识别配体",
      "givenStruct.givenImgAltRdkit": "Given 配体 2D 结构（RDKit）",

      "results.title": "结果预览",
      "results.resultDir": "结果目录（与上面输出目录一致后点“加载结果”）",
      "results.load": "加载结果",
      "results.doc": "文档",
      "results.allDocs": "全部",
      "results.tableEmpty": "暂无数据，请先运行推理并加载结果目录。",

      "footer.line": "BioMiner: A Multi-modal System for Automated Mining of Protein-Ligand Bioactivity Data from Literature",

      "common.first": "首页",
      "common.prev": "上一页",
      "common.next": "下一页",
      "common.last": "末页",
      "common.operation": "操作",
      "common.viewMol": "查看分子",
      "common.loading": "加载中…",
      "common.loadingLong": "加载中…（文档较多时可能需等待数秒）",
      "common.fillResultDir": "请填写结果目录",
      "common.pdfDocPreview": "选择文档后预览该文档 PDF",
      "common.pdfLoading": "加载中…",
      "common.docPdfTitle": "文档 PDF 预览",
    },
    en: {
      "meta.pageTitle": "BioMiner Interactive UI",
      "header.subtitle": "Automatically mine protein–ligand bioactivity data from literature",
      "nav.tablist": "Navigation",
      "nav.input": "Input",
      "nav.run": "Run",
      "nav.detection": "Structure detection",
      "nav.markushFull": "Full structures",
      "nav.markushPart": "Part Markush",
      "nav.activityText": "Text bioactivity",
      "nav.activityImage": "Figure/table bioactivity",
      "nav.activityGivenStructure": "Structure-conditioned bioactivity",
      "nav.results": "Results preview",
      "lang.label": "Language",
      "lang.zh": "中文",
      "lang.en": "English",

      "input.h1pdf": "1. Input PDF",
      "input.pdfPath": "PDF path (relative to project root)",
      "input.useExample": "Use example",
      "input.uploadPdf": "Or upload a PDF",
      "input.chooseFile": "Choose file",
      "input.noFileSelected": "No file selected",
      "input.previewPdf": "Preview PDF",
      "input.placeholderPreview": "Choose or enter a PDF path, then click “Preview PDF”",
      "input.h2out": "2. Output & config",
      "input.outputDir": "Output directory (relative to project root)",
      "input.configPath": "Config file path",
      "input.apiSummary": "API config (for proprietary MLLM)",
      "input.loadConfig": "Load from config file",
      "input.saveConfig": "Save to config file",

      "run.title": "Run inference",
      "run.hint": "Ensure mineru_server, moldet_server, ocsr_server are running per README; for BioMiner-Instruct, also start the vLLM service.",
      "run.btn": "Run BioMiner",
      "run.jobId": "Job ID:",
      "run.status": "Status:",
      "run.refresh": "Refresh",

      "detection.title": "Chemical structure detection",
      "detection.hint": "After a run, click “Show detection boxes” to load page images and bboxes_with_pred_smiless from stage_one.pkl; click a box to see page, index, bbox, SMILES.",
      "detection.resultDir": "Result directory (same as above)",
      "detection.showBbox": "Show detection boxes",
      "detection.docPage": "Document / page",
      "detection.selectDoc": "Select document",
      "detection.selectPage": "Select page",
      "detection.zoomAria": "Page zoom",
      "detection.zoomOut": "Zoom out",
      "detection.zoomIn": "Zoom in",
      "detection.zoomReset": "Reset to 100%",
      "detection.zoomFit": "Fit to column width",
      "detection.zoomFitBtn": "Fit width",
      "detection.bboxListEmpty": "No molecular boxes on this page",
      "detection.canvasAria": "Page image and boxes",
      "detection.bboxListTitle": "All boxes",
      "detection.backList": "Back to box list",
      "detection.cropTitle": "Cropped box",
      "detection.draw": "Draw",
      "detection.saveSmiles": "Save SMILES",
      "detection.ketcherTitle": "Ketcher editor",
      "detection.placeholder": "Click “Show detection boxes” first, then click a box to view the structure.",

      "markushFull.title": "Full (complete structures)",
      "markushFull.hint": "After inference, load coreference / Markush results from the output directory and browse Full structures by page.",
      "markushFull.hiddenDir": "Result directory (same as inference output)",
      "markushFull.load": "Load coreference / Markush",
      "markushFull.placeholder": "Select document and page for Full visualization (md_merge_*_yolo_distinguish_full_markush_after_ocsr)",
      "markushFull.pageImgAlt": "Full visualization page",
      "markushFull.pageScrollAria": "Full visualization",
      "markushFull.corefLabel": "Coreference",
      "markushFull.saveCoref": "Save coreference",
      "markushFull.corefAria": "Edit coreference JSON",
      "markushFull.wait": "Load coreference / Markush and select document and page first.",

      "markushPart.title": "Part (Markush scaffold / R-group)",
      "markushPart.hint": "After inference, load coreference / Markush results and browse Part (scaffold / R-group) data by page.",
      "markushPart.placeholder": "Select document and page for Part Markush visualization (md_merge_*_yolo_distinguish_full_markush_after_ocsr)",
      "markushPart.pageImgAlt": "Part Markush visualization",
      "markushPart.pageScrollAria": "Part Markush visualization",
      "markushPart.corefAria": "Edit Part coreference JSON",
      "markushPart.wait": "Load coreference / Markush and select document and page first.",

      "activityText.title": "Text bioactivity (merged)",
      "activityText.hint": "Protein–ligand activities extracted from full text, shown in one table.",
      "activityText.resultDir": "Result directory (same as inference output)",
      "activityText.load": "Load text bioactivity",
      "activityText.doc": "Document",
      "activityText.allDocs": "All",
      "activityText.pdfPreviewAria": "PDF preview for this document",
      "activityText.pdfPlaceholder": "Select a document to preview PDF",
      "activityText.saveEdits": "Save edits",

      "activityImg.title": "Figure/table bioactivity (per document)",
      "activityImg.hint": "Select a document to merge all figure/table bioactivity rows.",
      "activityImg.load": "Load figure/table bioactivity",
      "activityImg.saveEdits": "Save edits",
      "activityImg.placeholder": "Load figure/table bioactivity first, then select a document.",

      "givenStruct.title": "Structure-conditioned bioactivity",
      "givenStruct.resultDir": "Result directory, then click “Load results”",
      "givenStruct.load": "Load results",
      "givenStruct.doc": "Document",
      "givenStruct.givenHead": "Given ligand (RDKit 2D, reference SMILES for similarity)",
      "givenStruct.pdbIdLabel": "Complex PDB ID",
      "givenStruct.rcsbLink": "RCSB entry",
      "givenStruct.pdbTitleLabel": "PDB title",
      "givenStruct.givenImgAlt": "Given ligand 2D structure",
      "givenStruct.simHint": "Similarity matches (compare with Given above; “View molecule” opens recognized SMILES in Ketcher; use “Load Given” to compare).",
      "givenStruct.ketcherBack": "Back to similarity table",
      "givenStruct.smilesPh": "Recognized SMILES (editable)",
      "givenStruct.smilesAria": "Recognized SMILES",
      "givenStruct.draw": "Draw",
      "givenStruct.loadGiven": "Load Given in Ketcher",
      "givenStruct.ketcherIframeTitle": "Ketcher — recognized ligand",
      "givenStruct.givenImgAltRdkit": "Given ligand 2D structure (RDKit)",

      "results.title": "Results preview",
      "results.resultDir": "Result directory (same as output above), then “Load results”",
      "results.load": "Load results",
      "results.doc": "Document",
      "results.allDocs": "All",
      "results.tableEmpty":
        "No data yet. Run inference and load the results directory.",

      "footer.line": "BioMiner: A Multi-modal System for Automated Mining of Protein-Ligand Bioactivity Data from Literature",

      "common.first": "First",
      "common.prev": "Prev",
      "common.next": "Next",
      "common.last": "Last",
      "common.operation": "Action",
      "common.viewMol": "View molecule",
      "common.loading": "Loading…",
      "common.loadingLong": "Loading… (may take a few seconds for many documents)",
      "common.fillResultDir": "Please set the result directory",
      "common.pdfDocPreview": "Select a document to preview PDF",
      "common.pdfLoading": "Loading…",
      "common.docPdfTitle": "PDF preview",
    },
  };

  /** 动态文案（app.js） */
  const DYNAMIC = {
    zh: {
      "alert.noExamplePdf": "无示例 PDF",
      "alert.exampleFail": "获取示例路径失败: {msg}",
      "alert.needPdf": "请先输入 PDF 路径或选择上传文件",
      "alert.previewFail": "预览失败: {msg}",
      "alert.loadConfigFail": "加载配置失败: {msg}",
      "alert.savedConfig": "已保存到配置文件",
      "alert.saveConfigFail": "保存配置失败: {msg}",
      "alert.needPdfRun": "请填写 PDF 路径或上传 PDF 文件",
      "log.submitted": "任务已提交，请点击「刷新状态」查看日志。",
      "log.submitFail": "提交失败: {msg}",
      "log.statusFail": "获取状态失败: {msg}",
      "pagination.results":
        "共 {total} 条，第 {cur} / {pages} 页（每页 {size} 条）",
      "results.summary": "目录: {dir} | 共 {total} 条记录（分页展示，每页 {size} 条）",
      "results.loadFail": "加载失败: {msg}",
      "givenStruct.ketcherHint":
        "相似度 {sim}{lig} — 上方为 Given 配体（RDKit）；此处为表格「识别」SMILES。可点「载入 Given 到 Ketcher」与 Given 切换对比。",
      "givenStruct.ketcherHintLig": " · 配体 {lig}",
      "alert.noRowSmiles": "该行无识别 SMILES；可在下方输入框粘贴后点「绘制」。",
      "givenStruct.pdbTitleMissing": "（BioVista/pdb_titles.json 中无该 PDB ID；JSON 内 key 为小写，如 6qhr）",
      "givenStruct.noPdbTitle": "（暂无 PDB ID，无法匹配标题）",
      "givenStruct.smilesErr":
        "（未解析到 Given SMILES：请确认配置中 data.pdb_structure_path 下存在该文档对应的配体 .sdf / .mol2，并与推理时一致。）",
      "givenStruct.rdkitErr": "（无法渲染结构图：SMILES 无效或 RDKit 服务异常。）{extra}",
      "givenStruct.extraSmiles": " 原始 SMILES：{s}",
      "alert.noGivenDoc": "当前文档无 Given SMILES。",
      "activity.summary":
        "目录: {dir} | 共 {total} 条文本活性记录（分页展示，每页 {size} 条）",
      "markush.pagePdfDefault": "选择文档与页码后显示该页 PDF 图",
      "markush.pageMissing": "该页图不存在或加载失败",
      "markush.fullPlaceholder": "选择文档与页码后显示 Full 分子可视化页图",
      "markush.partPlaceholder": "选择文档与页码后显示 Part Markush 可视化页图",
      "markush.noPartViz":
        "本页无 Part 可视化图（该页没有含 * 的分子框时不会生成 merge_part）。右侧「本页无数据」与此一致。可换有 Part 的页码查看。",
      "markush.noFullViz":
        "该页无 Full 可视化图或路径错误（需 md_merge_*_yolo_distinguish_full_markush_after_ocsr 下存在对应 merge_full PNG）。",
      "log.submitting": "提交中…",
      "detection.pageImageFail": "页图加载失败",
      "detection.genericLoadFail": "加载失败",
      "detection.alertSelectBbox": "请先点击某个分子框选择 bbox",
      "detection.alertLoadPageFirst": "请先加载某一页的分子检测框",
      "detection.smilesEmpty": "SMILES 为空，无法保存",
      "detection.needDirOrRun": "请填写结果目录，或先运行推理以自动填充",
      "detection.loadDrawFail": "加载/绘制分子检测框失败: {msg}",
      "detection.placeholderAfterFail": "请先点击「展示分子检测框」加载页图与分子框（点击框可在右侧查看结构）。",
      "detection.selectDocOption": "选择文档",
      "detection.selectPageOption": "选择页码",
      "detection.pageN": "第 {n} 页",
      "markush.selectDocPagePrompt": "请选择文档与页码。",
      "markush.loadPageDataFail": "加载页数据失败",
      "markush.noCoref": "本页无指代(coreference)数据。",
      "markush.noFullFile": "本页无 Full 抽取结果文件。",
      "markush.noPartFile": "本页无 Part 抽取结果文件。",
      "markush.loadFailWithMsg": "加载失败: {msg}",
      "markush.saveBackup": "已保存。原文件已备份为: {path}",
      "markush.saveNoBackup": "已保存（此前无同名文件，未生成备份）。",
      "markush.needDirDocPage": "请先选择结果目录、文档与页码",
      "markush.invalidJson": "内容不是合法 JSON，无法保存: {msg}",
      "markush.notFound": "未找到分子指代/Markush 结果，请先运行推理。",
      "markush.loadPagesFail": "加载分子指代/Markush 结果失败: {msg}",
      "markush.waitLoadHint": "请先点击「加载分子指代/Markush 结果」并选择文档与页码。",
      "markush.partNoPartPages":
        "当前结果目录下没有 Part（含 *）页的抽取文件，无法列出文档/页码。请换目录或查看 Full 页签。",
      "activityImg.resultCol": "结果",
      "activityImg.noDataRow": "当前图表无活性数据",
      "activityImg.pdfSelectDoc": "请选择文档后预览该文档 PDF",
      "activityImg.pickDocOrEmpty": "请选择文档，或当前文档无活性数据。",
      "activityImg.fetchFail": "加载图表活性结果失败",
      "activityImg.loadFailWithMsg": "加载失败: {msg}",
      "activityImg.notFoundRun": "未找到图表活性结果，请先运行推理。",
      "activityImg.loadPagesFail": "加载图表活性结果失败: {msg}",
      "activityImg.waitHint": "请先点击「加载图表活性结果」，然后选择文档。",
      "alert.needActivityDir": "请先加载/选择结果目录",
      "alert.noEdits": "没有可保存的修改",
      "alert.savedOk": "已保存修改。",
      "alert.saveFailGeneric": "保存失败",
      "alert.needLoadImageDoc": "请先加载图表活性结果并选择文档",
      "save.failWithMsg": "保存失败: {msg}",
      "error.unknown": "未知错误",
    },
    en: {
      "alert.noExamplePdf": "No example PDF",
      "alert.exampleFail": "Failed to get example path: {msg}",
      "alert.needPdf": "Enter a PDF path or upload a file first",
      "alert.previewFail": "Preview failed: {msg}",
      "alert.loadConfigFail": "Failed to load config: {msg}",
      "alert.savedConfig": "Saved to config file",
      "alert.saveConfigFail": "Failed to save config: {msg}",
      "alert.needPdfRun": "Please provide a PDF path or upload a PDF",
      "log.submitted": "Job submitted — click “Refresh” to see logs.",
      "log.submitFail": "Submit failed: {msg}",
      "log.statusFail": "Failed to get status: {msg}",
      "pagination.results":
        "{total} records — page {cur} / {pages} ({size} per page)",
      "results.summary": "Dir: {dir} | {total} records (paginated, {size} per page)",
      "results.loadFail": "Load failed: {msg}",
      "givenStruct.ketcherHint":
        "Similarity {sim}{lig} — Given ligand (RDKit) is above; here is the recognized SMILES. Use “Load Given in Ketcher” to compare.",
      "givenStruct.ketcherHintLig": " · Ligand {lig}",
      "alert.noRowSmiles": "No SMILES in this row; paste in the box below and click Draw.",
      "givenStruct.pdbTitleMissing":
        "(No title in BioVista/pdb_titles.json for this PDB ID; keys are lowercase, e.g. 6qhr)",
      "givenStruct.noPdbTitle": "(No PDB ID — cannot match title)",
      "givenStruct.smilesErr":
        "(No Given SMILES: check data.pdb_structure_path for this document’s .sdf / .mol2, consistent with inference.)",
      "givenStruct.rdkitErr": "(Could not render structure: invalid SMILES or RDKit error.){extra}",
      "givenStruct.extraSmiles": " Original SMILES: {s}",
      "alert.noGivenDoc": "No Given SMILES for this document.",
      "activity.summary":
        "Dir: {dir} | {total} text bioactivity rows ({size} per page)",
      "markush.pagePdfDefault": "Select document and page for PDF image",
      "markush.pageMissing": "Page image missing or failed to load",
      "markush.fullPlaceholder": "Select document and page for Full visualization",
      "markush.partPlaceholder": "Select document and page for Part Markush visualization",
      "markush.noPartViz":
        "No Part visualization for this page (merge_part is not generated when there is no * box). Try another page with Part structures.",
      "markush.noFullViz":
        "No Full visualization or bad path (need merge_full PNG under md_merge_*_yolo_distinguish_full_markush_after_ocsr).",
      "log.submitting": "Submitting…",
      "detection.pageImageFail": "Failed to load page image",
      "detection.genericLoadFail": "Load failed",
      "detection.alertSelectBbox": "Click a molecule box first to select a bbox",
      "detection.alertLoadPageFirst": "Load detection boxes for a page first",
      "detection.smilesEmpty": "SMILES is empty; cannot save",
      "detection.needDirOrRun": "Set result directory or run inference first to auto-fill",
      "detection.loadDrawFail": "Failed to load/draw detection boxes: {msg}",
      "detection.placeholderAfterFail": "Click “Show detection boxes” first, then click a box to view the structure.",
      "detection.selectDocOption": "Select document",
      "detection.selectPageOption": "Select page",
      "detection.pageN": "Page {n}",
      "markush.selectDocPagePrompt": "Select document and page.",
      "markush.loadPageDataFail": "Failed to load page data",
      "markush.noCoref": "No coreference data on this page.",
      "markush.noFullFile": "No Full extraction file on this page.",
      "markush.noPartFile": "No Part extraction file on this page.",
      "markush.loadFailWithMsg": "Load failed: {msg}",
      "markush.saveBackup": "Saved. Original backed up to: {path}",
      "markush.saveNoBackup": "Saved (no previous file, no backup created).",
      "markush.needDirDocPage": "Select result directory, document, and page first",
      "markush.invalidJson": "Invalid JSON, cannot save: {msg}",
      "markush.notFound": "No coreference/Markush results; run inference first.",
      "markush.loadPagesFail": "Failed to load coreference/Markush: {msg}",
      "markush.waitLoadHint": "Click “Load coreference/Markush” and select document and page first.",
      "markush.partNoPartPages":
        "No Part (*-containing) pages in this directory. Try another folder or the Full tab.",
      "activityImg.resultCol": "Result",
      "activityImg.noDataRow": "No bioactivity data in current figure/table",
      "activityImg.pdfSelectDoc": "Select a document to preview PDF",
      "activityImg.pickDocOrEmpty": "Select a document, or no data for the current one.",
      "activityImg.fetchFail": "Failed to load figure/table bioactivity",
      "activityImg.loadFailWithMsg": "Load failed: {msg}",
      "activityImg.notFoundRun": "No figure/table bioactivity; run inference first.",
      "activityImg.loadPagesFail": "Failed to load figure/table bioactivity: {msg}",
      "activityImg.waitHint": "Click “Load figure/table bioactivity”, then select a document.",
      "alert.needActivityDir": "Load or select result directory first",
      "alert.noEdits": "No edits to save",
      "alert.savedOk": "Saved.",
      "alert.saveFailGeneric": "Save failed",
      "alert.needLoadImageDoc": "Load figure/table results and select a document first",
      "save.failWithMsg": "Save failed: {msg}",
      "error.unknown": "Unknown error",
    },
  };

  let lang = localStorage.getItem(STORAGE_KEY) || "zh";

  function pick(table, key) {
    return (table[lang] && table[lang][key]) || (table.zh && table.zh[key]) || null;
  }

  function t(key, vars) {
    let s = pick(STRINGS, key);
    if (s == null) s = pick(DYNAMIC, key);
    if (s == null) return key;
    if (vars && typeof s === "string") {
      s = s.replace(/\{(\w+)\}/g, (_, k) =>
        vars[k] != null ? String(vars[k]) : ""
      );
    }
    return s;
  }

  function applyDom() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!key) return;
      const val = t(key);
      if (
        el.tagName === "INPUT" ||
        el.tagName === "TEXTAREA"
      ) {
        if (el.hasAttribute("data-i18n-placeholder")) {
          el.placeholder = t(el.getAttribute("data-i18n-placeholder"));
        }
      } else {
        el.textContent = val;
      }
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (
        key &&
        (el.tagName === "INPUT" ||
          el.tagName === "TEXTAREA")
      ) {
        el.placeholder = t(key);
      }
    });
    document.querySelectorAll("[data-i18n-title]").forEach((el) => {
      const key = el.getAttribute("data-i18n-title");
      if (key) el.title = t(key);
    });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      const key = el.getAttribute("data-i18n-aria");
      if (key) el.setAttribute("aria-label", t(key));
    });
    document.querySelectorAll("[data-i18n-alt]").forEach((el) => {
      const key = el.getAttribute("data-i18n-alt");
      if (key) el.setAttribute("alt", t(key));
    });
    document.querySelectorAll("iframe[data-i18n-title]").forEach((el) => {
      const key = el.getAttribute("data-i18n-title");
      if (key) el.setAttribute("title", t(key));
    });
    document.title = t("meta.pageTitle");
  }

  function setLang(next) {
    if (next !== "zh" && next !== "en") return;
    lang = next;
    localStorage.setItem(STORAGE_KEY, lang);
    applyDom();
    syncHtmlLangAndButtons();
    document.dispatchEvent(
      new CustomEvent("biominer:langchange", { detail: { lang } })
    );
  }

  function initButtons() {
    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const l = btn.getAttribute("data-lang");
        if (l) setLang(l);
      });
    });
  }

  window.BioMinerI18n = { t, setLang, getLang: () => lang, applyDom, DYNAMIC };

  function syncHtmlLangAndButtons() {
    document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
    document.querySelectorAll(".lang-btn").forEach((btn) => {
      const l = btn.getAttribute("data-lang");
      btn.classList.toggle("active", l === lang);
      btn.setAttribute("aria-pressed", l === lang ? "true" : "false");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      syncHtmlLangAndButtons();
      applyDom();
      initButtons();
    });
  } else {
    syncHtmlLangAndButtons();
    applyDom();
    initButtons();
  }
})();
