/**
 * BioMiner_UI 用 Ketcher 桥接脚本（不依赖 Gradio）
 * 与 iframe 内 Ketcher 通信：setMolecule / getSmiles，同步本地 SMILES 输入框与绘图按钮。
 */
(function () {
  const INIT_DELAY_MS = 1000;
  const KETCHER_IFRAME_ID = "ketcher-iframe";
  const LOCAL_SMILES_INPUT_ID = "smiles-input";
  const DRAW_BUTTON_ID = "draw-button";

  let ketcherInstance = null;
  let commandQueue = [];

  function executeCommand(command) {
    if (ketcherInstance) {
      try {
        command();
      } catch (e) {
        console.warn("Ketcher command error:", e);
      }
    } else {
      commandQueue.push(command);
    }
  }

  function findKetcherInstance(maxAttempts) {
    if (maxAttempts <= 0) return;

    const ketcherIframe = document.getElementById(KETCHER_IFRAME_ID);
    if (!ketcherIframe) {
      setTimeout(() => findKetcherInstance(maxAttempts - 1), 100);
      return;
    }

    let ketcher = null;
    try {
      ketcher = ketcherIframe.contentWindow && ketcherIframe.contentWindow.ketcher ? ketcherIframe.contentWindow.ketcher : null;
    } catch (e) {
      setTimeout(() => findKetcherInstance(maxAttempts - 1), 100);
      return;
    }

    if (ketcher) {
      ketcherInstance = ketcher;
      setupKetcherListeners(ketcher);
      while (commandQueue.length > 0) {
        const cmd = commandQueue.shift();
        try {
          cmd();
        } catch (err) {
          console.warn("Queued command error:", err);
        }
      }
    } else {
      setTimeout(() => findKetcherInstance(maxAttempts - 1), 100);
    }
  }

  function setupKetcherListeners(ketcher) {
    const localSmilesInput = document.getElementById(LOCAL_SMILES_INPUT_ID);
    const drawButton = document.getElementById(DRAW_BUTTON_ID);

    if (drawButton && localSmilesInput) {
      drawButton.addEventListener("click", () => {
        const smiles = (localSmilesInput.value || "").trim();
        if (smiles) {
          executeCommand(() => {
            ketcher.setMolecule(smiles);
          });
        }
      });
    }

    ketcher.changeEvent.add(async () => {
      try {
        const newSmiles = await ketcher.getSmiles();
        if (localSmilesInput) localSmilesInput.value = newSmiles || "";
      } catch (e) {
        if (localSmilesInput) localSmilesInput.value = "";
      }
    });
  }

  /** 供外部调用：用 SMILES 在 Ketcher 中绘图 */
  window.biominerKetcherSetMolecule = function (smiles) {
    const input = document.getElementById(LOCAL_SMILES_INPUT_ID);
    if (input && typeof smiles === "string" && smiles.trim()) {
      input.value = smiles.trim();
      executeCommand(() => {
        if (ketcherInstance) ketcherInstance.setMolecule(smiles.trim());
      });
    }
  };

  setTimeout(() => {
    findKetcherInstance(15);
  }, INIT_DELAY_MS);
})();

/** 结构条件活性抽取 sheet：独立 Ketcher 实例（givenStructureKetcherIframe） */
(function initGivenStructureKetcher() {
  const IFRAME_ID = "givenStructureKetcherIframe";
  const INPUT_ID = "givenStructureKetcherSmilesInput";
  const DRAW_BTN_ID = "btnGivenStructureKetcherDraw";
  const INIT_DELAY_MS = 1200;
  let ketcherInstance = null;
  let commandQueue = [];

  function executeCommand(command) {
    if (ketcherInstance) {
      try {
        command();
      } catch (e) {
        console.warn("GivenStructure Ketcher command error:", e);
      }
    } else {
      commandQueue.push(command);
    }
  }

  function findKetcherInstance(maxAttempts) {
    if (maxAttempts <= 0) return;

    const ketcherIframe = document.getElementById(IFRAME_ID);
    if (!ketcherIframe) {
      setTimeout(() => findKetcherInstance(maxAttempts - 1), 100);
      return;
    }

    let ketcher = null;
    try {
      ketcher =
        ketcherIframe.contentWindow && ketcherIframe.contentWindow.ketcher
          ? ketcherIframe.contentWindow.ketcher
          : null;
    } catch (e) {
      setTimeout(() => findKetcherInstance(maxAttempts - 1), 100);
      return;
    }

    if (ketcher) {
      ketcherInstance = ketcher;
      const localSmilesInput = document.getElementById(INPUT_ID);
      const drawButton = document.getElementById(DRAW_BTN_ID);

      if (drawButton && localSmilesInput) {
        drawButton.addEventListener("click", () => {
          const smiles = (localSmilesInput.value || "").trim();
          if (smiles) {
            executeCommand(() => {
              ketcher.setMolecule(smiles);
            });
          }
        });
      }

      ketcher.changeEvent.add(async () => {
        try {
          const newSmiles = await ketcher.getSmiles();
          if (localSmilesInput) localSmilesInput.value = newSmiles || "";
        } catch (e) {
          if (localSmilesInput) localSmilesInput.value = "";
        }
      });

      while (commandQueue.length > 0) {
        const cmd = commandQueue.shift();
        try {
          cmd();
        } catch (err) {
          console.warn("GivenStructure queued command error:", err);
        }
      }
    } else {
      setTimeout(() => findKetcherInstance(maxAttempts - 1), 100);
    }
  }

  window.biominerGivenStructureKetcherSetMolecule = function (smiles) {
    const input = document.getElementById(INPUT_ID);
    if (input && typeof smiles === "string" && smiles.trim()) {
      input.value = smiles.trim();
      executeCommand(() => {
        if (ketcherInstance) ketcherInstance.setMolecule(smiles.trim());
      });
    }
  };

  setTimeout(() => {
    findKetcherInstance(30);
  }, INIT_DELAY_MS);
})();
