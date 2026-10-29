document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // 1. STATE & STORAGE MANAGEMENT
    // ==========================================
    let currentTab = "tab-ocr"; // "tab-ocr", "tab-whisper", "tab-settings"
    let currentLang = localStorage.getItem("app_lang") || "vi";
    let isLocked = true; // Lock red and green boxes together by default
    let isMaskEnabled = true;

    // Default Bounding Box Coordinates (Percentages)
    let maskBoxCoords = { x: 10, y: 78, w: 80, h: 14 };
    let subBoxCoords = { x: 10, y: 78, w: 80, h: 14 };

    // DOM Elements - Tabs
    const tabBtns = document.querySelectorAll(".tab-btn");
    const workspaceLayout = document.getElementById("workspace-layout");
    const panelSubtitles = document.getElementById("panel-subtitles");
    const panelSettings = document.getElementById("panel-settings");

    // DOM Elements - CapCut Subtitle Studio
    const capcutLiveSample = document.getElementById("capcut-live-sample");
    const bboxSubPreviewText = document.getElementById("bbox-sub-preview-text");
    const monitorStyleDesc = document.getElementById("monitor-style-desc");
    const btnResetSubStyling = document.getElementById("btn-reset-sub-styling");
    const presetCards = document.querySelectorAll(".preset-card");
    const capcutChips = document.querySelectorAll(".capcut-chip");
    const colorSwatchBtns = document.querySelectorAll(".color-swatch-btn");
    const subPrimaryColor = document.getElementById("sub-primary-color");
    const subPrimaryHex = document.getElementById("sub-primary-hex");
    const step3SubColor = document.getElementById("step3-sub-color");
    const step3SubColorHex = document.getElementById("step3-sub-color-hex");
    const subOutlineColor = document.getElementById("sub-outline-color");
    const subOutlineHex = document.getElementById("sub-outline-hex");
    const subOutlineWidth = document.getElementById("sub-outline-width");
    const btnBoxstyleOutline = document.getElementById("btn-boxstyle-outline");
    const btnBoxstyleBox = document.getElementById("btn-boxstyle-box");
    const boxOptionsWrapper = document.getElementById("box-options-wrapper");
    const subBoxColor = document.getElementById("sub-box-color");
    const subBoxHex = document.getElementById("sub-box-hex");
    const subBoxOpacity = document.getElementById("sub-box-opacity");
    const subBoxOpacityVal = document.getElementById("sub-box-opacity-val");
    const subFontSize = document.getElementById("sub-font-size");
    const subFontName = document.getElementById("sub-font-name");
    const subBold = document.getElementById("sub-bold");
    const step3FontSizeBadge = document.getElementById("step3-font-size-badge");
    const fontSizeChips = document.querySelectorAll(".font-size-chip");

    // DOM Elements - Modular Settings Subpanes
    const subnavPills = document.querySelectorAll(".subnav-pill");
    const subpanes = document.querySelectorAll(".subpane-content");

    // DOM Elements - Mask & Bounding Box Controls
    const maskEnabledCheck = document.getElementById("mask-enabled");
    const maskStyleSelect = document.getElementById("mask-style");
    const step3MaskEnabled = document.getElementById("step3-mask-enabled");
    const step3MaskOptions = document.getElementById("step3-mask-options");
    const maskChips = document.querySelectorAll(".mask-chip");
    const btnToggleMaskBoxPreview = document.getElementById("btn-toggle-mask-box-preview");
    const btnToggleLock = document.getElementById("btn-toggle-lock");
    const btnPresetBottom = document.getElementById("btn-preset-bottom");
    const btnPresetTop = document.getElementById("btn-preset-top");
    const btnPresetReset = document.getElementById("btn-preset-reset");

    // DOM Elements - Tab 4 (System Settings)
    const sharedVoiceSelect = document.getElementById("shared-voice-select");
    const sharedVoiceRate = document.getElementById("shared-voice-rate");
    const btnSharedPreviewVoice = document.getElementById("btn-shared-preview-voice");
    const sharedTtsVol = document.getElementById("shared-tts-vol");
    const sharedTtsVolVal = document.getElementById("shared-tts-vol-val");
    const sharedBgVol = document.getElementById("shared-bg-vol");
    const sharedBgVolVal = document.getElementById("shared-bg-vol-val");
    const sharedBilibiliCookie = document.getElementById("shared-bilibili-cookie");
    const ttsStudioText = document.getElementById("tts-studio-text");
    const btnStudioPlay = document.getElementById("btn-studio-play");
    const btnStudioDownload = document.getElementById("btn-studio-download");

    // DOM Elements - Canvas & Bounding Boxes
    const canvasVideoWrapper = document.getElementById("canvas-video-wrapper");
    const canvasOverlay = document.getElementById("canvas-overlay");
    const bboxMask = document.getElementById("bbox-mask");
    const bboxSub = document.getElementById("bbox-sub");
    const videoContainer = document.getElementById("video-container-relative");
    const previewVideoElement = document.getElementById("preview-video-element");

    // DOM Elements - Output / Progress / Results
    const stateIdle = document.getElementById("state-idle");
    const stateProcessing = document.getElementById("state-processing");
    const stateSuccess = document.getElementById("state-success");
    const stateError = document.getElementById("state-error");
    const progressBar = document.getElementById("progress-bar");
    const progressPercent = document.getElementById("progress-percent");
    const statusMessage = document.getElementById("status-message");
    const statusBadge = document.getElementById("status-badge");
    const videoPreview = document.getElementById("video-preview");
    const downloadBtn = document.getElementById("download-btn");
    const downloadSrtBtn = document.getElementById("download-srt-btn");
    const resetBtn = document.getElementById("reset-btn");
    const retryBtn = document.getElementById("retry-btn");
    const errorMessage = document.getElementById("error-message");

    // Steps timeline
    const stepDownload = document.getElementById("step-download");
    const stepTranslate = document.getElementById("step-translate");
    const stepTts = document.getElementById("step-tts");
    const stepMerge = document.getElementById("step-merge");

    let processingInterval = null;
    let currentTaskId = null;
    let previewAudio = null;

    // ==========================================
    // 2. LOAD & SAVE SHARED CONFIGURATION
    // ==========================================
    function loadSharedSettings() {
        const savedVoice = localStorage.getItem("shared_voice") || "female_hoaimy";
        const savedRate = localStorage.getItem("shared_rate") || "+0%";
        const savedTtsVol = localStorage.getItem("shared_tts_vol") || "1.0";
        const savedBgVol = localStorage.getItem("shared_bg_vol") || "0.15";
        const savedCookie = localStorage.getItem("shared_cookie") || "";

        if (sharedVoiceSelect) sharedVoiceSelect.value = savedVoice;
        if (sharedVoiceRate) sharedVoiceRate.value = savedRate;
        if (sharedTtsVol) {
            sharedTtsVol.value = savedTtsVol;
            sharedTtsVolVal.textContent = Math.round(parseFloat(savedTtsVol) * 100) + "%";
        }
        if (sharedBgVol) {
            sharedBgVol.value = savedBgVol;
            sharedBgVolVal.textContent = Math.round(parseFloat(savedBgVol) * 100) + "%";
        }
        if (sharedBilibiliCookie) sharedBilibiliCookie.value = savedCookie;
    }

    function saveSharedSettings() {
        if (sharedVoiceSelect) localStorage.setItem("shared_voice", sharedVoiceSelect.value);
        if (sharedVoiceRate) localStorage.setItem("shared_rate", sharedVoiceRate.value);
        if (sharedTtsVol) localStorage.setItem("shared_tts_vol", sharedTtsVol.value);
        if (sharedBgVol) localStorage.setItem("shared_bg_vol", sharedBgVol.value);
        if (sharedBilibiliCookie) localStorage.setItem("shared_cookie", sharedBilibiliCookie.value);
    }

    // Attach listeners to auto-save settings
    [sharedVoiceSelect, sharedVoiceRate, sharedBilibiliCookie].forEach(el => {
        if (el) el.addEventListener("change", saveSharedSettings);
    });

    if (sharedTtsVol) {
        sharedTtsVol.addEventListener("input", (e) => {
            sharedTtsVolVal.textContent = Math.round(parseFloat(e.target.value) * 100) + "%";
            saveSharedSettings();
        });
    }

    if (sharedBgVol) {
        sharedBgVol.addEventListener("input", (e) => {
            sharedBgVolVal.textContent = Math.round(parseFloat(e.target.value) * 100) + "%";
            saveSharedSettings();
        });
    }

    loadSharedSettings();

    // ==========================================
    // 3. CAPCUT SUBTITLE ENGINE & PRESETS
    // ==========================================
    const capcutPresets = {
        "viral_white": {
            name: "Trắng Chuẩn (Hot Trend)",
            primary_color: "#FFFFFF",
            outline_color: "#000000",
            outline_width: 3.5,
            box_style: "outline",
            back_color: "#000000",
            box_opacity: 0.75,
            font_name: "Nunito",
            bold: true
        },
        "tiktok_yellow": {
            name: "Vàng Neon Nổi Bật",
            primary_color: "#FFE600",
            outline_color: "#000000",
            outline_width: 3.5,
            box_style: "outline",
            back_color: "#000000",
            box_opacity: 0.75,
            font_name: "Nunito",
            bold: true
        },
        "neon_green": {
            name: "Xanh Neon Dạ Quang",
            primary_color: "#00FF88",
            outline_color: "#000000",
            outline_width: 3.5,
            box_style: "outline",
            back_color: "#000000",
            box_opacity: 0.75,
            font_name: "Nunito",
            bold: true
        },
        "neon_cyan": {
            name: "Cyan Hiện Đại",
            primary_color: "#00F5FF",
            outline_color: "#000000",
            outline_width: 3.5,
            box_style: "outline",
            back_color: "#000000",
            box_opacity: 0.75,
            font_name: "Nunito",
            bold: true
        },
        "yellow_box": {
            name: "Hộp Vàng Bo Góc",
            primary_color: "#000000",
            outline_color: "#000000",
            outline_width: 0,
            box_style: "box",
            back_color: "#FFE600",
            box_opacity: 0.95,
            font_name: "Nunito",
            bold: true
        },
        "black_box": {
            name: "Hộp Đen Mờ",
            primary_color: "#FFFFFF",
            outline_color: "#000000",
            outline_width: 0,
            box_style: "box",
            back_color: "#000000",
            box_opacity: 0.75,
            font_name: "Nunito",
            bold: true
        }
    };

    let subStylingState = {
        preset: "viral_white",
        primary_color: "#FFFFFF",
        outline_color: "#000000",
        outline_width: 4.0,
        box_style: "outline",
        back_color: "#000000",
        box_opacity: 0.75,
        font_size: 48,
        font_name: "Nunito",
        bold: true
    };

    function loadSubStyling() {
        try {
            const savedVersion = localStorage.getItem("shared_sub_styling_v");
            if (savedVersion !== "2.3") {
                localStorage.setItem("shared_sub_styling_v", "2.3");
                subStylingState.font_size = 48;
                subStylingState.outline_width = 4.0;
                localStorage.setItem("shared_sub_styling", JSON.stringify(subStylingState));
                return;
            }
            const saved = localStorage.getItem("shared_sub_styling");
            if (saved) {
                const parsed = JSON.parse(saved);
                subStylingState = { ...subStylingState, ...parsed };
            }
        } catch (e) {
            console.warn("Failed to load sub styling from localStorage:", e);
        }
    }

    function setFontSize(size) {
        const s = parseInt(size);
        if (!s || isNaN(s)) return;
        subStylingState.font_size = s;
        subStylingState.preset = "custom";
        applySubStylingToUI();
        triggerDebouncedAutoSave(500);
    }

    function setPrimaryColor(color) {
        if (!color) return;
        subStylingState.primary_color = color;
        // Nếu người dùng đang ở chế độ hộp (box), khi người dùng cố ý chọn màu chữ
        // ta tự động chuyển sang chữ nổi viền đen dày 3.5px để chữ nổi rực rỡ, không bị chìm/tàng hình trong hộp
        if (subStylingState.box_style === "box") {
            subStylingState.box_style = "outline";
            subStylingState.outline_width = 3.5;
            subStylingState.outline_color = "#000000";
        }
        subStylingState.preset = "custom";
        applySubStylingToUI();
    }

    function applySubStylingToUI() {
        // 1. Controls inputs sync
        if (subPrimaryColor) subPrimaryColor.value = subStylingState.primary_color;
        if (subPrimaryHex) subPrimaryHex.textContent = subStylingState.primary_color.toUpperCase();
        if (step3SubColor) step3SubColor.value = subStylingState.primary_color;
        if (step3SubColorHex) step3SubColorHex.textContent = subStylingState.primary_color.toUpperCase();
        if (subOutlineColor) subOutlineColor.value = subStylingState.outline_color;
        if (subOutlineHex) subOutlineHex.textContent = subStylingState.outline_color.toUpperCase();
        if (subOutlineWidth) subOutlineWidth.value = String(subStylingState.outline_width);
        if (subBoxColor) subBoxColor.value = subStylingState.back_color;
        if (subBoxHex) subBoxHex.textContent = subStylingState.back_color.toUpperCase();
        if (subBoxOpacity) subBoxOpacity.value = subStylingState.box_opacity;
        if (subBoxOpacityVal) subBoxOpacityVal.textContent = Math.round(subStylingState.box_opacity * 100) + "%";
        if (subFontSize) subFontSize.value = String(subStylingState.font_size);
        if (subFontName) subFontName.value = subStylingState.font_name;
        if (subBold) subBold.checked = subStylingState.bold;

        // Step 3 Font size badge & chips sync
        if (step3FontSizeBadge) {
            let lbl = `${subStylingState.font_size}px`;
            if (subStylingState.font_size <= 36) lbl += " (Nhỏ gọn)";
            else if (subStylingState.font_size <= 42) lbl += " (Vừa)";
            else if (subStylingState.font_size <= 50) lbl += " (Chuẩn đẹp)";
            else if (subStylingState.font_size <= 60) lbl += " (Lớn nổi bật)";
            else lbl += " (Khổng lồ / Anime)";
            step3FontSizeBadge.textContent = lbl;
        }
        document.querySelectorAll(".font-size-chip").forEach(chip => {
            const sz = parseInt(chip.getAttribute("data-size"));
            chip.classList.toggle("active", sz === subStylingState.font_size);
        });

        // Box style toggle
        const isBox = subStylingState.box_style === "box";
        if (btnBoxstyleBox) btnBoxstyleBox.classList.toggle("active", isBox);
        if (btnBoxstyleOutline) btnBoxstyleOutline.classList.toggle("active", !isBox);
        if (boxOptionsWrapper) boxOptionsWrapper.classList.toggle("d-none", !isBox);

        // Color swatches active state (cho cả Bước 3 lẫn Subtitle Studio)
        document.querySelectorAll(".color-swatch-btn").forEach(btn => {
            const c = btn.getAttribute("data-color");
            btn.classList.toggle("active", c && c.toUpperCase() === subStylingState.primary_color.toUpperCase());
        });

        // Preset cards active state
        if (presetCards) {
            presetCards.forEach(card => {
                card.classList.toggle("active", card.getAttribute("data-preset") === subStylingState.preset);
            });
        }

        // Quick chips active state
        if (capcutChips) {
            capcutChips.forEach(chip => {
                chip.classList.toggle("active", chip.getAttribute("data-preset") === subStylingState.preset);
            });
        }

        // Monitor info text
        if (monitorStyleDesc) {
            const pName = capcutPresets[subStylingState.preset]?.name || "Tùy biến";
            monitorStyleDesc.textContent = `Mẫu: ${pName} • Font: ${subStylingState.font_name} • Cỡ: ${subStylingState.font_size}px`;
        }

        // 2. Render styling on Live Monitor & Bounding Box on canvas
        const vH = (videoContainer && videoContainer.clientHeight) || 450;
        const scaleRatio = vH / 720;
        const canvasFontSize = Math.max(14, Math.round(subStylingState.font_size * scaleRatio));

        [capcutLiveSample, bboxSubPreviewText].forEach(el => {
            if (!el) return;
            el.style.color = subStylingState.primary_color;
            el.style.webkitTextFillColor = subStylingState.primary_color;
            el.style.fontFamily = `"${subStylingState.font_name}", sans-serif`;
            el.style.fontWeight = subStylingState.bold ? "800" : "normal";

            if (el === capcutLiveSample) {
                el.style.fontSize = `${subStylingState.font_size}px`;
            } else {
                el.style.fontSize = `${canvasFontSize}px`;
            }

            if (isBox) {
                const hex = subStylingState.back_color.replace("#", "");
                const r = parseInt(hex.substring(0, 2), 16) || 0;
                const g = parseInt(hex.substring(2, 4), 16) || 0;
                const b = parseInt(hex.substring(4, 6), 16) || 0;
                el.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${subStylingState.box_opacity})`;
                el.style.webkitTextStroke = "none";
                el.style.padding = el === capcutLiveSample ? "6px 18px" : "4px 14px";
                el.style.borderRadius = "6px";
                el.style.textShadow = "none";
                el.style.paintOrder = "normal";
            } else {
                el.style.backgroundColor = "transparent";
                el.style.padding = "0";
                el.style.borderRadius = "0";
                el.style.paintOrder = "stroke fill";
                if (subStylingState.outline_width > 0) {
                    const sw = el === capcutLiveSample 
                        ? subStylingState.outline_width 
                        : Math.max(1.2, Math.round(subStylingState.outline_width * scaleRatio));
                    el.style.webkitTextStroke = `${sw}px ${subStylingState.outline_color}`;
                    el.style.textShadow = "0 3px 6px rgba(0,0,0,0.95), 0 0 14px rgba(0,0,0,0.7)";
                } else {
                    el.style.webkitTextStroke = "none";
                    el.style.textShadow = "0 2px 5px rgba(0,0,0,0.7)";
                }
            }
        });

        // Persist to localStorage
        localStorage.setItem("shared_sub_styling", JSON.stringify(subStylingState));
    }

    function applyPreset(presetKey) {
        if (!capcutPresets[presetKey]) return;
        const p = capcutPresets[presetKey];
        subStylingState.preset = presetKey;
        subStylingState.primary_color = p.primary_color;
        subStylingState.outline_color = p.outline_color;
        subStylingState.outline_width = p.outline_width;
        subStylingState.box_style = p.box_style;
        subStylingState.back_color = p.back_color;
        subStylingState.box_opacity = p.box_opacity;
        if (p.font_name) subStylingState.font_name = p.font_name;
        subStylingState.bold = p.bold;
        applySubStylingToUI();
    }

    // Attach CapCut Subtitle Event Listeners
    loadSubStyling();
    applySubStylingToUI();

    presetCards.forEach(card => {
        card.addEventListener("click", () => {
            const p = card.getAttribute("data-preset");
            applyPreset(p);
        });
    });

    capcutChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const p = chip.getAttribute("data-preset");
            applyPreset(p);
        });
    });

    // Lắng nghe click cho tất cả swatch màu (cả Bước 3 lẫn Subtitle Studio)
    document.querySelectorAll(".color-swatch-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const color = btn.getAttribute("data-color");
            setPrimaryColor(color);
        });
    });

    if (subPrimaryColor) {
        ["input", "change"].forEach(evt => {
            subPrimaryColor.addEventListener(evt, (e) => {
                setPrimaryColor(e.target.value);
            });
        });
    }

    if (step3SubColor) {
        ["input", "change"].forEach(evt => {
            step3SubColor.addEventListener(evt, (e) => {
                setPrimaryColor(e.target.value);
            });
        });
    }

    if (subOutlineColor) {
        ["input", "change"].forEach(evt => {
            subOutlineColor.addEventListener(evt, (e) => {
                subStylingState.outline_color = e.target.value;
                subStylingState.preset = "custom";
                applySubStylingToUI();
            });
        });
    }

    if (subOutlineWidth) {
        subOutlineWidth.addEventListener("change", (e) => {
            subStylingState.outline_width = parseFloat(e.target.value);
            subStylingState.preset = "custom";
            applySubStylingToUI();
        });
    }

    if (btnBoxstyleOutline) {
        btnBoxstyleOutline.addEventListener("click", () => {
            subStylingState.box_style = "outline";
            subStylingState.preset = "custom";
            applySubStylingToUI();
        });
    }

    if (btnBoxstyleBox) {
        btnBoxstyleBox.addEventListener("click", () => {
            subStylingState.box_style = "box";
            subStylingState.preset = "custom";
            applySubStylingToUI();
        });
    }

    if (subBoxColor) {
        subBoxColor.addEventListener("input", (e) => {
            subStylingState.back_color = e.target.value;
            subStylingState.preset = "custom";
            applySubStylingToUI();
        });
    }

    if (subBoxOpacity) {
        subBoxOpacity.addEventListener("input", (e) => {
            subStylingState.box_opacity = parseFloat(e.target.value);
            subStylingState.preset = "custom";
            applySubStylingToUI();
        });
    }

    if (subFontSize) {
        subFontSize.addEventListener("change", (e) => {
            setFontSize(e.target.value);
        });
    }

    // Lắng nghe click cho các chip cỡ chữ nhanh Bước 3
    document.querySelectorAll(".font-size-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const sz = parseInt(chip.getAttribute("data-size"));
            setFontSize(sz);
        });
    });

    if (subFontName) {
        subFontName.addEventListener("change", (e) => {
            subStylingState.font_name = e.target.value;
            applySubStylingToUI();
        });
    }

    if (subBold) {
        subBold.addEventListener("change", (e) => {
            subStylingState.bold = e.target.checked;
            applySubStylingToUI();
        });
    }

    if (btnResetSubStyling) {
        btnResetSubStyling.addEventListener("click", () => {
            applyPreset("viral_white");
            subStylingState.font_name = "Nunito";
            subStylingState.font_size = 48;
            subStylingState.outline_width = 4.0;
            applySubStylingToUI();
        });
    }

    window.addEventListener("resize", () => {
        applySubStylingToUI();
    });

    // ==========================================
    // 4. MODULAR SYSTEM SETTINGS SUBNAV
    // ==========================================
    if (subnavPills) {
        subnavPills.forEach(pill => {
            pill.addEventListener("click", () => {
                const targetSubpane = pill.getAttribute("data-subpane");
                subnavPills.forEach(p => p.classList.toggle("active", p === pill));
                subpanes.forEach(pane => {
                    pane.classList.toggle("d-none", pane.id !== targetSubpane);
                });
            });
        });
    }

    // ==========================================
    // 5. TAB SWITCHING LOGIC (4 TABS)
    // ==========================================
    function switchTab(targetTab) {
        currentTab = targetTab;
        tabBtns.forEach(btn => {
            btn.classList.toggle("active", btn.getAttribute("data-tab") === targetTab);
        });

        // Hide all major layout panels first
        if (workspaceLayout) workspaceLayout.classList.add("d-none");
        if (panelSubtitles) panelSubtitles.classList.add("d-none");
        if (panelSettings) panelSettings.classList.add("d-none");

        if (targetTab === "tab-subtitles") {
            if (panelSubtitles) panelSubtitles.classList.remove("d-none");
        } else if (targetTab === "tab-settings") {
            if (panelSettings) panelSettings.classList.remove("d-none");
        } else {
            // Workspace Layout (Step-by-Step Studio)
            if (workspaceLayout) workspaceLayout.classList.remove("d-none");
            if (typeof updateBBoxVisibility === "function") {
                updateBBoxVisibility();
            }
        }
    }

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tab = btn.getAttribute("data-tab");
            switchTab(tab);
        });
    });

    // ==========================================
    // 4. INTERACTIVE BOUNDING BOX ENGINE
    // ==========================================
    function applyBoxStyles() {
        if (bboxMask) {
            bboxMask.style.left = maskBoxCoords.x + "%";
            bboxMask.style.top = maskBoxCoords.y + "%";
            bboxMask.style.width = maskBoxCoords.w + "%";
            bboxMask.style.height = maskBoxCoords.h + "%";
        }
        if (bboxSub) {
            bboxSub.style.left = subBoxCoords.x + "%";
            bboxSub.style.top = subBoxCoords.y + "%";
            bboxSub.style.width = subBoxCoords.w + "%";
            bboxSub.style.height = subBoxCoords.h + "%";
        }
    }

    applyBoxStyles();

    function setupDragAndResize(element, getCoords, setCoords, onSync) {
        let isDragging = false;
        let isResizing = false;
        let activeHandle = null;
        let startX, startY;
        let initialCoords = { ...getCoords() };

        element.addEventListener("mousedown", (e) => {
            const handle = e.target.getAttribute("data-handle");
            const rect = videoContainer.getBoundingClientRect();
            startX = e.clientX;
            startY = e.clientY;
            initialCoords = { ...getCoords() };

            if (handle) {
                isResizing = true;
                activeHandle = handle;
            } else {
                isDragging = true;
            }

            element.classList.add("active-focus");
            e.stopPropagation();
            e.preventDefault();

            function onMouseMove(moveEvent) {
                const deltaX = ((moveEvent.clientX - startX) / rect.width) * 100;
                const deltaY = ((moveEvent.clientY - startY) / rect.height) * 100;

                let coords = { ...initialCoords };

                if (isDragging) {
                    coords.x = Math.max(0, Math.min(100 - coords.w, initialCoords.x + deltaX));
                    coords.y = Math.max(0, Math.min(100 - coords.h, initialCoords.y + deltaY));
                } else if (isResizing) {
                    if (activeHandle === "se") {
                        coords.w = Math.max(5, Math.min(100 - coords.x, initialCoords.w + deltaX));
                        coords.h = Math.max(3, Math.min(100 - coords.y, initialCoords.h + deltaY));
                    } else if (activeHandle === "sw") {
                        const newX = Math.max(0, Math.min(initialCoords.x + initialCoords.w - 5, initialCoords.x + deltaX));
                        coords.w = initialCoords.w + (initialCoords.x - newX);
                        coords.x = newX;
                        coords.h = Math.max(3, Math.min(100 - coords.y, initialCoords.h + deltaY));
                    } else if (activeHandle === "ne") {
                        coords.w = Math.max(5, Math.min(100 - coords.x, initialCoords.w + deltaX));
                        const newY = Math.max(0, Math.min(initialCoords.y + initialCoords.h - 3, initialCoords.y + deltaY));
                        coords.h = initialCoords.h + (initialCoords.y - newY);
                        coords.y = newY;
                    } else if (activeHandle === "nw") {
                        const newX = Math.max(0, Math.min(initialCoords.x + initialCoords.w - 5, initialCoords.x + deltaX));
                        const newY = Math.max(0, Math.min(initialCoords.y + initialCoords.h - 3, initialCoords.y + deltaY));
                        coords.w = initialCoords.w + (initialCoords.x - newX);
                        coords.h = initialCoords.h + (initialCoords.y - newY);
                        coords.x = newX;
                        coords.y = newY;
                    }
                }

                setCoords(coords);
                applyBoxStyles();
                if (onSync) onSync(coords);
            }

            function onMouseUp() {
                isDragging = false;
                isResizing = false;
                activeHandle = null;
                element.classList.remove("active-focus");
                document.removeEventListener("mousemove", onMouseMove);
                document.removeEventListener("mouseup", onMouseUp);
            }

            document.addEventListener("mousemove", onMouseMove);
            document.addEventListener("mouseup", onMouseUp);
        });
    }

    // Setup Red Box (Mask) Drag & Resize
    setupDragAndResize(
        bboxMask,
        () => maskBoxCoords,
        (newCoords) => { maskBoxCoords = newCoords; },
        (newCoords) => {
            if (isLocked) {
                subBoxCoords = { ...newCoords };
                applyBoxStyles();
            }
        }
    );

    // Setup Green Box (Subtitle) Drag & Resize
    setupDragAndResize(
        bboxSub,
        () => subBoxCoords,
        (newCoords) => { subBoxCoords = newCoords; },
        null
    );

    // Lock Toggle Button
    if (btnToggleLock) {
        btnToggleLock.addEventListener("click", () => {
            isLocked = !isLocked;
            if (isLocked) {
                btnToggleLock.classList.remove("unlocked");
                btnToggleLock.classList.add("active");
                btnToggleLock.innerHTML = '<i class="fa-solid fa-link"></i> <span>Đang khóa vị trí</span>';
                // Sync green to red box
                subBoxCoords = { ...maskBoxCoords };
                applyBoxStyles();
            } else {
                btnToggleLock.classList.add("unlocked");
                btnToggleLock.classList.remove("active");
                btnToggleLock.innerHTML = '<i class="fa-solid fa-link-slash"></i> <span>Đã mở khóa tự do</span>';
            }
        });
    }

    // Presets for Tab 1
    if (btnPresetBottom) {
        btnPresetBottom.addEventListener("click", () => {
            maskBoxCoords = { x: 10, y: 78, w: 80, h: 14 };
            if (isLocked) subBoxCoords = { ...maskBoxCoords };
            applyBoxStyles();
        });
    }

    if (btnPresetTop) {
        btnPresetTop.addEventListener("click", () => {
            maskBoxCoords = { x: 10, y: 8, w: 80, h: 14 };
            if (isLocked) subBoxCoords = { ...maskBoxCoords };
            applyBoxStyles();
        });
    }

    if (btnPresetReset) {
        btnPresetReset.addEventListener("click", () => {
            maskBoxCoords = { x: 10, y: 78, w: 80, h: 14 };
            subBoxCoords = { x: 10, y: 78, w: 80, h: 14 };
            applyBoxStyles();
        });
    }

    // ==========================================
    // 5. TAB 3: VOICE PREVIEW & TTS STUDIO
    // ==========================================
    if (btnSharedPreviewVoice) {
        btnSharedPreviewVoice.addEventListener("click", async () => {
            const voice = sharedVoiceSelect ? sharedVoiceSelect.value : "female_hoaimy";
            if (previewAudio && !previewAudio.paused) {
                previewAudio.pause();
                previewAudio = null;
                btnSharedPreviewVoice.innerHTML = '<i class="fa-solid fa-volume-high"></i> <span>Nghe thử</span>';
                return;
            }

            btnSharedPreviewVoice.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Đang tải...</span>';
            try {
                const res = await fetch(`/api/preview-voice?voice=${encodeURIComponent(voice)}`);
                if (!res.ok) throw new Error("Preview failed");
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                previewAudio = new Audio(url);
                previewAudio.onended = () => {
                    btnSharedPreviewVoice.innerHTML = '<i class="fa-solid fa-volume-high"></i> <span>Nghe thử</span>';
                };
                previewAudio.play();
                btnSharedPreviewVoice.innerHTML = '<i class="fa-solid fa-stop"></i> <span>Dừng</span>';
            } catch (err) {
                alert("Không thể tải bản nghe thử: " + err.message);
                btnSharedPreviewVoice.innerHTML = '<i class="fa-solid fa-volume-high"></i> <span>Nghe thử</span>';
            }
        });
    }

    if (btnStudioPlay) {
        btnStudioPlay.addEventListener("click", async () => {
            const text = ttsStudioText ? ttsStudioText.value.trim() : "";
            if (!text) {
                alert("Vui lòng nhập văn bản cần đọc.");
                return;
            }
            const voice = sharedVoiceSelect ? sharedVoiceSelect.value : "female_hoaimy";
            const rate = sharedVoiceRate ? sharedVoiceRate.value : "+0%";

            btnStudioPlay.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Đang đọc...</span>';
            try {
                const res = await fetch("/api/tts-free", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, voice, rate })
                });
                if (!res.ok) throw new Error("TTS generation failed");
                const blob = await res.blob();
                const audio = new Audio(URL.createObjectURL(blob));
                audio.play();
            } catch (err) {
                alert("Lỗi đọc văn bản: " + err.message);
            } finally {
                btnStudioPlay.innerHTML = '<i class="fa-solid fa-play"></i> <span>Đọc Trực Tiếp</span>';
            }
        });
    }

    if (btnStudioDownload) {
        btnStudioDownload.addEventListener("click", async () => {
            const text = ttsStudioText ? ttsStudioText.value.trim() : "";
            if (!text) {
                alert("Vui lòng nhập văn bản cần tải MP3.");
                return;
            }
            const voice = sharedVoiceSelect ? sharedVoiceSelect.value : "female_hoaimy";
            const rate = sharedVoiceRate ? sharedVoiceRate.value : "+0%";

            btnStudioDownload.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Đang tải...</span>';
            try {
                const res = await fetch("/api/tts-free", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, voice, rate })
                });
                if (!res.ok) throw new Error("TTS download failed");
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "tts_speech.mp3";
                a.click();
            } catch (err) {
                alert("Lỗi tải MP3: " + err.message);
            } finally {
                btnStudioDownload.innerHTML = '<i class="fa-solid fa-download"></i> <span>Tải File MP3</span>';
            }
        });
    }

    // ==========================================
    // 6. PIPELINE WORKFLOW & POLLING
    // ==========================================
    function showState(state) {
        [stateIdle, stateProcessing, stateSuccess, stateError].forEach(el => {
            if (el) el.classList.add("d-none");
        });
        if (canvasVideoWrapper) {
            canvasVideoWrapper.classList.remove("d-none");
        }
        if (state === "idle" && stateIdle) stateIdle.classList.remove("d-none");
        if (state === "processing" && stateProcessing) stateProcessing.classList.remove("d-none");
        if (state === "success" && stateSuccess) stateSuccess.classList.remove("d-none");
        if (state === "error" && stateError) stateError.classList.remove("d-none");
    }

    // ==========================================
    // STEP-BY-STEP STUDIO CONTROLLER (HORIZONTAL TABS)
    // ==========================================
    let currentProjectId = null;
    let currentTranscribeMode = "ocr";
    let currentStudioStep = 1;
    let segmentsData = [];
    let pollingInterval = null;

    // Elements - Horizontal Stepper Tabs
    const stepTabBtns = document.querySelectorAll(".step-tab-btn");
    const stepTabContents = document.querySelectorAll(".step-tab-content");

    // Elements - Wizard Step 1
    const videoUrlInput = document.getElementById("video-url-input");
    const btnPasteUrl = document.getElementById("btn-paste-url");
    const btnClearUrl = document.getElementById("btnClearUrl") || document.getElementById("btn-clear-url");
    const btnToggleCookie = document.getElementById("btn-toggle-cookie");
    const cookiePanel = document.getElementById("cookie-panel");
    const bilibiliCookieInput = document.getElementById("bilibili-cookie-input");
    const btnStep1Download = document.getElementById("btn-step1-download");
    const step1ProgressBox = document.getElementById("step1-progress-box");
    const step1ProgressBar = document.getElementById("step1-progress-bar");
    const step1ProgressMsg = document.getElementById("step1-progress-msg");
    const step1ProgressPct = document.getElementById("step1-progress-pct");

    // Elements - Wizard Step 2
    const btnModeOcr = document.getElementById("btn-mode-ocr");
    const btnModeWhisper = document.getElementById("btn-mode-whisper");
    const step2OcrOptions = document.getElementById("step2-ocr-options");
    const step2WhisperOptions = document.getElementById("step2-whisper-options");
    const maskEnabledCheckStep = document.getElementById("mask-enabled");
    const maskStyleSelectStep = document.getElementById("mask-style");
    const btnPresetBottomStep = document.getElementById("btn-preset-bottom");
    const btnStep2Transcribe = document.getElementById("btn-step2-transcribe");
    const step2ProgressBox = document.getElementById("step2-progress-box");
    const step2ProgressBar = document.getElementById("step2-progress-bar");
    const step2ProgressMsg = document.getElementById("step2-progress-msg");
    const step2ProgressPct = document.getElementById("step2-progress-pct");

    // Elements - Subtitle Editor Card
    const subtitleEditorCard = document.getElementById("subtitle-editor-card");
    const segmentsCount = document.getElementById("segments-count");
    const subtitleTableBody = document.getElementById("subtitle-table-body");
    const btnAddSegment = document.getElementById("btn-add-segment");
    const btnSaveSegments = document.getElementById("btn-save-segments");

    // Elements - Wizard Step 3
    const voiceSelectStep3 = document.getElementById("voice-select-step3");
    const btnPreviewVoiceStep3 = document.getElementById("btn-preview-voice-step3");
    const bgVolumeSlider = document.getElementById("bg-volume-slider");
    const bgVolLabel = document.getElementById("bg-vol-label");
    const ttsVolumeSlider = document.getElementById("tts-volume-slider");
    const ttsVolLabel = document.getElementById("tts-vol-label");
    const rvcModelSelectStep3 = document.getElementById("rvc-model-select-step3");
    const btnRefreshRvc = document.getElementById("btn-refresh-rvc");
    const rvcStatusHint = document.getElementById("rvc-status-hint");
    const rvcPitchRow = document.getElementById("rvc-pitch-row");
    const rvcPitchSlider = document.getElementById("rvc-pitch-slider");
    const rvcPitchVal = document.getElementById("rvc-pitch-val");
    const btnGotoSubstudio = document.getElementById("btn-goto-substudio");
    const btnStep3Next = document.getElementById("btn-step3-next");
    const btnStep3RenderDownload = document.getElementById("btn-step3-render-download");
    const lblStep3RenderDownload = document.getElementById("lbl-step3-render-download");
    const iconStep3RenderDownload = document.getElementById("icon-step3-render-download");
    const step3ProgressBox = document.getElementById("step3-progress-box");
    const step3ProgressBar = document.getElementById("step3-progress-bar");
    const step3ProgressMsg = document.getElementById("step3-progress-msg");
    const step3ProgressPct = document.getElementById("step3-progress-pct");
    const step3SuccessBox = document.getElementById("step3-success-box");
    const btnStep3Redownload = document.getElementById("btn-step3-redownload");
    const btnTlQuickExport = document.getElementById("btn-tl-quick-export");
    const lblTlQuickExport = document.getElementById("lbl-tl-quick-export");
    const iconTlQuickExport = document.getElementById("icon-tl-quick-export");
    const btnHeaderQuickExport = document.getElementById("btn-header-quick-export");
    const btnStep3DownloadAudio = document.getElementById("btn-step3-download-audio");
    const btnTlDownloadAudio = document.getElementById("btn-tl-download-audio");
    const btnHeaderDownloadAudio = document.getElementById("btn-header-download-audio");

    // Elements - Wizard Step 4
    const summarySubCount = document.getElementById("summary-sub-count");
    const summaryVoiceName = document.getElementById("summary-voice-name");
    const btnStep4Render = document.getElementById("btn-step4-render");
    const step4ProgressBox = document.getElementById("step4-progress-box");
    const step4ProgressBar = document.getElementById("step4-progress-bar");
    const step4ProgressMsg = document.getElementById("step4-progress-msg");
    const step4ProgressPct = document.getElementById("step4-progress-pct");
    const canvasWatermark = document.getElementById("canvas-watermark");

    // Elements - Project Bar & Modals
    const projectNameDisplay = document.getElementById("project-name-display");
    const projectNameInput = document.getElementById("project-name-input");
    const btnEditProjectName = document.getElementById("btn-edit-project-name");
    const projectSaveStatus = document.getElementById("project-save-status");
    const projectSaveText = document.getElementById("project-save-text");
    const projectStepIndicator = document.getElementById("project-step-indicator");
    const btnProjectOpen = document.getElementById("btn-project-open");
    const btnProjectNew = document.getElementById("btn-project-new");
    const btnProjectSaveManual = document.getElementById("btn-project-save-manual");

    const modalProjects = document.getElementById("modal-projects");
    const btnCloseProjectModal = document.getElementById("btn-close-project-modal");
    const projectSearchInput = document.getElementById("project-search-input");
    const btnModalCreateNew = document.getElementById("btn-modal-create-new");
    const projectListContainer = document.getElementById("project-list-container");
    const projectListEmpty = document.getElementById("project-list-empty");

    const modalConfirm = document.getElementById("modal-confirm");
    const confirmModalTitle = document.getElementById("confirm-modal-title");
    const confirmModalMessage = document.getElementById("confirm-modal-message");
    const confirmModalIcon = document.getElementById("confirm-modal-icon");
    const btnConfirmCancel = document.getElementById("btn-confirm-cancel");
    const btnConfirmCancelX = document.getElementById("btn-confirm-cancel-x");
    const btnConfirmOk = document.getElementById("btn-confirm-ok");

    let currentProjectMeta = null;
    let autoSaveTimer = null;

    const STEP_NAMES = {
        1: "Bước 1: Tải Video",
        2: "Bước 2: Quét OCR",
        3: "Bước 3: Dịch & Sub",
        4: "Bước 4: Xuất Video"
    };

    function escapeHtml(text) {
        if (!text) return "";
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // ------------------------------------------
    // CONFIRM DIALOG SYSTEM
    // ------------------------------------------
    let confirmResolver = null;
    function showConfirmDialog(title, message, isDanger = false) {
        return new Promise((resolve) => {
            confirmResolver = resolve;
            if (confirmModalTitle) confirmModalTitle.textContent = title || "Xác Nhận Thao Tác";
            if (confirmModalMessage) confirmModalMessage.textContent = message || "Bạn có chắc chắn muốn thực hiện thao tác này?";
            if (confirmModalIcon) {
                confirmModalIcon.className = isDanger ? "fa-solid fa-triangle-exclamation icon-yellow text-danger" : "fa-solid fa-circle-question icon-purple";
            }
            if (btnConfirmOk) {
                btnConfirmOk.className = isDanger ? "primary-btn btn-danger" : "primary-btn btn-accent";
                btnConfirmOk.textContent = isDanger ? "Xóa Vĩnh Viễn" : "Đồng Ý";
            }
            if (modalConfirm) modalConfirm.classList.remove("d-none");
        });
    }

    function closeConfirmDialog(result = false) {
        if (modalConfirm) modalConfirm.classList.add("d-none");
        if (confirmResolver) {
            confirmResolver(result);
            confirmResolver = null;
        }
    }

    if (btnConfirmOk) btnConfirmOk.addEventListener("click", () => closeConfirmDialog(true));
    if (btnConfirmCancel) btnConfirmCancel.addEventListener("click", () => closeConfirmDialog(false));
    if (btnConfirmCancelX) btnConfirmCancelX.addEventListener("click", () => closeConfirmDialog(false));
    if (modalConfirm) {
        modalConfirm.addEventListener("click", (e) => {
            if (e.target === modalConfirm) closeConfirmDialog(false);
        });
    }

    // ------------------------------------------
    // SAVE STATUS & PROJECT BAR UI CONTROLLER
    // ------------------------------------------
    function setSaveStatus(status, customText = "") {
        if (!projectSaveStatus) return;
        projectSaveStatus.className = "project-save-status";
        if (status === "saving") {
            projectSaveStatus.classList.add("saving");
            projectSaveStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span id="project-save-text">Đang tự động lưu...</span>`;
        } else if (status === "saved") {
            const now = new Date();
            const timeStr = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;
            projectSaveStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span id="project-save-text">${customText || `Đã tự động lưu lúc ${timeStr}`}</span>`;
        } else if (status === "error") {
            projectSaveStatus.classList.add("error");
            projectSaveStatus.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> <span id="project-save-text">Lỗi khi lưu dự án</span>`;
        }
    }

    function updateProjectBarUI() {
        if (projectNameDisplay) {
            projectNameDisplay.textContent = (currentProjectMeta && currentProjectMeta.name) ? currentProjectMeta.name : "Dự án mới";
        }
        if (projectStepIndicator) {
            projectStepIndicator.textContent = STEP_NAMES[currentStudioStep] || `Bước ${currentStudioStep}`;
        }
    }

    async function autoSaveProjectState(extraUpdates = {}) {
        if (!currentProjectId) return;
        setSaveStatus("saving");
        try {
            const payload = {
                current_step: currentStudioStep,
                video_url: videoUrlInput ? videoUrlInput.value.trim() : "",
                bilibili_cookie: bilibiliCookieInput ? bilibiliCookieInput.value.trim() : null,
                mode: currentTranscribeMode,
                mask_box: {
                    x: maskBoxCoords.x,
                    y: maskBoxCoords.y,
                    w: maskBoxCoords.w,
                    h: maskBoxCoords.h,
                    enabled: maskEnabledCheckStep ? maskEnabledCheckStep.checked : true,
                    style: maskStyleSelectStep ? maskStyleSelectStep.value : "blur"
                },
                sub_box: {
                    x: subBoxCoords.x,
                    y: subBoxCoords.y,
                    w: subBoxCoords.w,
                    h: subBoxCoords.h
                },
                sub_styling: {
                    font_size: parseInt(subStylingState.font_size || 30),
                    font_name: subStylingState.font_name || "Nunito",
                    primary_color: subStylingState.primary_color || "#FFFFFF",
                    outline_color: subStylingState.outline_color || "#000000",
                    outline_width: parseFloat(subStylingState.outline_width ?? 3.5),
                    box_style: subStylingState.box_style || "outline",
                    back_color: subStylingState.back_color || "#000000",
                    box_opacity: parseFloat(subStylingState.box_opacity ?? 0.75),
                    bold: Boolean(subStylingState.bold)
                },
                voice: voiceSelectStep3 ? voiceSelectStep3.value : "female_hoaimy",
                rvc_model: rvcModelSelectStep3 ? rvcModelSelectStep3.value : "none",
                rvc_pitch: rvcPitchSlider ? parseInt(rvcPitchSlider.value) : 0,
                bg_volume: bgVolumeSlider ? parseFloat(bgVolumeSlider.value) : 0.15,
                tts_volume: ttsVolumeSlider ? parseFloat(ttsVolumeSlider.value) : 1.0,
                auto_extend_video: document.getElementById("chk-auto-extend-video") ? document.getElementById("chk-auto-extend-video").checked : false,
                ...extraUpdates
            };

            const res = await fetch(`/api/projects/${currentProjectId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                currentProjectMeta = await res.json();
                updateProjectBarUI();
                setSaveStatus("saved");
            } else {
                setSaveStatus("error");
            }
        } catch (e) {
            console.warn("Auto-save error", e);
            setSaveStatus("error");
        }
    }

    function triggerDebouncedAutoSave(delayMs = 1200) {
        if (!currentProjectId) return;
        if (autoSaveTimer) clearTimeout(autoSaveTimer);
        setSaveStatus("saving");
        autoSaveTimer = setTimeout(() => {
            autoSaveProjectState();
        }, delayMs);
    }

    // ------------------------------------------
    // PROJECT CRUD OPERATIONS
    // ------------------------------------------
    async function createNewProject(promptConfirm = true) {
        if (promptConfirm && currentProjectId && (segmentsData.length > 0 || (videoUrlInput && videoUrlInput.value))) {
            const confirmed = await showConfirmDialog(
                "Tạo Dự Án Mới?",
                "Dự án hiện tại đã được tự động lưu. Bạn có muốn tạo một dự án mới tinh không?"
            );
            if (!confirmed) return;
        }

        try {
            setSaveStatus("saving");
            const res = await fetch("/api/projects", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            if (!res.ok) throw new Error("Không thể tạo dự án.");
            const meta = await res.json();

            currentProjectId = meta.id;
            currentProjectMeta = meta;
            localStorage.setItem("current_project_id", meta.id);

            // Reset inputs & preview
            if (videoUrlInput) videoUrlInput.value = "";
            if (btnClearUrl) btnClearUrl.classList.add("d-none");
            if (previewVideoElement) previewVideoElement.src = "";
            if (videoPreview) videoPreview.src = "";
            if (canvasWatermark) canvasWatermark.classList.remove("d-none");
            if (subtitleEditorCard) subtitleEditorCard.classList.add("d-none");
            segmentsData = [];
            if (subtitleTableBody) subtitleTableBody.innerHTML = "";
            showState("idle");

            // Lock steps 2, 3, 4
            [2, 3, 4].forEach(stepNum => {
                const tab = document.getElementById(`tab-step-${stepNum}`);
                if (tab) {
                    tab.classList.add("locked");
                    tab.classList.remove("done");
                    tab.classList.remove("active");
                }
            });
            const tab1 = document.getElementById("tab-step-1");
            if (tab1) tab1.classList.remove("done");
            switchStep(1);

            updateProjectBarUI();
            setSaveStatus("saved", "Đã khởi tạo dự án mới");

            if (modalProjects) modalProjects.classList.add("d-none");
        } catch (e) {
            console.error("Create project error", e);
            alert("Lỗi khi tạo dự án: " + e.message);
        }
    }

    async function openProject(projectId, promptConfirm = false) {
        if (promptConfirm && currentProjectId && currentProjectId !== projectId && (segmentsData.length > 0 || (videoUrlInput && videoUrlInput.value))) {
            const confirmed = await showConfirmDialog(
                "Mở Dự Án Khác?",
                "Dự án hiện tại đã được tự động lưu. Bạn có muốn chuyển sang dự án này không?"
            );
            if (!confirmed) return;
        }

        try {
            setSaveStatus("saving");
            const res = await fetch(`/api/projects/${projectId}`);
            if (!res.ok) throw new Error("Không tìm thấy dự án.");
            const meta = await res.json();

            currentProjectId = meta.id;
            currentProjectMeta = meta;
            localStorage.setItem("current_project_id", meta.id);

            // Populate video inputs
            if (videoUrlInput) videoUrlInput.value = meta.video_url || "";
            if (btnClearUrl) btnClearUrl.classList.toggle("d-none", !meta.video_url);
            if (bilibiliCookieInput) bilibiliCookieInput.value = meta.bilibili_cookie || "";

            // Populate mode
            currentTranscribeMode = meta.mode || "ocr";
            if (btnModeOcr && btnModeWhisper) {
                btnModeOcr.classList.toggle("active", currentTranscribeMode === "ocr");
                btnModeWhisper.classList.toggle("active", currentTranscribeMode === "whisper");
                if (step2OcrOptions) step2OcrOptions.classList.toggle("d-none", currentTranscribeMode !== "ocr");
                if (step2WhisperOptions) step2WhisperOptions.classList.toggle("d-none", currentTranscribeMode === "ocr");
            }

            // Populate boxes
            if (meta.mask_box) {
                maskBoxCoords = {
                    x: meta.mask_box.x ?? 10,
                    y: meta.mask_box.y ?? 78,
                    w: meta.mask_box.w ?? 80,
                    h: meta.mask_box.h ?? 14
                };
                if (maskEnabledCheckStep && meta.mask_box.enabled !== undefined) {
                    maskEnabledCheckStep.checked = meta.mask_box.enabled;
                }
                if (maskStyleSelectStep && meta.mask_box.style) {
                    maskStyleSelectStep.value = meta.mask_box.style;
                }
                applyMaskVisualPreview();
            }
            if (meta.sub_box) {
                subBoxCoords = {
                    x: meta.sub_box.x ?? 10,
                    y: meta.sub_box.y ?? 78,
                    w: meta.sub_box.w ?? 80,
                    h: meta.sub_box.h ?? 14
                };
            }
            applyBoxStyles();

            // Populate voice & sliders
            if (meta.voice && voiceSelectStep3) voiceSelectStep3.value = meta.voice;
            if (meta.rvc_model && rvcModelSelectStep3) {
                rvcModelSelectStep3.value = meta.rvc_model;
                if (typeof updateRvcPitchVisibility === "function") updateRvcPitchVisibility();
            }
            if (meta.rvc_pitch !== undefined && rvcPitchSlider) {
                rvcPitchSlider.value = meta.rvc_pitch;
                if (rvcPitchVal) rvcPitchVal.textContent = meta.rvc_pitch > 0 ? `+${meta.rvc_pitch}` : meta.rvc_pitch;
            }
            if (meta.bg_volume !== undefined && bgVolumeSlider) {
                bgVolumeSlider.value = meta.bg_volume;
                if (bgVolLabel) bgVolLabel.textContent = `${Math.round(meta.bg_volume * 100)}%`;
                syncPreviewVideoVolume();
            }
            if (meta.tts_volume !== undefined && ttsVolumeSlider) {
                ttsVolumeSlider.value = meta.tts_volume;
                if (ttsVolLabel) ttsVolLabel.textContent = `${Math.round(meta.tts_volume * 100)}%`;
            }

            // Populate sub styling
            if (meta.sub_styling) {
                Object.assign(subStylingState, meta.sub_styling);
                if (!subStylingState.font_size) {
                    subStylingState.font_size = 48;
                    subStylingState.outline_width = 4.0;
                }
                applySubStylingToUI();
            }

            // Populate Auto-Extend toggle
            if (meta.auto_extend_video !== undefined) {
                const chkAutoExtend = document.getElementById("chk-auto-extend-video");
                if (chkAutoExtend) {
                    chkAutoExtend.checked = Boolean(meta.auto_extend_video);
                    const sumAutoExtend = document.getElementById("summary-auto-extend");
                    if (sumAutoExtend) {
                        sumAutoExtend.textContent = chkAutoExtend.checked ? "Đang bật (Chống mất từ)" : "Đã tắt (Giữ nguyên gốc)";
                        sumAutoExtend.className = chkAutoExtend.checked ? "summary-val text-success" : "summary-val";
                    }
                }
            }

            // Load segments
            segmentsData = meta.segments || [];
            if (segmentsData.length > 0) {
                renderSegmentsTable(segmentsData);
            } else if (subtitleEditorCard) {
                subtitleEditorCard.classList.add("d-none");
            }

            // Load Video Preview
            if (meta.has_raw_video && previewVideoElement) {
                previewVideoElement.src = `/api/project/${meta.id}/video-raw`;
                previewVideoElement.load();
                if (canvasWatermark) canvasWatermark.classList.add("d-none");
            } else if (previewVideoElement) {
                previewVideoElement.src = "";
                if (canvasWatermark) canvasWatermark.classList.remove("d-none");
            }

            // Unlock completed steps
            const completed = meta.completed_steps || [];
            [1, 2, 3, 4].forEach(s => {
                const tab = document.getElementById(`tab-step-${s}`);
                if (tab) {
                    if (completed.includes(s)) {
                        tab.classList.remove("locked");
                        tab.classList.add("done");
                    } else if (s === (meta.current_step || 1)) {
                        tab.classList.remove("locked");
                    } else if (s > (meta.current_step || 1)) {
                        tab.classList.add("locked");
                        tab.classList.remove("done");
                    }
                }
            });

            // Target step navigation
            const targetStep = meta.current_step || (completed.length > 0 ? Math.min(Math.max(...completed) + 1, 4) : 1);
            unlockStep(targetStep);
            switchStep(targetStep);

            // If finished, show success state
            if (meta.status === "completed" && meta.has_dubbed_video) {
                showState("success");
                if (videoPreview) {
                    videoPreview.src = `/api/project/${meta.id}/video-dubbed`;
                    videoPreview.load();
                }
                if (downloadBtn) downloadBtn.href = `/api/project/${meta.id}/download`;
                if (downloadSrtBtn) downloadSrtBtn.href = `/api/project/${meta.id}/subtitles`;
            } else {
                showState("idle");
            }

            updateProjectBarUI();
            setSaveStatus("saved", "Đã mở dự án thành công");

            if (modalProjects) modalProjects.classList.add("d-none");
        } catch (e) {
            console.error("Open project error", e);
            alert("Không thể mở dự án: " + e.message);
        }
    }

    async function fetchProjectsList(searchQuery = "") {
        if (!projectListContainer) return;
        projectListContainer.innerHTML = `<div style="text-align:center; padding: 2.5rem; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Đang tải danh sách...</div>`;
        try {
            const res = await fetch("/api/projects");
            if (!res.ok) throw new Error("Không thể tải danh sách dự án.");
            let list = await res.json();

            if (searchQuery && searchQuery.trim()) {
                const q = searchQuery.toLowerCase().trim();
                list = list.filter(p => (p.name || "").toLowerCase().includes(q) || (p.video_url || "").toLowerCase().includes(q));
            }

            if (list.length === 0) {
                projectListContainer.innerHTML = "";
                if (projectListEmpty) projectListEmpty.classList.remove("d-none");
                return;
            }

            if (projectListEmpty) projectListEmpty.classList.add("d-none");
            projectListContainer.innerHTML = "";

            list.forEach(p => {
                const card = document.createElement("div");
                card.className = "project-card";
                if (p.id === currentProjectId) {
                    card.classList.add("active-project");
                }

                let statusBadgeHTML = "";
                if (p.status === "completed") {
                    statusBadgeHTML = `<span class="project-card-status-badge status-badge-done"><i class="fa-solid fa-check"></i> Hoàn Thành</span>`;
                } else if (p.current_step > 1 || (p.completed_steps && p.completed_steps.length > 0)) {
                    statusBadgeHTML = `<span class="project-card-status-badge status-badge-progress">Đang làm: Bước ${p.current_step || 1}</span>`;
                } else {
                    statusBadgeHTML = `<span class="project-card-status-badge status-badge-draft">Mới tạo</span>`;
                }

                const updatedDate = p.updated_at ? new Date(p.updated_at) : new Date();
                const dateStr = `${updatedDate.toLocaleDateString("vi-VN")} ${updatedDate.getHours().toString().padStart(2, "0")}:${updatedDate.getMinutes().toString().padStart(2, "0")}`;

                card.innerHTML = `
                    <div class="project-card-main">
                        <div class="project-card-header">
                            <span class="project-card-title">${escapeHtml(p.name || "Dự án không tên")}</span>
                            ${statusBadgeHTML}
                        </div>
                        <div class="project-card-meta">
                            <span class="project-card-meta-item"><i class="fa-regular fa-clock"></i> Sửa: ${dateStr}</span>
                            <span class="project-card-meta-item"><i class="fa-solid fa-closed-captioning"></i> ${p.segments_count || 0} câu sub</span>
                            ${p.has_raw_video ? '<span class="project-card-meta-item text-success"><i class="fa-solid fa-video"></i> Video gốc</span>' : ''}
                            ${p.has_dubbed_video ? '<span class="project-card-meta-item text-success"><i class="fa-solid fa-film"></i> Đã xuất MP4</span>' : ''}
                            ${p.video_url ? `<span class="project-card-url" title="${escapeHtml(p.video_url)}"><i class="fa-solid fa-link"></i> ${escapeHtml(p.video_url)}</span>` : ''}
                        </div>
                    </div>
                    <div class="project-card-actions">
                        <button type="button" class="primary-btn btn-sm btn-card-open" data-id="${p.id}">
                            <i class="fa-solid fa-folder-open"></i> Mở
                        </button>
                        <button type="button" class="btn-card-del" data-id="${p.id}" title="Xóa dự án">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                `;

                card.querySelector(".btn-card-open").addEventListener("click", (e) => {
                    e.stopPropagation();
                    openProject(p.id, true);
                });
                card.addEventListener("click", () => {
                    openProject(p.id, true);
                });

                card.querySelector(".btn-card-del").addEventListener("click", async (e) => {
                    e.stopPropagation();
                    const confirmed = await showConfirmDialog(
                        "Xóa Dự Án?",
                        `Bạn có chắc chắn muốn xóa vĩnh viễn dự án "${p.name || 'này'}" và toàn bộ file video, phụ đề liên quan không?`,
                        true
                    );
                    if (!confirmed) return;

                    try {
                        const delRes = await fetch(`/api/projects/${p.id}`, { method: "DELETE" });
                        if (delRes.ok) {
                            if (currentProjectId === p.id) {
                                await createNewProject(false);
                            }
                            fetchProjectsList(projectSearchInput ? projectSearchInput.value : "");
                        } else {
                            alert("Xóa dự án thất bại.");
                        }
                    } catch (err) {
                        alert("Lỗi khi xóa: " + err.message);
                    }
                });

                projectListContainer.appendChild(card);
            });
        } catch (e) {
            projectListContainer.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--error);">Không thể nạp danh sách: ${e.message}</div>`;
        }
    }

    // Project Bar & Modal Button Listeners
    if (btnProjectOpen) {
        btnProjectOpen.addEventListener("click", () => {
            if (modalProjects) modalProjects.classList.remove("d-none");
            if (projectSearchInput) projectSearchInput.value = "";
            fetchProjectsList();
        });
    }
    if (btnCloseProjectModal) {
        btnCloseProjectModal.addEventListener("click", () => {
            if (modalProjects) modalProjects.classList.add("d-none");
        });
    }
    if (modalProjects) {
        modalProjects.addEventListener("click", (e) => {
            if (e.target === modalProjects) modalProjects.classList.add("d-none");
        });
    }
    if (projectSearchInput) {
        projectSearchInput.addEventListener("input", () => {
            fetchProjectsList(projectSearchInput.value);
        });
    }
    if (btnProjectNew) btnProjectNew.addEventListener("click", () => createNewProject(true));
    if (btnModalCreateNew) btnModalCreateNew.addEventListener("click", () => createNewProject(true));

    if (btnProjectSaveManual) {
        btnProjectSaveManual.addEventListener("click", async () => {
            const origHTML = btnProjectSaveManual.innerHTML;
            btnProjectSaveManual.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Đang lưu...</span>`;
            await saveSegmentsToServer();
            await autoSaveProjectState();
            setTimeout(() => {
                btnProjectSaveManual.innerHTML = `<i class="fa-solid fa-check"></i> <span>Đã lưu!</span>`;
                setTimeout(() => {
                    btnProjectSaveManual.innerHTML = origHTML;
                }, 1200);
            }, 300);
        });
    }

    // Inline editing Project Name
    if (btnEditProjectName && projectNameDisplay && projectNameInput) {
        function startEditProjectName() {
            projectNameInput.value = projectNameDisplay.textContent.trim();
            projectNameDisplay.classList.add("d-none");
            btnEditProjectName.classList.add("d-none");
            projectNameInput.classList.remove("d-none");
            projectNameInput.focus();
            projectNameInput.select();
        }

        async function finishEditProjectName() {
            const newName = projectNameInput.value.trim();
            projectNameInput.classList.add("d-none");
            projectNameDisplay.classList.remove("d-none");
            btnEditProjectName.classList.remove("d-none");

            if (newName && currentProjectId && (!currentProjectMeta || currentProjectMeta.name !== newName)) {
                projectNameDisplay.textContent = newName;
                await autoSaveProjectState({ name: newName });
            }
        }

        btnEditProjectName.addEventListener("click", (e) => {
            e.stopPropagation();
            startEditProjectName();
        });
        projectNameDisplay.addEventListener("click", startEditProjectName);

        projectNameInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                finishEditProjectName();
            } else if (e.key === "Escape") {
                projectNameInput.classList.add("d-none");
                projectNameDisplay.classList.remove("d-none");
                btnEditProjectName.classList.remove("d-none");
            }
        });
        projectNameInput.addEventListener("blur", finishEditProjectName);
    }

    // ------------------------------------------
    // BOUNDING BOX & STEP VISIBILITY CONTROLLER
    // ------------------------------------------
    function updateBBoxVisibility() {
        if (!bboxMask || !bboxSub) return;

        if (currentStudioStep === 1) {
            // Bước 1: Ẩn cả 2 khung
            bboxMask.classList.add("d-none");
            bboxSub.classList.add("d-none");
        } else if (currentStudioStep === 2) {
            // Bước 2: Chỉ hiện khung OCR tiếng Trung (nếu chọn mode OCR), KHÔNG hiện khung Sub Việt
            bboxSub.classList.add("d-none");
            if (currentTranscribeMode === "ocr") {
                bboxMask.classList.remove("d-none");
            } else {
                bboxMask.classList.add("d-none");
            }
        } else if (currentStudioStep === 3 || currentStudioStep === 4) {
            // Bước 3 & 4: Hiện khung Sub Việt để căn vị trí & hiển thị hiệu ứng che mờ
            bboxSub.classList.remove("d-none");
            // Khung đỏ OCR cũ mặc định ẩn, trừ khi người dùng bật nút "Hiện khung đỏ"
            if (!btnToggleMaskBoxPreview || !btnToggleMaskBoxPreview.classList.contains("active")) {
                bboxMask.classList.add("d-none");
            } else {
                bboxMask.classList.remove("d-none");
            }
        }
        applyMaskVisualPreview();
    }

    function switchStep(stepNum) {
        currentStudioStep = stepNum;

        // Cập nhật trạng thái active của các nút Tabs
        stepTabBtns.forEach(btn => {
            const step = parseInt(btn.getAttribute("data-step"));
            btn.classList.toggle("active", step === stepNum);
        });

        // Cập nhật nội dung tab tương ứng
        stepTabContents.forEach(content => {
            const isTarget = content.id === `content-step-${stepNum}`;
            content.classList.toggle("d-none", !isTarget);
            content.classList.toggle("active", isTarget);
        });

        // Đồng bộ hiển thị Bounding Box
        updateBBoxVisibility();

        // Hiển thị / ẩn bảng phụ đề bên dưới player
        if (subtitleEditorCard) {
            if ((stepNum === 3 || stepNum === 4) && segmentsData && segmentsData.length > 0) {
                subtitleEditorCard.classList.remove("d-none");
            } else if (stepNum < 3) {
                subtitleEditorCard.classList.add("d-none");
            }
        }

        // Cập nhật tóm tắt khi sang Bước 4
        if (stepNum === 4) {
            updateStep4Summary();
        } else if (stepNum === 3) {
            syncPreviewVideoVolume();
            loadPreviewDubbedAudio(false);
        }

        updateProjectBarUI();
        if (currentProjectId) {
            triggerDebouncedAutoSave(1500);
        }
    }

    function unlockStep(stepNum) {
        const tabBtn = document.getElementById(`tab-step-${stepNum}`);
        if (tabBtn) {
            tabBtn.classList.remove("locked");
        }
    }

    function markStepDone(stepNum) {
        const tabBtn = document.getElementById(`tab-step-${stepNum}`);
        if (tabBtn) {
            tabBtn.classList.add("done");
        }
    }

    // Gắn sự kiện click cho các nút Tabs - cho phép chuyển tab tự do
    stepTabBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            const step = parseInt(btn.getAttribute("data-step"));
            if (step) {
                switchStep(step);
            }
        });
    });

    function updateStep4Summary() {
        if (summarySubCount) {
            summarySubCount.textContent = segmentsData.length > 0 ? `${segmentsData.length} câu đã dịch` : "Đã sẵn sàng";
        }
        if (summaryVoiceName && voiceSelectStep3) {
            const opt = voiceSelectStep3.options[voiceSelectStep3.selectedIndex];
            summaryVoiceName.textContent = opt ? opt.text : "Hoài My (Nữ chuẩn)";
        }
    }

    function cleanBilibiliUrl(rawUrl) {
        if (!rawUrl) return "";
        let u = rawUrl.trim();
        if (u.includes("bilibili.com")) {
            u = u.replace(/bilibili\.com\/[a-z]{2}(?:-[a-z]{2,4})?\/video\//, "bilibili.com/video/");
            const pMatch = u.match(/[?&](p=\d+)/);
            const cleanBase = u.split("?")[0].replace(/\/$/, "");
            u = pMatch ? `${cleanBase}?${pMatch[1]}` : cleanBase;
        }
        return u;
    }

    // 1. URL Input paste & clear
    if (btnPasteUrl && videoUrlInput) {
        btnPasteUrl.addEventListener("click", async () => {
            try {
                const text = await navigator.clipboard.readText();
                if (text) {
                    videoUrlInput.value = cleanBilibiliUrl(text);
                    if (btnClearUrl) btnClearUrl.classList.remove("d-none");
                }
            } catch (e) {
                console.warn("Clipboard access denied", e);
            }
        });
    }
    if (videoUrlInput && btnClearUrl) {
        videoUrlInput.addEventListener("input", () => {
            btnClearUrl.classList.toggle("d-none", !videoUrlInput.value);
        });
        videoUrlInput.addEventListener("blur", () => {
            if (videoUrlInput.value) {
                videoUrlInput.value = cleanBilibiliUrl(videoUrlInput.value);
            }
        });
        btnClearUrl.addEventListener("click", () => {
            videoUrlInput.value = "";
            btnClearUrl.classList.add("d-none");
            videoUrlInput.focus();
        });
    }
    if (btnToggleCookie && cookiePanel) {
        btnToggleCookie.addEventListener("click", () => {
            cookiePanel.classList.toggle("d-none");
            const arrow = btnToggleCookie.querySelector(".toggle-arrow");
            if (arrow) arrow.classList.toggle("fa-chevron-up");
        });
    }

    // 2. Bước 1: Tải Video
    if (btnStep1Download) {
        btnStep1Download.addEventListener("click", async () => {
            let url = videoUrlInput ? videoUrlInput.value.trim() : "";
            url = cleanBilibiliUrl(url);
            if (videoUrlInput) videoUrlInput.value = url;
            if (!url) {
                alert("Vui lòng nhập link video.");
                return;
            }
            const cookie = bilibiliCookieInput ? bilibiliCookieInput.value.trim() : "";

            btnStep1Download.disabled = true;
            if (step1ProgressBox) step1ProgressBox.classList.remove("d-none");
            if (step1ProgressBar) step1ProgressBar.style.width = "5%";
            if (step1ProgressPct) step1ProgressPct.textContent = "5%";
            if (step1ProgressMsg) step1ProgressMsg.textContent = "Đang kết nối...";

            try {
                const res = await fetch("/api/project/download", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        url: url,
                        bilibili_cookie: cookie || null,
                        project_id: currentProjectId || null
                    })
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể tải video.");
                }
                const data = await res.json();
                currentProjectId = data.project_id;
                currentProjectMeta = data.project || currentProjectMeta;
                localStorage.setItem("current_project_id", currentProjectId);
                updateProjectBarUI();

                if (pollingInterval) clearInterval(pollingInterval);
                pollingInterval = setInterval(async () => {
                    try {
                        const statusRes = await fetch(`/api/project/${currentProjectId}/status`);
                        if (!statusRes.ok) return;
                        const statusData = await statusRes.json();
                        
                        if (step1ProgressBar) step1ProgressBar.style.width = `${statusData.progress || 0}%`;
                        if (step1ProgressPct) step1ProgressPct.textContent = `${statusData.progress || 0}%`;
                        if (step1ProgressMsg) step1ProgressMsg.textContent = statusData.message || "Đang tải...";

                        if (statusData.status === "downloaded") {
                            clearInterval(pollingInterval);
                            btnStep1Download.disabled = false;
                            if (step1ProgressBox) step1ProgressBox.classList.add("d-none");
                            
                            // Load video thật vào player xem trước
                            if (previewVideoElement) {
                                previewVideoElement.src = `/api/project/${currentProjectId}/video-raw`;
                                previewVideoElement.load();
                            }
                            if (canvasWatermark) {
                                canvasWatermark.classList.add("d-none");
                            }

                            currentProjectMeta = statusData.project || currentProjectMeta;
                            setSaveStatus("saved", "Đã tải xong & tự động lưu");
                            // Đánh dấu xong bước 1, mở khóa và chuyển sang bước 2
                            markStepDone(1);
                            unlockStep(2);
                            switchStep(2);
                        } else if (statusData.status === "download_failed") {
                            clearInterval(pollingInterval);
                            btnStep1Download.disabled = false;
                            if (step1ProgressBox) step1ProgressBox.classList.add("d-none");
                            if (cookiePanel && (statusData.error || "").includes("Cookie")) {
                                cookiePanel.classList.remove("d-none");
                                if (bilibiliCookieInput) bilibiliCookieInput.focus();
                            }
                            alert("Tải video thất bại:\n\n" + (statusData.error || statusData.message));
                        }
                    } catch (e) {
                        console.error(e);
                    }
                }, 800);
            } catch (err) {
                btnStep1Download.disabled = false;
                if (step1ProgressBox) step1ProgressBox.classList.add("d-none");
                alert(err.message);
            }
        });
    }

    // 3. Bước 2: Mode Toggle & Quét Chữ
    if (btnModeOcr && btnModeWhisper) {
        btnModeOcr.addEventListener("click", () => {
            currentTranscribeMode = "ocr";
            btnModeOcr.classList.add("active");
            btnModeWhisper.classList.remove("active");
            if (step2OcrOptions) step2OcrOptions.classList.remove("d-none");
            if (step2WhisperOptions) step2WhisperOptions.classList.add("d-none");
            updateBBoxVisibility();
        });
        btnModeWhisper.addEventListener("click", () => {
            currentTranscribeMode = "whisper";
            btnModeWhisper.classList.add("active");
            btnModeOcr.classList.remove("active");
            if (step2OcrOptions) step2OcrOptions.classList.add("d-none");
            if (step2WhisperOptions) step2WhisperOptions.classList.remove("d-none");
            updateBBoxVisibility();
        });
    }

    // Nút căn đáy chuẩn nhanh ở Bước 2
    if (btnPresetBottomStep) {
        btnPresetBottomStep.addEventListener("click", () => {
            maskBoxCoords = { x: 10, y: 78, w: 80, h: 14 };
            if (isLocked) {
                subBoxCoords = { ...maskBoxCoords };
            }
            applyBoxStyles();
        });
    }

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
    }

    function getDurationBadgeHTML(text, duration) {
        const trimmed = (text || "").trim();
        if (!trimmed) {
            return `<span class="badge-pace badge-empty"><i class="fa-solid fa-volume-xmark"></i> Bỏ trống (Không đọc câu này)</span>`;
        }
        const words = trimmed.split(/\s+/).filter(Boolean).length;
        const dur = Math.max(0.1, duration);
        const pace = words / dur;
        
        if (pace <= 3.8) {
            return `<span class="badge-pace badge-good" title="Tốc độ tự nhiên, rõ từng chữ"><i class="fa-solid fa-circle-check"></i> ${words} từ / ${dur.toFixed(1)}s • Chuẩn tự nhiên 1.0x</span>`;
        } else if (pace <= 4.8) {
            return `<span class="badge-pace badge-warn" title="Hơi nhiều từ, sẽ đọc nhanh hơn một chút"><i class="fa-solid fa-triangle-exclamation"></i> ${words} từ / ${dur.toFixed(1)}s • Đọc nhanh ~${(pace/3.4).toFixed(1)}x</span>`;
        } else {
            return `<span class="badge-pace badge-danger" title="Quá nhiều từ so với số giây video! Nên gọt bớt chữ để giọng đọc rõ nét"><i class="fa-solid fa-bolt"></i> ${words} từ / ${dur.toFixed(1)}s • Quá dài (~${(pace/3.4).toFixed(1)}x)! Nên rút gọn</span>`;
        }
    }

    function renderSegmentsTable(segments) {
        segmentsData = segments;
        if (!subtitleTableBody) return;
        subtitleTableBody.innerHTML = "";
        if (segmentsCount) segmentsCount.textContent = segments.length;

        segments.forEach((seg, index) => {
            const tr = document.createElement("tr");
            const startVal = seg.start != null ? Number(seg.start).toFixed(1) : "0.0";
            const endVal = seg.end != null ? Number(seg.end).toFixed(1) : "0.0";
            const dur = Math.max(0.1, Number(endVal) - Number(startVal));
            const curSpeed = seg.speed != null ? Number(seg.speed) : 1.0;

            tr.innerHTML = `
                <td><strong>${index + 1}</strong></td>
                <td>
                    <div class="time-edit-group">
                        <div class="time-inputs-row">
                            <input type="number" step="0.1" min="0" class="time-num-input seg-start-input" data-index="${index}" value="${startVal}" title="Thời gian bắt đầu (giây)">
                            <span class="time-sep">-</span>
                            <input type="number" step="0.1" min="0" class="time-num-input seg-end-input" data-index="${index}" value="${endVal}" title="Thời gian kết thúc (giây)">
                        </div>
                        <div class="time-nudge-bar">
                            <button type="button" class="btn-nudge btn-nudge-sub" data-index="${index}" title="Giảm 0.5s thời lượng">-0.5s</button>
                            <button type="button" class="btn-nudge btn-nudge-add" data-index="${index}" title="Tăng 0.5s thời lượng (thêm thời gian nói)">+0.5s</button>
                            <button type="button" class="btn-nudge-play" data-time="${seg.start}" title="Xem video tại câu này"><i class="fa-solid fa-play"></i></button>
                        </div>
                    </div>
                </td>
                <td>
                    <select class="seg-speed-select" data-index="${index}" title="Tốc độ đọc câu này">
                        <option value="0.9" ${curSpeed === 0.9 ? 'selected' : ''}>0.9x (Chậm)</option>
                        <option value="1.0" ${curSpeed === 1.0 ? 'selected' : ''}>1.0x (Chuẩn)</option>
                        <option value="1.1" ${curSpeed === 1.1 ? 'selected' : ''}>1.1x</option>
                        <option value="1.2" ${curSpeed === 1.2 ? 'selected' : ''}>1.2x</option>
                        <option value="1.3" ${curSpeed === 1.3 ? 'selected' : ''}>1.3x (Nhanh)</option>
                    </select>
                </td>
                <td style="color: #cbd5e1; font-size: 0.86rem;">${seg.text || ""}</td>
                <td>
                    <div class="sub-input-container">
                        <input type="text" class="sub-edit-input" data-index="${index}" value="${seg.translation ? seg.translation.replace(/"/g, '&quot;') : ''}" placeholder="Nhập bản dịch tiếng Việt (để trống = không đọc)...">
                        <div class="sub-duration-badge" id="sub-badge-${index}">${getDurationBadgeHTML(seg.translation, dur)}</div>
                    </div>
                </td>
                <td style="text-align: center;">
                    <button type="button" class="btn-table-action btn-tts" data-index="${index}" title="Nghe thử TTS câu này"><i class="fa-solid fa-volume-high"></i></button>
                    <button type="button" class="btn-table-action btn-del" data-index="${index}" title="Xóa dòng này"><i class="fa-solid fa-trash-can"></i></button>
                </td>
            `;
            subtitleTableBody.appendChild(tr);
        });

        // Time Nudge Play Button
        subtitleTableBody.querySelectorAll(".btn-nudge-play").forEach(btn => {
            btn.addEventListener("click", () => {
                const time = parseFloat(btn.dataset.time || 0);
                if (previewVideoElement) {
                    previewVideoElement.currentTime = time;
                    previewVideoElement.play();
                }
            });
        });

        // Start time input change
        subtitleTableBody.querySelectorAll(".seg-start-input").forEach(input => {
            input.addEventListener("change", () => {
                const idx = parseInt(input.dataset.index);
                const val = parseFloat(input.value);
                if (segmentsData[idx] && !isNaN(val) && val >= 0) {
                    segmentsData[idx].start = val;
                    const badge = document.getElementById(`sub-badge-${idx}`);
                    if (badge) {
                        const dur = Math.max(0.1, (segmentsData[idx].end || 0) - val);
                        badge.innerHTML = getDurationBadgeHTML(segmentsData[idx].translation, dur);
                    }
                    saveSegmentsToServer();
                    triggerDebouncedAutoSave(1000);
                }
            });
        });

        // End time input change
        subtitleTableBody.querySelectorAll(".seg-end-input").forEach(input => {
            input.addEventListener("change", () => {
                const idx = parseInt(input.dataset.index);
                const val = parseFloat(input.value);
                if (segmentsData[idx] && !isNaN(val) && val >= 0) {
                    segmentsData[idx].end = val;
                    const badge = document.getElementById(`sub-badge-${idx}`);
                    if (badge) {
                        const dur = Math.max(0.1, val - (segmentsData[idx].start || 0));
                        badge.innerHTML = getDurationBadgeHTML(segmentsData[idx].translation, dur);
                    }
                    saveSegmentsToServer();
                    triggerDebouncedAutoSave(1000);
                }
            });
        });

        // Nudge +0.5s button
        subtitleTableBody.querySelectorAll(".btn-nudge-add").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.index);
                if (segmentsData[idx]) {
                    const currentEnd = Number(segmentsData[idx].end || 0);
                    const newEnd = Math.round((currentEnd + 0.5) * 10) / 10;
                    segmentsData[idx].end = newEnd;
                    const endInput = subtitleTableBody.querySelector(`.seg-end-input[data-index="${idx}"]`);
                    if (endInput) endInput.value = newEnd.toFixed(1);
                    const badge = document.getElementById(`sub-badge-${idx}`);
                    if (badge) {
                        const dur = Math.max(0.1, newEnd - (segmentsData[idx].start || 0));
                        badge.innerHTML = getDurationBadgeHTML(segmentsData[idx].translation, dur);
                    }
                    saveSegmentsToServer();
                    triggerDebouncedAutoSave(1000);
                }
            });
        });

        // Nudge -0.5s button
        subtitleTableBody.querySelectorAll(".btn-nudge-sub").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.index);
                if (segmentsData[idx]) {
                    const currentEnd = Number(segmentsData[idx].end || 0);
                    const minEnd = (segmentsData[idx].start || 0) + 0.2;
                    const newEnd = Math.max(minEnd, Math.round((currentEnd - 0.5) * 10) / 10);
                    segmentsData[idx].end = newEnd;
                    const endInput = subtitleTableBody.querySelector(`.seg-end-input[data-index="${idx}"]`);
                    if (endInput) endInput.value = newEnd.toFixed(1);
                    const badge = document.getElementById(`sub-badge-${idx}`);
                    if (badge) {
                        const dur = Math.max(0.1, newEnd - (segmentsData[idx].start || 0));
                        badge.innerHTML = getDurationBadgeHTML(segmentsData[idx].translation, dur);
                    }
                    saveSegmentsToServer();
                    triggerDebouncedAutoSave(1000);
                }
            });
        });

        // Speed select change
        subtitleTableBody.querySelectorAll(".seg-speed-select").forEach(sel => {
            sel.addEventListener("change", () => {
                const idx = parseInt(sel.dataset.index);
                const val = parseFloat(sel.value);
                if (segmentsData[idx] && !isNaN(val) && val > 0) {
                    segmentsData[idx].speed = val;
                    saveSegmentsToServer();
                    triggerDebouncedAutoSave(1000);
                }
            });
        });

        subtitleTableBody.querySelectorAll(".btn-tts").forEach(btn => {
            btn.addEventListener("click", async () => {
                const idx = parseInt(btn.dataset.index);
                const input = subtitleTableBody.querySelector(`.sub-edit-input[data-index="${idx}"]`);
                const text = input ? input.value.trim() : (segmentsData[idx]?.translation || "");
                if (!text) return;
                
                const voice = voiceSelectStep3 ? voiceSelectStep3.value : "female_hoaimy";
                btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
                try {
                    const res = await fetch("/api/tts-free", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text, voice })
                    });
                    if (res.ok) {
                        const blob = await res.blob();
                        const audioUrl = URL.createObjectURL(blob);
                        const audio = new Audio(audioUrl);
                        audio.play();
                    }
                } catch (e) {
                    console.error("TTS preview error", e);
                } finally {
                    btn.innerHTML = `<i class="fa-solid fa-volume-high"></i>`;
                }
            });
        });

        subtitleTableBody.querySelectorAll(".btn-del").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.index);
                segmentsData.splice(idx, 1);
                renderSegmentsTable(segmentsData);
                saveSegmentsToServer();
                triggerDebouncedAutoSave(500);
            });
        });

        subtitleTableBody.querySelectorAll(".sub-edit-input").forEach(input => {
            input.addEventListener("input", () => {
                if (step3SuccessBox) step3SuccessBox.classList.add("d-none");
                const idx = parseInt(input.dataset.index);
                if (segmentsData[idx]) {
                    segmentsData[idx].translation = input.value;
                    const badge = document.getElementById(`sub-badge-${idx}`);
                    if (badge) {
                        const dur = Math.max(0.1, (segmentsData[idx].end || 0) - (segmentsData[idx].start || 0));
                        badge.innerHTML = getDurationBadgeHTML(input.value, dur);
                    }
                }
                updatePreviewSubtitle();
                triggerDebouncedAutoSave(1500);
            });
            input.addEventListener("blur", () => {
                const idx = parseInt(input.dataset.index);
                if (segmentsData[idx]) {
                    segmentsData[idx].translation = input.value.trim();
                }
                saveSegmentsToServer();
            });
        });

        updatePreviewSubtitle();
        renderTimeline();

        if (subtitleEditorCard && (currentStudioStep === 3 || currentStudioStep === 4)) {
            subtitleEditorCard.classList.remove("d-none");
        }
    }

    function updatePreviewSubtitle() {
        if (!bboxSubPreviewText) return;
        if (!segmentsData || segmentsData.length === 0) {
            bboxSubPreviewText.textContent = "Phụ đề tiếng Việt mẫu";
            return;
        }

        const currentTime = previewVideoElement ? (previewVideoElement.currentTime || 0) : 0;
        // 1. Phụ đề khớp chính xác với giây đang phát/dừng trên video
        const activeSeg = segmentsData.find(s => currentTime >= s.start && currentTime <= s.end);
        if (activeSeg) {
            const txt = (activeSeg.translation !== undefined && activeSeg.translation !== null ? activeSeg.translation : activeSeg.text) || "";
            bboxSubPreviewText.textContent = txt || "Phụ đề tiếng Việt";
            return;
        }

        // 2. Tolerance window: trong vòng 0.8s sau khi câu trước vừa dứt
        const prevSeg = [...segmentsData].reverse().find(s => currentTime >= s.start);
        if (prevSeg && (currentTime - prevSeg.end < 0.8)) {
            const txt = prevSeg.translation || prevSeg.text || "";
            if (txt) {
                bboxSubPreviewText.textContent = txt;
                return;
            }
        }

        // 3. Fallback: Nếu video đang ở đoạn trống, hiện câu dịch đầu tiên hoặc gần nhất để người dùng luôn thấy mẫu trực quan
        const fallbackSeg = segmentsData.find(s => (s.translation || "").trim().length > 0) || segmentsData[0];
        if (fallbackSeg) {
            bboxSubPreviewText.textContent = fallbackSeg.translation || fallbackSeg.text || "Phụ đề tiếng Việt mẫu";
        } else {
            bboxSubPreviewText.textContent = "Phụ đề tiếng Việt mẫu";
        }
    }

    // ==========================================
    // REAL-TIME AUDIO DUBBING ENGINE FOR PREVIEW
    // ==========================================
    const dubbingAudio = new Audio();
    dubbingAudio.preload = "auto";
    let isDubbingEnabled = true;
    let isDubbingAudioLoaded = false;
    let isDubbingAudioLoading = false;
    let dubbingDebounceTimer = null;

    dubbingAudio.addEventListener("loadeddata", () => {
        isDubbingAudioLoaded = true;
        isDubbingAudioLoading = false;
        const lblTlDub = document.getElementById("lbl-tl-dub");
        if (lblTlDub && isDubbingEnabled) {
            lblTlDub.textContent = "Lồng tiếng (BẬT)";
        }
    });

    dubbingAudio.addEventListener("canplay", () => {
        isDubbingAudioLoaded = true;
        isDubbingAudioLoading = false;
    });

    dubbingAudio.addEventListener("error", (e) => {
        console.warn("Dubbing audio load warning:", e);
        isDubbingAudioLoaded = false;
        isDubbingAudioLoading = false;
        const lblTlDub = document.getElementById("lbl-tl-dub");
        if (lblTlDub && isDubbingEnabled) {
            lblTlDub.textContent = "Lồng tiếng (Đang tải...)";
        }
    });

    function getTTSVolume() {
        if (ttsVolumeSlider) {
            const v = parseFloat(ttsVolumeSlider.value);
            return isNaN(v) ? 1.0 : Math.max(0, Math.min(1, v));
        }
        return 1.0;
    }

    function loadPreviewDubbedAudio(autoPlay = false) {
        if (!currentProjectId) return;
        isDubbingAudioLoading = true;
        isDubbingAudioLoaded = false;

        const lblTlDub = document.getElementById("lbl-tl-dub");
        if (lblTlDub && isDubbingEnabled) {
            lblTlDub.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang tải giọng dịch...`;
        }

        const url = `/api/project/${currentProjectId}/preview-audio?t=${Date.now()}`;
        dubbingAudio.src = url;
        dubbingAudio.load();

        if (autoPlay) {
            const onCanPlay = () => {
                dubbingAudio.removeEventListener("canplay", onCanPlay);
                if (previewVideoElement && !previewVideoElement.paused && isDubbingEnabled) {
                    dubbingAudio.currentTime = previewVideoElement.currentTime;
                    dubbingAudio.volume = getTTSVolume();
                    syncPreviewVideoVolume();
                    dubbingAudio.play().catch(e => console.log("Dubbing audio autoPlay catch:", e));
                }
            };
            dubbingAudio.addEventListener("canplay", onCanPlay);
        }
    }

    async function refreshPreviewDubbedAudio() {
        if (!currentProjectId) return;
        setSaveStatus("saving", "Đang cập nhật âm thanh lồng tiếng xem trước...");
        const btnRef = document.getElementById("btn-tl-refresh-dub");
        if (btnRef) btnRef.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        try {
            const voice = voiceSelectStep3 ? voiceSelectStep3.value : "female_hoaimy";
            const rvc_model = rvcModelSelectStep3 ? rvcModelSelectStep3.value : "none";
            const rvc_pitch = rvcPitchSlider ? parseInt(rvcPitchSlider.value) : 0;
            const res = await fetch(`/api/project/${currentProjectId}/preview-audio`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ voice, rvc_model, rvc_pitch })
            });
            if (res.ok) {
                loadPreviewDubbedAudio(true);
                setSaveStatus("saved", "Đã cập nhật giọng lồng tiếng xem trước!");
            }
        } catch (e) {
            console.error("Refresh dubbing failed", e);
            setSaveStatus("error", "Lỗi tạo âm thanh xem trước.");
        } finally {
            if (btnRef) btnRef.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i>';
        }
    }

    function triggerDebouncedDubbingRefresh(ms = 2500) {
        if (dubbingDebounceTimer) clearTimeout(dubbingDebounceTimer);
        dubbingDebounceTimer = setTimeout(() => {
            refreshPreviewDubbedAudio();
        }, ms);
    }

    let lastDubSyncTime = 0;

    function playDubbingAudio() {
        if (!isDubbingEnabled || !currentProjectId) return;
        // Nếu video đang phát là video đã ghép âm thanh (video-dubbed), không phát thêm audio dubbing tránh nhân đôi âm thanh
        if (previewVideoElement && previewVideoElement.src && previewVideoElement.src.includes("video-dubbed")) {
            pauseDubbingAudio();
            return;
        }

        if (!dubbingAudio.src || dubbingAudio.src === "" || (!isDubbingAudioLoaded && !isDubbingAudioLoading)) {
            loadPreviewDubbedAudio(true);
            return;
        }

        // Nếu audio đang tải dở, chờ tải đủ buffer để phát đồng bộ ngay
        if (dubbingAudio.readyState < 2) {
            const onCanPlayNow = () => {
                dubbingAudio.removeEventListener("canplay", onCanPlayNow);
                if (previewVideoElement && !previewVideoElement.paused && isDubbingEnabled) {
                    dubbingAudio.currentTime = previewVideoElement.currentTime;
                    dubbingAudio.volume = getTTSVolume();
                    syncPreviewVideoVolume();
                    dubbingAudio.play().catch(e => console.log("Dubbing delayed play caught", e));
                }
            };
            dubbingAudio.addEventListener("canplay", onCanPlayNow);
            return;
        }

        const vTime = previewVideoElement ? (previewVideoElement.currentTime || 0) : 0;
        // Chỉ đặt lại currentTime nếu chênh lệch đáng kể (> 0.4s) để tránh giật lặp âm thanh
        if (Math.abs((dubbingAudio.currentTime || 0) - vTime) > 0.4) {
            dubbingAudio.currentTime = vTime;
        }
        dubbingAudio.volume = getTTSVolume();
        syncPreviewVideoVolume();
        dubbingAudio.play().catch(e => console.log("Dubbing play caught", e));
    }

    function pauseDubbingAudio() {
        if (dubbingAudio) {
            dubbingAudio.pause();
        }
    }

    function syncDubbingAudioSeek() {
        if (dubbingAudio && previewVideoElement) {
            if (previewVideoElement.src && previewVideoElement.src.includes("video-dubbed")) {
                pauseDubbingAudio();
                return;
            }
            dubbingAudio.currentTime = previewVideoElement.currentTime;
            if (!previewVideoElement.paused && isDubbingEnabled) {
                dubbingAudio.play().catch(e => {});
            }
        }
    }

    function syncDubbingAudioTime() {
        if (!isDubbingEnabled || !previewVideoElement || previewVideoElement.paused) return;
        if (previewVideoElement.src && previewVideoElement.src.includes("video-dubbed")) {
            pauseDubbingAudio();
            return;
        }
        const now = Date.now();
        // Chỉ can thiệp đồng bộ nếu chênh lệch lớn hơn 0.75s và cách lần can thiệp trước ít nhất 1.5s
        // Điều này ngăn chặn triệt để tình trạng lặp tiếng / duplicate âm thanh do liên tục tua lại
        if (dubbingAudio && Math.abs(dubbingAudio.currentTime - previewVideoElement.currentTime) > 0.75) {
            if (now - lastDubSyncTime > 1500) {
                lastDubSyncTime = now;
                dubbingAudio.currentTime = previewVideoElement.currentTime;
            }
        }
    }

    if (previewVideoElement) {
        previewVideoElement.addEventListener("timeupdate", () => {
            updatePreviewSubtitle();
            syncTimelinePlayhead();
            syncDubbingAudioTime();
        });
        previewVideoElement.addEventListener("seeked", () => {
            updatePreviewSubtitle();
            syncTimelinePlayhead();
            syncDubbingAudioSeek();
        });
        previewVideoElement.addEventListener("loadedmetadata", () => {
            syncPreviewVideoVolume();
            applySubStylingToUI();
            updatePreviewSubtitle();
            renderTimeline();
            loadPreviewDubbedAudio();
        });
        previewVideoElement.addEventListener("play", () => {
            syncPreviewVideoVolume();
            syncTimelinePlayhead();
            playDubbingAudio();
        });
        previewVideoElement.addEventListener("pause", () => {
            syncTimelinePlayhead();
            pauseDubbingAudio();
        });
        previewVideoElement.addEventListener("ended", () => {
            syncTimelinePlayhead();
            pauseDubbingAudio();
            if (dubbingAudio) dubbingAudio.currentTime = 0;
        });
    }

    // ==========================================
    // CAPCUT-STYLE TIMELINE EDITOR ENGINE
    // ==========================================
    const timelineEditorCard = document.getElementById("timeline-editor-card");
    const btnTlPlay = document.getElementById("btn-tl-play");
    const iconTlPlay = document.getElementById("icon-tl-play");
    const tlCurrentTime = document.getElementById("tl-current-time");
    const tlTotalTime = document.getElementById("tl-total-time");
    const btnTlSplit = document.getElementById("btn-tl-split");
    const btnTlMerge = document.getElementById("btn-tl-merge");
    const btnTlDelete = document.getElementById("btn-tl-delete");
    const btnTlPreviewAudio = document.getElementById("btn-tl-preview-audio");
    const btnTlZoomOut = document.getElementById("btn-tl-zoom-out");
    const btnTlZoomIn = document.getElementById("btn-tl-zoom-in");
    const btnTlZoomFit = document.getElementById("btn-tl-zoom-fit");
    const tlZoomVal = document.getElementById("tl-zoom-val");

    const timelineScrollContainer = document.getElementById("timeline-scroll-container");
    const timelineWorkspace = document.getElementById("timeline-workspace");
    const timelineRuler = document.getElementById("timeline-ruler");
    const timelinePlayhead = document.getElementById("timeline-playhead");
    const tlLaneSub = document.getElementById("tl-lane-sub");
    const tlLaneVideo = document.getElementById("tl-lane-video");

    // Clip Inspector Elements
    const timelineClipInspector = document.getElementById("timeline-clip-inspector");
    const inspClipIndex = document.getElementById("insp-clip-index");
    const inspClipTiming = document.getElementById("insp-clip-timing");
    const btnInspListen = document.getElementById("btn-insp-listen");
    const btnInspClose = document.getElementById("btn-insp-close");
    const inspInputTranslation = document.getElementById("insp-input-translation");
    const inspSelectSpeed = document.getElementById("insp-select-speed");
    const inspInputStart = document.getElementById("insp-input-start");
    const inspInputEnd = document.getElementById("insp-input-end");

    let selectedSegmentIndex = -1;
    let timelineZoomFactor = 1.0;
    let isDraggingPlayhead = false;
    let activeClipDrag = null;

    function getTimelineTotalDuration() {
        if (previewVideoElement && !isNaN(previewVideoElement.duration) && previewVideoElement.duration > 0) {
            return previewVideoElement.duration;
        }
        if (segmentsData && segmentsData.length > 0) {
            const maxEnd = Math.max(...segmentsData.map(s => Number(s.end || 0)));
            if (maxEnd > 0) return maxEnd;
        }
        return 30.0;
    }

    function renderTimelineRuler(totalDur) {
        if (!timelineRuler) return;
        timelineRuler.innerHTML = "";
        const stepSec = totalDur > 120 ? 10 : (totalDur > 40 ? 5 : 2);
        const totalMarks = Math.ceil(totalDur / stepSec);

        for (let i = 0; i <= totalMarks; i++) {
            const sec = i * stepSec;
            if (sec > totalDur) break;
            const pct = (sec / totalDur) * 100;

            const tick = document.createElement("div");
            tick.className = "ruler-tick major";
            tick.style.left = `${pct}%`;

            const label = document.createElement("span");
            label.className = "ruler-label";
            label.style.left = `${pct}%`;
            label.textContent = formatTime(sec);

            timelineRuler.appendChild(tick);
            timelineRuler.appendChild(label);

            if (stepSec > 2) {
                const halfSec = sec + stepSec / 2;
                if (halfSec <= totalDur) {
                    const halfPct = (halfSec / totalDur) * 100;
                    const halfTick = document.createElement("div");
                    halfTick.className = "ruler-tick";
                    halfTick.style.left = `${halfPct}%`;
                    timelineRuler.appendChild(halfTick);
                }
            }
        }
    }

    function renderTimeline() {
        if (!tlLaneSub) return;
        const totalDur = getTimelineTotalDuration();

        renderTimelineRuler(totalDur);
        tlLaneSub.innerHTML = "";
        if (tlLaneVideo) tlLaneVideo.innerHTML = "";

        if (tlTotalTime) tlTotalTime.textContent = formatTime(totalDur);

        if (!segmentsData || segmentsData.length === 0) return;

        segmentsData.forEach((seg, idx) => {
            const start = Number(seg.start || 0);
            const end = Number(seg.end || 0);
            const dur = Math.max(0.1, end - start);
            const leftPct = (start / totalDur) * 100;
            const widthPct = Math.max(0.8, (dur / totalDur) * 100);

            // 1. Subtitle Clip on Track 1
            const clipEl = document.createElement("div");
            clipEl.className = `tl-clip ${idx === selectedSegmentIndex ? "selected" : ""}`;
            clipEl.setAttribute("data-index", idx);
            clipEl.style.left = `${leftPct}%`;
            clipEl.style.width = `${widthPct}%`;

            clipEl.innerHTML = `
                <div class="tl-handle handle-l" data-handle="left" data-index="${idx}" title="Kéo để chỉnh mốc bắt đầu"></div>
                <div class="tl-clip-content">
                    <span class="tl-clip-num">#${idx + 1}</span>
                    <span class="tl-clip-text">${seg.translation ? seg.translation.replace(/</g, "&lt;") : (seg.text || "...")}</span>
                    <span class="tl-clip-dur">${dur.toFixed(1)}s</span>
                </div>
                <div class="tl-handle handle-r" data-handle="right" data-index="${idx}" title="Kéo để chỉnh mốc kết thúc"></div>
            `;

            clipEl.addEventListener("click", (e) => {
                if (e.target.classList.contains("tl-handle")) return;
                selectClip(idx, true);
            });

            tlLaneSub.appendChild(clipEl);

            // 2. Video Track Slice on Track 2
            if (tlLaneVideo) {
                const vSlice = document.createElement("div");
                vSlice.className = "tl-video-slice";
                vSlice.style.left = `${leftPct}%`;
                vSlice.style.width = `${widthPct}%`;
                vSlice.innerHTML = `<span>Cảnh ${idx + 1}</span>`;
                tlLaneVideo.appendChild(vSlice);
            }
        });

        syncTimelinePlayhead();
    }

    function syncTimelinePlayhead() {
        if (!timelinePlayhead || !previewVideoElement) return;
        const totalDur = getTimelineTotalDuration();
        const curTime = previewVideoElement.currentTime || 0;

        if (tlCurrentTime) tlCurrentTime.textContent = formatTime(curTime);

        const pct = Math.max(0, Math.min(100, (curTime / totalDur) * 100));
        timelinePlayhead.style.left = `${pct}%`;

        if (iconTlPlay) {
            iconTlPlay.className = previewVideoElement.paused ? "fa-solid fa-play" : "fa-solid fa-pause";
        }
    }

    function selectClip(index, seek = false) {
        selectedSegmentIndex = index;

        // Highlight clip on timeline
        if (tlLaneSub) {
            tlLaneSub.querySelectorAll(".tl-clip").forEach(c => {
                const cIdx = parseInt(c.dataset.index);
                c.classList.toggle("selected", cIdx === index);
            });
        }

        // Highlight corresponding row in subtitle table
        if (subtitleTableBody) {
            subtitleTableBody.querySelectorAll("tr").forEach((tr, i) => {
                tr.classList.toggle("active-row", i === index);
                if (i === index) {
                    tr.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }
            });
        }

        if (index < 0 || !segmentsData[index]) {
            if (timelineClipInspector) timelineClipInspector.classList.add("d-none");
            return;
        }

        const seg = segmentsData[index];
        const dur = Math.max(0.1, (seg.end || 0) - (seg.start || 0));

        // Populate inspector
        if (timelineClipInspector) {
            timelineClipInspector.classList.remove("d-none");
            if (inspClipIndex) inspClipIndex.textContent = `Đoạn #${index + 1}`;
            if (inspClipTiming) inspClipTiming.textContent = `${formatTime(seg.start)} - ${formatTime(seg.end)} (${dur.toFixed(1)}s)`;
            if (inspInputTranslation) inspInputTranslation.value = seg.translation || "";
            if (inspSelectSpeed) inspSelectSpeed.value = seg.speed != null ? String(seg.speed) : "1.0";
            if (inspInputStart) inspInputStart.value = Number(seg.start || 0).toFixed(1);
            if (inspInputEnd) inspInputEnd.value = Number(seg.end || 0).toFixed(1);
        }

        if (seek && previewVideoElement) {
            previewVideoElement.currentTime = seg.start;
            updatePreviewSubtitle();
        }
    }

    function splitAtPlayhead() {
        if (!previewVideoElement) return;
        const curTime = Math.round((previewVideoElement.currentTime || 0) * 10) / 10;
        if (curTime <= 0) return;

        // Find which segment covers curTime
        let targetIdx = segmentsData.findIndex(s => curTime > (s.start + 0.15) && curTime < (s.end - 0.15));

        if (targetIdx >= 0) {
            const orig = segmentsData[targetIdx];
            const origEnd = orig.end;
            const words = (orig.translation || "").trim().split(/\s+/).filter(Boolean);
            const mid = Math.max(1, Math.floor(words.length / 2));
            const part1 = words.slice(0, mid).join(" ");
            const part2 = words.slice(mid).join(" ");

            orig.end = curTime;
            orig.translation = part1;

            const newSeg = {
                id: Date.now(),
                start: curTime,
                end: origEnd,
                text: "",
                translation: part2,
                speed: orig.speed || 1.0
            };

            segmentsData.splice(targetIdx + 1, 0, newSeg);
            renderTimeline();
            renderSegmentsTable(segmentsData);
            selectClip(targetIdx + 1, false);
            saveSegmentsToServer();
            triggerDebouncedAutoSave(500);
        } else {
            const totalDur = getTimelineTotalDuration();
            const newEnd = Math.min(totalDur, Math.round((curTime + 1.5) * 10) / 10);
            const newSeg = {
                id: Date.now(),
                start: curTime,
                end: newEnd,
                text: "",
                translation: "Đoạn mới",
                speed: 1.0
            };
            segmentsData.push(newSeg);
            segmentsData.sort((a, b) => a.start - b.start);
            const newIdx = segmentsData.indexOf(newSeg);
            renderTimeline();
            renderSegmentsTable(segmentsData);
            selectClip(newIdx, false);
            saveSegmentsToServer();
            triggerDebouncedAutoSave(500);
        }
    }

    function mergeWithNext() {
        if (selectedSegmentIndex < 0 || selectedSegmentIndex >= segmentsData.length - 1) {
            alert("Vui lòng chọn một đoạn có đoạn tiếp theo để gộp.");
            return;
        }

        const cur = segmentsData[selectedSegmentIndex];
        const next = segmentsData[selectedSegmentIndex + 1];

        cur.end = next.end;
        cur.translation = [cur.translation, next.translation].filter(Boolean).join(" ").trim();
        cur.text = [cur.text, next.text].filter(Boolean).join(" ").trim();

        segmentsData.splice(selectedSegmentIndex + 1, 1);
        renderTimeline();
        renderSegmentsTable(segmentsData);
        selectClip(selectedSegmentIndex, false);
        saveSegmentsToServer();
        triggerDebouncedAutoSave(500);
    }

    function deleteSelectedClip() {
        if (selectedSegmentIndex < 0 || !segmentsData[selectedSegmentIndex]) {
            alert("Vui lòng chọn đoạn cần xóa trên Timeline.");
            return;
        }

        segmentsData.splice(selectedSegmentIndex, 1);
        selectedSegmentIndex = -1;
        if (timelineClipInspector) timelineClipInspector.classList.add("d-none");
        renderTimeline();
        renderSegmentsTable(segmentsData);
        saveSegmentsToServer();
        triggerDebouncedAutoSave(500);
    }

    function setTimelineZoom(zoom) {
        timelineZoomFactor = Math.max(1.0, Math.min(5.0, zoom));
        if (timelineWorkspace) {
            timelineWorkspace.style.width = `${timelineZoomFactor * 100}%`;
        }
        if (tlZoomVal) {
            tlZoomVal.textContent = `${Math.round(timelineZoomFactor * 100)}%`;
        }
        renderTimeline();
    }

    // Ruler Click to Seek
    if (timelineRuler) {
        timelineRuler.addEventListener("click", (e) => {
            const rect = timelineWorkspace.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const pct = Math.max(0, Math.min(1, clickX / rect.width));
            const totalDur = getTimelineTotalDuration();
            const seekTime = pct * totalDur;
            if (previewVideoElement) {
                previewVideoElement.currentTime = seekTime;
                syncTimelinePlayhead();
            }
        });
    }

    // Handle Dragging (Left / Right Handles of clips)
    if (tlLaneSub) {
        tlLaneSub.addEventListener("mousedown", (e) => {
            const handle = e.target.getAttribute("data-handle");
            const idx = parseInt(e.target.getAttribute("data-index"));
            if (!handle || isNaN(idx) || !segmentsData[idx]) return;

            e.stopPropagation();
            e.preventDefault();

            const rect = timelineWorkspace.getBoundingClientRect();
            activeClipDrag = {
                type: handle,
                index: idx,
                startX: e.clientX,
                origStart: segmentsData[idx].start,
                origEnd: segmentsData[idx].end,
                wsWidth: rect.width,
                totalDur: getTimelineTotalDuration()
            };

            selectClip(idx, false);

            function onClipDragMove(moveEvent) {
                if (!activeClipDrag) return;
                const deltaX = moveEvent.clientX - activeClipDrag.startX;
                const deltaSec = (deltaX / activeClipDrag.wsWidth) * activeClipDrag.totalDur;
                const seg = segmentsData[activeClipDrag.index];

                if (activeClipDrag.type === "left") {
                    const newStart = Math.max(0, Math.min(activeClipDrag.origEnd - 0.2, Math.round((activeClipDrag.origStart + deltaSec) * 10) / 10));
                    seg.start = newStart;
                } else if (activeClipDrag.type === "right") {
                    const newEnd = Math.max(activeClipDrag.origStart + 0.2, Math.min(activeClipDrag.totalDur, Math.round((activeClipDrag.origEnd + deltaSec) * 10) / 10));
                    seg.end = newEnd;
                }

                // Update clip visual immediately
                const clipEl = tlLaneSub.querySelector(`.tl-clip[data-index="${activeClipDrag.index}"]`);
                if (clipEl) {
                    const leftPct = (seg.start / activeClipDrag.totalDur) * 100;
                    const widthPct = Math.max(0.8, ((seg.end - seg.start) / activeClipDrag.totalDur) * 100);
                    clipEl.style.left = `${leftPct}%`;
                    clipEl.style.width = `${widthPct}%`;
                    const durSpan = clipEl.querySelector(".tl-clip-dur");
                    if (durSpan) durSpan.textContent = `${(seg.end - seg.start).toFixed(1)}s`;
                }

                if (inspClipTiming) inspClipTiming.textContent = `${formatTime(seg.start)} - ${formatTime(seg.end)} (${(seg.end - seg.start).toFixed(1)}s)`;
                if (inspInputStart) inspInputStart.value = seg.start.toFixed(1);
                if (inspInputEnd) inspInputEnd.value = seg.end.toFixed(1);
            }

            function onClipDragUp() {
                activeClipDrag = null;
                document.removeEventListener("mousemove", onClipDragMove);
                document.removeEventListener("mouseup", onClipDragUp);
                renderTimeline();
                renderSegmentsTable(segmentsData);
                saveSegmentsToServer();
                triggerDebouncedAutoSave(500);
            }

            document.addEventListener("mousemove", onClipDragMove);
            document.addEventListener("mouseup", onClipDragUp);
        });
    }

    // Playhead Drag
    if (timelinePlayhead) {
        timelinePlayhead.querySelector(".playhead-head")?.addEventListener("mousedown", (e) => {
            isDraggingPlayhead = true;
            e.preventDefault();
            e.stopPropagation();

            function onPlayheadMove(moveEvent) {
                if (!isDraggingPlayhead) return;
                const rect = timelineWorkspace.getBoundingClientRect();
                const mouseX = moveEvent.clientX - rect.left;
                const pct = Math.max(0, Math.min(1, mouseX / rect.width));
                const totalDur = getTimelineTotalDuration();
                if (previewVideoElement) {
                    previewVideoElement.currentTime = pct * totalDur;
                    syncTimelinePlayhead();
                    updatePreviewSubtitle();
                }
            }

            function onPlayheadUp() {
                isDraggingPlayhead = false;
                document.removeEventListener("mousemove", onPlayheadMove);
                document.removeEventListener("mouseup", onPlayheadUp);
            }

            document.addEventListener("mousemove", onPlayheadMove);
            document.addEventListener("mouseup", onPlayheadUp);
        });
    }

    // Toolbar Buttons
    if (btnTlPlay) {
        btnTlPlay.addEventListener("click", () => {
            if (!previewVideoElement) return;
            if (previewVideoElement.paused) {
                previewVideoElement.play();
            } else {
                previewVideoElement.pause();
            }
        });
    }

    if (btnTlSplit) btnTlSplit.addEventListener("click", splitAtPlayhead);
    if (btnTlMerge) btnTlMerge.addEventListener("click", mergeWithNext);
    if (btnTlDelete) btnTlDelete.addEventListener("click", deleteSelectedClip);

    if (btnTlZoomIn) btnTlZoomIn.addEventListener("click", () => setTimelineZoom(timelineZoomFactor + 0.3));
    if (btnTlZoomOut) btnTlZoomOut.addEventListener("click", () => setTimelineZoom(timelineZoomFactor - 0.3));
    if (btnTlZoomFit) btnTlZoomFit.addEventListener("click", () => setTimelineZoom(1.0));

    const btnTlToggleDub = document.getElementById("btn-tl-toggle-dub");
    const lblTlDub = document.getElementById("lbl-tl-dub");
    const btnTlRefreshDub = document.getElementById("btn-tl-refresh-dub");

    if (btnTlToggleDub) {
        btnTlToggleDub.addEventListener("click", () => {
            isDubbingEnabled = !isDubbingEnabled;
            btnTlToggleDub.classList.toggle("active", isDubbingEnabled);
            if (lblTlDub) {
                lblTlDub.textContent = isDubbingEnabled ? "Lồng tiếng (BẬT)" : "Lồng tiếng (TẮT)";
            }
            syncPreviewVideoVolume();
            if (isDubbingEnabled) {
                if (previewVideoElement && !previewVideoElement.paused) {
                    playDubbingAudio();
                }
            } else {
                pauseDubbingAudio();
            }
        });
    }

    if (btnTlRefreshDub) {
        btnTlRefreshDub.addEventListener("click", () => {
            refreshPreviewDubbedAudio();
        });
    }

    // Inspector Inputs Live Binding
    if (inspInputTranslation) {
        inspInputTranslation.addEventListener("input", () => {
            if (selectedSegmentIndex >= 0 && segmentsData[selectedSegmentIndex]) {
                segmentsData[selectedSegmentIndex].translation = inspInputTranslation.value;
                const clipText = tlLaneSub?.querySelector(`.tl-clip[data-index="${selectedSegmentIndex}"] .tl-clip-text`);
                if (clipText) clipText.textContent = inspInputTranslation.value || "(Trống)";
                updatePreviewSubtitle();
                triggerDebouncedAutoSave(1500);
            }
        });
        inspInputTranslation.addEventListener("blur", () => {
            renderSegmentsTable(segmentsData);
            saveSegmentsToServer();
        });
    }

    if (inspSelectSpeed) {
        inspSelectSpeed.addEventListener("change", () => {
            if (selectedSegmentIndex >= 0 && segmentsData[selectedSegmentIndex]) {
                segmentsData[selectedSegmentIndex].speed = parseFloat(inspSelectSpeed.value);
                renderSegmentsTable(segmentsData);
                saveSegmentsToServer();
                triggerDebouncedAutoSave(500);
            }
        });
    }

    if (inspInputStart) {
        inspInputStart.addEventListener("change", () => {
            if (selectedSegmentIndex >= 0 && segmentsData[selectedSegmentIndex]) {
                const val = parseFloat(inspInputStart.value);
                if (!isNaN(val) && val >= 0) {
                    segmentsData[selectedSegmentIndex].start = val;
                    renderTimeline();
                    renderSegmentsTable(segmentsData);
                    saveSegmentsToServer();
                }
            }
        });
    }

    if (inspInputEnd) {
        inspInputEnd.addEventListener("change", () => {
            if (selectedSegmentIndex >= 0 && segmentsData[selectedSegmentIndex]) {
                const val = parseFloat(inspInputEnd.value);
                if (!isNaN(val) && val > segmentsData[selectedSegmentIndex].start) {
                    segmentsData[selectedSegmentIndex].end = val;
                    renderTimeline();
                    renderSegmentsTable(segmentsData);
                    saveSegmentsToServer();
                }
            }
        });
    }

    if (btnInspClose) {
        btnInspClose.addEventListener("click", () => {
            if (timelineClipInspector) timelineClipInspector.classList.add("d-none");
            selectedSegmentIndex = -1;
            if (tlLaneSub) tlLaneSub.querySelectorAll(".tl-clip").forEach(c => c.classList.remove("selected"));
        });
    }

    if (btnInspListen || btnTlPreviewAudio) {
        const previewVoice = async () => {
            if (selectedSegmentIndex < 0 || !segmentsData[selectedSegmentIndex]) return;
            const text = (segmentsData[selectedSegmentIndex].translation || "").trim();
            if (!text) return;
            const voice = voiceSelectStep3 ? voiceSelectStep3.value : "female_hoaimy";
            try {
                const res = await fetch("/api/tts-free", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, voice })
                });
                if (res.ok) {
                    const blob = await res.blob();
                    const audio = new Audio(URL.createObjectURL(blob));
                    audio.play();
                }
            } catch (e) {
                console.error("Audio preview failed", e);
            }
        };
        if (btnInspListen) btnInspListen.addEventListener("click", previewVoice);
        if (btnTlPreviewAudio) btnTlPreviewAudio.addEventListener("click", previewVoice);
    }

    // Keyboard Shortcuts (Space: Play/Pause, S/C: Split, Delete: Delete)
    document.addEventListener("keydown", (e) => {
        const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : "";
        if (tag === "input" || tag === "textarea" || tag === "select") return;

        if (e.code === "Space") {
            e.preventDefault();
            if (previewVideoElement) {
                if (previewVideoElement.paused) previewVideoElement.play();
                else previewVideoElement.pause();
            }
        } else if (e.code === "KeyS" || e.code === "KeyC") {
            e.preventDefault();
            splitAtPlayhead();
        } else if (e.code === "Delete" || e.code === "Backspace") {
            if (selectedSegmentIndex >= 0) {
                e.preventDefault();
                deleteSelectedClip();
            }
        }
    });

    if (btnAddSegment) {
        btnAddSegment.addEventListener("click", () => {
            const curTime = previewVideoElement ? previewVideoElement.currentTime : 0;
            segmentsData.push({
                id: segmentsData.length + 1,
                start: Math.round(curTime * 10) / 10,
                end: Math.round((curTime + 3) * 10) / 10,
                text: "Tự thêm",
                translation: "Nội dung phụ đề mới"
            });
            renderSegmentsTable(segmentsData);
            saveSegmentsToServer();
            triggerDebouncedAutoSave(500);
        });
    }

    function collectEditedSegments() {
        if (!subtitleTableBody) return segmentsData;
        const inputs = subtitleTableBody.querySelectorAll(".sub-edit-input");
        inputs.forEach(input => {
            const idx = parseInt(input.dataset.index);
            if (segmentsData[idx]) {
                segmentsData[idx].translation = input.value.trim();
            }
        });
        const startInputs = subtitleTableBody.querySelectorAll(".seg-start-input");
        startInputs.forEach(input => {
            const idx = parseInt(input.dataset.index);
            const val = parseFloat(input.value);
            if (segmentsData[idx] && !isNaN(val) && val >= 0) {
                segmentsData[idx].start = val;
            }
        });
        const endInputs = subtitleTableBody.querySelectorAll(".seg-end-input");
        endInputs.forEach(input => {
            const idx = parseInt(input.dataset.index);
            const val = parseFloat(input.value);
            if (segmentsData[idx] && !isNaN(val) && val >= 0) {
                segmentsData[idx].end = val;
            }
        });
        const speedSelects = subtitleTableBody.querySelectorAll(".seg-speed-select");
        speedSelects.forEach(sel => {
            const idx = parseInt(sel.dataset.index);
            const val = parseFloat(sel.value);
            if (segmentsData[idx] && !isNaN(val) && val > 0) {
                segmentsData[idx].speed = val;
            }
        });
        return segmentsData;
    }

    if (btnStep2Transcribe) {
        btnStep2Transcribe.addEventListener("click", async () => {
            if (!currentProjectId) {
                alert("Vui lòng tải video ở Bước 1 trước.");
                return;
            }

            btnStep2Transcribe.disabled = true;
            if (step2ProgressBox) step2ProgressBox.classList.remove("d-none");
            if (step2ProgressBar) step2ProgressBar.style.width = "5%";
            if (step2ProgressPct) step2ProgressPct.textContent = "5%";
            if (step2ProgressMsg) step2ProgressMsg.textContent = "Đang khởi tạo...";

            try {
                const res = await fetch(`/api/project/${currentProjectId}/transcribe`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        mode: currentTranscribeMode,
                        mask_box: {
                            x: maskBoxCoords.x,
                            y: maskBoxCoords.y,
                            w: maskBoxCoords.w,
                            h: maskBoxCoords.h
                        },
                        source_lang: "Chinese"
                    })
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể khởi động quét.");
                }

                if (pollingInterval) clearInterval(pollingInterval);
                pollingInterval = setInterval(async () => {
                    try {
                        const statusRes = await fetch(`/api/project/${currentProjectId}/status`);
                        if (!statusRes.ok) return;
                        const statusData = await statusRes.json();

                        if (step2ProgressBar) step2ProgressBar.style.width = `${statusData.progress || 0}%`;
                        if (step2ProgressPct) step2ProgressPct.textContent = `${statusData.progress || 0}%`;
                        if (step2ProgressMsg) step2ProgressMsg.textContent = statusData.message || "Đang quét...";

                        if (statusData.status === "transcribed") {
                            clearInterval(pollingInterval);
                            btnStep2Transcribe.disabled = false;
                            if (step2ProgressBox) step2ProgressBox.classList.add("d-none");

                            renderSegmentsTable(statusData.segments || []);

                            currentProjectMeta = statusData.project || currentProjectMeta;
                            setSaveStatus("saved", "Đã quét phụ đề & tự động lưu");
                            // Đánh dấu xong bước 2, mở khóa và chuyển sang bước 3 (mới bắt đầu hiện phụ đề tiếng Việt)
                            markStepDone(2);
                            unlockStep(3);
                            switchStep(3);
                        } else if (statusData.status === "transcribe_failed") {
                            clearInterval(pollingInterval);
                            btnStep2Transcribe.disabled = false;
                            alert("Quét phụ đề thất bại: " + (statusData.error || statusData.message));
                        }
                    } catch (e) {
                        console.error(e);
                    }
                }, 1000);
            } catch (err) {
                btnStep2Transcribe.disabled = false;
                if (step2ProgressBox) step2ProgressBox.classList.add("d-none");
                alert(err.message);
            }
        });
    }

    // 4. Bước 3: Giọng Đọc, Masking Che Chữ Cũ & Kiểu Sub
    function applyMaskVisualPreview() {
        const isEnabled = step3MaskEnabled 
            ? step3MaskEnabled.checked 
            : (maskEnabledCheck ? maskEnabledCheck.checked : true);
        const style = maskStyleSelect ? maskStyleSelect.value : "blur";

        if (maskEnabledCheck) maskEnabledCheck.checked = isEnabled;
        if (step3MaskEnabled) step3MaskEnabled.checked = isEnabled;
        if (maskStyleSelect) maskStyleSelect.value = style;

        if (step3MaskOptions) {
            step3MaskOptions.classList.toggle("d-none", !isEnabled);
        }

        document.querySelectorAll(".mask-chip").forEach(chip => {
            chip.classList.toggle("active", chip.getAttribute("data-style") === style);
        });

        if (bboxSub) {
            if (!isEnabled) {
                bboxSub.classList.remove("has-blur-mask", "has-solid-mask");
            } else if (style === "solid") {
                bboxSub.classList.remove("has-blur-mask");
                bboxSub.classList.add("has-solid-mask");
            } else {
                bboxSub.classList.remove("has-solid-mask");
                bboxSub.classList.add("has-blur-mask");
            }
        }

        if (bboxMask) {
            // Khung đỏ OCR tuyệt đối không áp dụng blur hay che tối để người dùng luôn nhìn rõ chữ gốc căn chỉnh
            bboxMask.classList.remove("has-blur-mask", "has-solid-mask");
        }
    }

    if (step3MaskEnabled) {
        step3MaskEnabled.addEventListener("change", () => {
            if (maskEnabledCheck) maskEnabledCheck.checked = step3MaskEnabled.checked;
            applyMaskVisualPreview();
            triggerDebouncedAutoSave(500);
        });
    }

    if (maskEnabledCheck) {
        maskEnabledCheck.addEventListener("change", () => {
            if (step3MaskEnabled) step3MaskEnabled.checked = maskEnabledCheck.checked;
            applyMaskVisualPreview();
            triggerDebouncedAutoSave(500);
        });
    }

    if (maskStyleSelect) {
        maskStyleSelect.addEventListener("change", () => {
            applyMaskVisualPreview();
            triggerDebouncedAutoSave(500);
        });
    }

    document.querySelectorAll(".mask-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const style = chip.getAttribute("data-style");
            if (maskStyleSelect) maskStyleSelect.value = style;
            applyMaskVisualPreview();
            triggerDebouncedAutoSave(500);
        });
    });

    if (btnToggleMaskBoxPreview) {
        btnToggleMaskBoxPreview.addEventListener("click", () => {
            const isActive = btnToggleMaskBoxPreview.classList.toggle("active");
            btnToggleMaskBoxPreview.innerHTML = isActive 
                ? `<i class="fa-solid fa-eye-slash"></i> Ẩn khung đỏ` 
                : `<i class="fa-solid fa-vector-square"></i> Hiện khung đỏ`;
            if (bboxMask) {
                bboxMask.classList.toggle("d-none", !isActive);
            }
        });
    }

    applyMaskVisualPreview();

    function syncPreviewVideoVolume() {
        if (!previewVideoElement) return;

        // Nếu video đang phát là video đã ghép lồng tiếng sẵn (video-dubbed)
        if (previewVideoElement.src && previewVideoElement.src.includes("video-dubbed")) {
            previewVideoElement.volume = 1.0;
            pauseDubbingAudio();
            return;
        }

        // Nếu người dùng tắt lồng tiếng, phát âm thanh video gốc 100%
        if (!isDubbingEnabled) {
            previewVideoElement.volume = 1.0;
            return;
        }

        // Khi bật lồng tiếng, video gốc đóng vai trò nhạc nền (Background)
        let vol = 0.15;
        if (bgVolumeSlider) {
            vol = parseFloat(bgVolumeSlider.value);
        } else if (sharedBgVol) {
            vol = parseFloat(sharedBgVol.value);
        }
        if (isNaN(vol)) vol = 0.15;
        vol = Math.max(0, Math.min(1, vol));
        previewVideoElement.volume = vol;
    }

    if (bgVolumeSlider && bgVolLabel) {
        bgVolumeSlider.addEventListener("input", () => {
            const v = parseFloat(bgVolumeSlider.value);
            bgVolLabel.textContent = `${Math.round(v * 100)}%`;
            syncPreviewVideoVolume();
        });
        bgVolumeSlider.addEventListener("change", () => {
            syncPreviewVideoVolume();
            triggerDebouncedAutoSave(500);
        });
    }
    if (ttsVolumeSlider && ttsVolLabel) {
        ttsVolumeSlider.addEventListener("input", () => {
            ttsVolLabel.textContent = `${Math.round(ttsVolumeSlider.value * 100)}%`;
        });
        ttsVolumeSlider.addEventListener("change", () => triggerDebouncedAutoSave(500));
    }
    if (voiceSelectStep3) {
        voiceSelectStep3.addEventListener("change", () => triggerDebouncedAutoSave(500));
    }

    if (btnPreviewVoiceStep3 && voiceSelectStep3) {
        btnPreviewVoiceStep3.addEventListener("click", async () => {
            const voice = voiceSelectStep3.value;
            btnPreviewVoiceStep3.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
            try {
                const res = await fetch(`/api/preview-voice?voice=${encodeURIComponent(voice)}`);
                if (res.ok) {
                    const blob = await res.blob();
                    const url = URL.createObjectURL(blob);
                    const audio = new Audio(url);
                    audio.play();
                }
            } catch (e) {
                console.error(e);
            } finally {
                btnPreviewVoiceStep3.innerHTML = `<i class="fa-solid fa-volume-high"></i>`;
            }
        });
    }

    if (btnGotoSubstudio) {
        btnGotoSubstudio.addEventListener("click", () => {
            const tabBtnSub = document.getElementById("tab-btn-subtitles");
            if (tabBtnSub) tabBtnSub.click();
        });
    }

    async function saveSegmentsToServer() {
        const segments = collectEditedSegments();
        if (currentProjectId && segments.length > 0) {
            try {
                await fetch(`/api/project/${currentProjectId}/segments`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ segments })
                });
                triggerDebouncedDubbingRefresh(2500);
            } catch (e) {
                console.warn("Could not sync segments to server", e);
            }
        }
    }

    if (btnSaveSegments) {
        btnSaveSegments.addEventListener("click", async () => {
            const originalHTML = btnSaveSegments.innerHTML;
            btnSaveSegments.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...`;
            await saveSegmentsToServer();
            setTimeout(() => {
                btnSaveSegments.innerHTML = `<i class="fa-solid fa-check"></i> Đã lưu xong!`;
                setTimeout(() => {
                    btnSaveSegments.innerHTML = originalHTML;
                }, 1500);
            }, 300);
        });
    }

    const chkAutoExtendVideo = document.getElementById("chk-auto-extend-video");
    const summaryAutoExtend = document.getElementById("summary-auto-extend");
    if (chkAutoExtendVideo) {
        chkAutoExtendVideo.addEventListener("change", () => {
            if (summaryAutoExtend) {
                summaryAutoExtend.textContent = chkAutoExtendVideo.checked ? "Đang bật (Chống mất từ)" : "Đã tắt (Giữ nguyên gốc)";
                summaryAutoExtend.className = chkAutoExtendVideo.checked ? "summary-val text-success" : "summary-val";
            }
            triggerDebouncedAutoSave(500);
        });
    }

    if (btnStep3Next) {
        btnStep3Next.addEventListener("click", async () => {
            await saveSegmentsToServer();
            await autoSaveProjectState({ current_step: 4 });
            if (summaryAutoExtend && chkAutoExtendVideo) {
                summaryAutoExtend.textContent = chkAutoExtendVideo.checked ? "Đang bật (Chống mất từ)" : "Đã tắt (Giữ nguyên gốc)";
                summaryAutoExtend.className = chkAutoExtendVideo.checked ? "summary-val text-success" : "summary-val";
            }
            markStepDone(3);
            unlockStep(4);
            switchStep(4);
        });
    }

    // ==========================================
    // 4.5. XUẤT & TẢI VIDEO TRỰC TIẾP TẠI BƯỚC 3 (QUICK EXPORT)
    // ==========================================
    let isQuickExporting = false;

    async function startQuickExportAndDownload() {
        if (!currentProjectId) {
            alert("Vui lòng tải hoặc mở một dự án trước khi xuất video!");
            return;
        }

        if (isQuickExporting) {
            return;
        }

        const segments = collectEditedSegments();
        if (!segments || segments.length === 0) {
            alert("Chưa có đoạn phụ đề nào. Vui lòng quét OCR hoặc tạo câu trước!");
            return;
        }

        isQuickExporting = true;

        const updateExportButtons = (exporting, pct = 0, msg = "") => {
            const btns = [btnStep3RenderDownload, btnTlQuickExport, btnHeaderQuickExport];
            btns.forEach(b => {
                if (!b) return;
                b.disabled = exporting;
            });

            if (lblStep3RenderDownload && iconStep3RenderDownload) {
                if (exporting) {
                    iconStep3RenderDownload.className = "fa-solid fa-spinner fa-spin";
                    lblStep3RenderDownload.textContent = pct > 0 ? `Đang xuất video... (${pct}%)` : "Đang chuẩn bị ghép...";
                } else {
                    iconStep3RenderDownload.className = "fa-solid fa-download";
                    lblStep3RenderDownload.textContent = "⚡ Xuất & Tải Lại Video (MP4)";
                }
            }

            if (lblTlQuickExport && iconTlQuickExport) {
                if (exporting) {
                    iconTlQuickExport.className = "fa-solid fa-spinner fa-spin";
                    lblTlQuickExport.textContent = pct > 0 ? `${pct}%` : "Đang ghép";
                } else {
                    iconTlQuickExport.className = "fa-solid fa-download";
                    lblTlQuickExport.textContent = "Tải Video";
                }
            }

            if (btnHeaderQuickExport) {
                btnHeaderQuickExport.disabled = exporting;
                btnHeaderQuickExport.innerHTML = exporting 
                    ? `<i class="fa-solid fa-spinner fa-spin"></i> <span>${pct > 0 ? `${pct}%` : 'Đang xuất...'}</span>`
                    : `<i class="fa-solid fa-download"></i> <span>Tải Video MP4</span>`;
            }
        };

        if (step3ProgressBox) {
            step3ProgressBox.classList.remove("d-none");
            if (step3ProgressBar) step3ProgressBar.style.width = "5%";
            if (step3ProgressPct) step3ProgressPct.textContent = "5%";
            if (step3ProgressMsg) step3ProgressMsg.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang chuẩn bị xuất video...`;
        }
        if (step3SuccessBox) step3SuccessBox.classList.add("d-none");

        updateExportButtons(true, 5);

        try {
            // 1. Lưu câu phụ đề mới nhất lên máy chủ
            await saveSegmentsToServer();

            // 2. Gửi lệnh render
            const payload = {
                voice: voiceSelectStep3 ? voiceSelectStep3.value : "female_hoaimy",
                rvc_model: rvcModelSelectStep3 ? rvcModelSelectStep3.value : "none",
                rvc_pitch: rvcPitchSlider ? parseInt(rvcPitchSlider.value) : 0,
                bg_volume: bgVolumeSlider ? parseFloat(bgVolumeSlider.value) : 0.15,
                tts_volume: ttsVolumeSlider ? parseFloat(ttsVolumeSlider.value) : 1.0,
                mask_box: {
                    x: maskBoxCoords.x,
                    y: maskBoxCoords.y,
                    w: maskBoxCoords.w,
                    h: maskBoxCoords.h,
                    enabled: maskEnabledCheckStep ? maskEnabledCheckStep.checked : true,
                    style: maskStyleSelectStep ? maskStyleSelectStep.value : "blur"
                },
                sub_box: {
                    x: subBoxCoords.x,
                    y: subBoxCoords.y,
                    w: subBoxCoords.w,
                    h: subBoxCoords.h
                },
                sub_styling: {
                    font_size: parseInt(subStylingState.font_size || 48),
                    font_name: subStylingState.font_name || "Nunito",
                    primary_color: subStylingState.primary_color || "#FFFFFF",
                    outline_color: subStylingState.outline_color || "#000000",
                    outline_width: parseFloat(subStylingState.outline_width ?? 3.0),
                    box_style: subStylingState.box_style || "outline",
                    back_color: subStylingState.back_color || "#000000",
                    box_opacity: parseFloat(subStylingState.box_opacity ?? 0.75),
                    bold: Boolean(subStylingState.bold),
                    shadow: 1.5
                },
                burn_subtitles: true,
                auto_extend_video: Boolean(document.getElementById("chk-auto-extend-video")?.checked ?? false),
                segments: segments
            };

            const res = await fetch(`/api/project/${currentProjectId}/render`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Không thể khởi động render video.");
            }

            const exportPoll = setInterval(async () => {
                try {
                    const statusRes = await fetch(`/api/project/${currentProjectId}/status`);
                    if (!statusRes.ok) return;
                    const statusData = await statusRes.json();

                    const progress = statusData.progress || 0;
                    const msg = statusData.message || "Đang ghép âm thanh & phụ đề...";

                    if (step3ProgressBar) step3ProgressBar.style.width = `${progress}%`;
                    if (step3ProgressPct) step3ProgressPct.textContent = `${progress}%`;
                    if (step3ProgressMsg) step3ProgressMsg.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${msg}`;

                    updateExportButtons(true, progress, msg);

                    if (statusData.status === "completed") {
                        clearInterval(exportPoll);
                        isQuickExporting = false;
                        updateExportButtons(false);

                        if (step3ProgressBar) step3ProgressBar.style.width = "100%";
                        if (step3ProgressPct) step3ProgressPct.textContent = "100%";
                        if (step3ProgressMsg) step3ProgressMsg.innerHTML = `<i class="fa-solid fa-circle-check"></i> Ghép video hoàn tất!`;

                        setTimeout(() => {
                            if (step3ProgressBox) step3ProgressBox.classList.add("d-none");
                        }, 1200);

                        // Hiện hộp thông báo thành công tại Bước 3
                        if (step3SuccessBox) step3SuccessBox.classList.remove("d-none");

                        // Tự động tải file MP4 về máy ngay lập tức
                        const dlUrl = `/api/project/${currentProjectId}/download?t=${Date.now()}`;
                        const dl = document.createElement("a");
                        dl.href = dlUrl;
                        dl.download = `video_dubbed_${currentProjectId.substring(0, 8)}.mp4`;
                        document.body.appendChild(dl);
                        dl.click();
                        document.body.removeChild(dl);

                        // Cập nhật trạng thái dự án
                        currentProjectMeta = statusData.project || currentProjectMeta;
                        setSaveStatus("saved", "Đã xuất video & tự động lưu");
                        markStepDone(4);

                    } else if (statusData.status === "render_failed") {
                        clearInterval(exportPoll);
                        isQuickExporting = false;
                        updateExportButtons(false);
                        if (step3ProgressBox) step3ProgressBox.classList.add("d-none");
                        alert("Lỗi khi ghép video: " + (statusData.error || statusData.message || "Không xác định"));
                    }
                } catch (pe) {
                    console.error("Polling export status error", pe);
                }
            }, 1000);

        } catch (err) {
            isQuickExporting = false;
            updateExportButtons(false);
            if (step3ProgressBox) step3ProgressBox.classList.add("d-none");
            alert("Lỗi: " + err.message);
        }
    }

    if (btnStep3RenderDownload) {
        btnStep3RenderDownload.addEventListener("click", startQuickExportAndDownload);
    }
    if (btnTlQuickExport) {
        btnTlQuickExport.addEventListener("click", startQuickExportAndDownload);
    }
    if (btnHeaderQuickExport) {
        btnHeaderQuickExport.addEventListener("click", startQuickExportAndDownload);
    }
    if (btnStep3Redownload) {
        btnStep3Redownload.addEventListener("click", () => {
            if (!currentProjectId) return;
            const dl = document.createElement("a");
            dl.href = `/api/project/${currentProjectId}/download?t=${Date.now()}`;
            dl.download = `video_dubbed_${currentProjectId.substring(0, 8)}.mp4`;
            document.body.appendChild(dl);
            dl.click();
            document.body.removeChild(dl);
        });
    }

    // ==========================================
    // 4.6. TẢI RIÊNG FILE ÂM THANH LỜI DỊCH TIẾNG VIỆT (MP3)
    // ==========================================
    async function downloadTranslatedAudioOnly() {
        if (!currentProjectId) {
            alert("Vui lòng mở hoặc tải dự án trước khi tải âm thanh!");
            return;
        }

        const segments = collectEditedSegments();
        if (!segments || segments.length === 0) {
            alert("Chưa có đoạn phụ đề nào để tạo âm thanh lời dịch!");
            return;
        }

        setSaveStatus("saving", "Đang chuẩn bị file âm thanh lời dịch tiếng Việt...");

        const btns = [btnStep3DownloadAudio, btnTlDownloadAudio, btnHeaderDownloadAudio];
        const origHTMLs = btns.map(b => b ? b.innerHTML : "");

        btns.forEach(b => {
            if (b) {
                b.disabled = true;
                b.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Đang xử lý...</span>`;
            }
        });

        try {
            // Đồng bộ câu từ mới nhất lên server trước
            await saveSegmentsToServer();

            const url = `/api/project/${currentProjectId}/download-audio?t=${Date.now()}`;
            const link = document.createElement("a");
            link.href = url;
            link.download = `audio_dich_tieng_viet_${currentProjectId.substring(0, 8)}.mp3`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setSaveStatus("saved", "Đã tải file âm thanh lời dịch (MP3)!");
        } catch (e) {
            console.error("Download audio error", e);
            alert("Lỗi tải âm thanh: " + e.message);
            setSaveStatus("error", "Lỗi tải âm thanh.");
        } finally {
            btns.forEach((b, i) => {
                if (b) {
                    b.disabled = false;
                    b.innerHTML = origHTMLs[i];
                }
            });
        }
    }

    if (btnStep3DownloadAudio) {
        btnStep3DownloadAudio.addEventListener("click", downloadTranslatedAudioOnly);
    }
    if (btnTlDownloadAudio) {
        btnTlDownloadAudio.addEventListener("click", downloadTranslatedAudioOnly);
    }
    if (btnHeaderDownloadAudio) {
        btnHeaderDownloadAudio.addEventListener("click", downloadTranslatedAudioOnly);
    }

    // 5. Bước 4: Render & Xuất Video Hoàn Chỉnh
    if (btnStep4Render) {
        btnStep4Render.addEventListener("click", async () => {
            if (!currentProjectId) {
                alert("Chưa có phiên làm việc.");
                return;
            }

            const segments = collectEditedSegments();
            btnStep4Render.disabled = true;
            if (step4ProgressBox) step4ProgressBox.classList.remove("d-none");
            if (step4ProgressBar) step4ProgressBar.style.width = "5%";
            if (step4ProgressPct) step4ProgressPct.textContent = "5%";
            if (step4ProgressMsg) step4ProgressMsg.textContent = "Đang bắt đầu ghép...";

            showState("processing");

            try {
                const res = await fetch(`/api/project/${currentProjectId}/render`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        voice: voiceSelectStep3 ? voiceSelectStep3.value : "female_hoaimy",
                        bg_volume: bgVolumeSlider ? parseFloat(bgVolumeSlider.value) : 0.15,
                        tts_volume: ttsVolumeSlider ? parseFloat(ttsVolumeSlider.value) : 1.0,
                        mask_box: {
                            x: maskBoxCoords.x,
                            y: maskBoxCoords.y,
                            w: maskBoxCoords.w,
                            h: maskBoxCoords.h,
                            enabled: maskEnabledCheckStep ? maskEnabledCheckStep.checked : true,
                            style: maskStyleSelectStep ? maskStyleSelectStep.value : "blur"
                        },
                        sub_box: {
                            x: subBoxCoords.x,
                            y: subBoxCoords.y,
                            w: subBoxCoords.w,
                            h: subBoxCoords.h
                        },
                        sub_styling: {
                            font_size: parseInt(subStylingState.font_size || 48),
                            font_name: subStylingState.font_name || "Nunito",
                            primary_color: subStylingState.primary_color || "#FFFFFF",
                            outline_color: subStylingState.outline_color || "#000000",
                            outline_width: parseFloat(subStylingState.outline_width ?? 3.0),
                            box_style: subStylingState.box_style || "outline",
                            back_color: subStylingState.back_color || "#000000",
                            box_opacity: parseFloat(subStylingState.box_opacity ?? 0.75),
                            bold: Boolean(subStylingState.bold),
                            shadow: 1.5
                        },
                        burn_subtitles: true,
                        auto_extend_video: Boolean(document.getElementById("chk-auto-extend-video")?.checked ?? false),
                        segments: segments
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể khởi động render.");
                }

                if (pollingInterval) clearInterval(pollingInterval);
                pollingInterval = setInterval(async () => {
                    try {
                        const statusRes = await fetch(`/api/project/${currentProjectId}/status`);
                        if (!statusRes.ok) return;
                        const statusData = await statusRes.json();

                        if (step4ProgressBar) step4ProgressBar.style.width = `${statusData.progress || 0}%`;
                        if (step4ProgressPct) step4ProgressPct.textContent = `${statusData.progress || 0}%`;
                        if (step4ProgressMsg) step4ProgressMsg.textContent = statusData.message || "Đang render...";

                        if (progressBar) progressBar.style.width = `${statusData.progress || 0}%`;
                        if (progressPercent) progressPercent.textContent = `${statusData.progress || 0}%`;
                        if (statusMessage) statusMessage.textContent = statusData.message || "Đang render...";

                        if (statusData.status === "completed") {
                            clearInterval(pollingInterval);
                            btnStep4Render.disabled = false;
                            if (step4ProgressBox) step4ProgressBox.classList.add("d-none");
                            markStepDone(4);

                            currentProjectMeta = statusData.project || currentProjectMeta;
                            setSaveStatus("saved", "Đã hoàn thành & tự động lưu");
                            showState("success");
                            if (videoPreview) {
                                videoPreview.src = statusData.video_url || `/api/project/${currentProjectId}/video-dubbed`;
                                videoPreview.load();
                            }
                            if (downloadBtn) downloadBtn.href = statusData.download_url || `/api/project/${currentProjectId}/download`;
                            if (downloadSrtBtn) downloadSrtBtn.href = statusData.subtitles_url || `/api/project/${currentProjectId}/subtitles`;

                            // Tự động tải file MP4
                            const dlUrl = `/api/project/${currentProjectId}/download?t=${Date.now()}`;
                            const dl = document.createElement("a");
                            dl.href = dlUrl;
                            dl.download = `video_dubbed_${currentProjectId.substring(0, 8)}.mp4`;
                            document.body.appendChild(dl);
                            dl.click();
                            document.body.removeChild(dl);
                        } else if (statusData.status === "render_failed") {
                            clearInterval(pollingInterval);
                            btnStep4Render.disabled = false;
                            showState("error");
                            if (errorMessage) errorMessage.textContent = statusData.error || statusData.message;
                        }
                    } catch (e) {
                        console.error(e);
                    }
                }, 1000);
            } catch (err) {
                btnStep4Render.disabled = false;
                if (step4ProgressBox) step4ProgressBox.classList.add("d-none");
                showState("error");
                if (errorMessage) errorMessage.textContent = err.message;
            }
        });
    }

    // 6. Nút Reset toàn bộ Studio
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            createNewProject(true);
        });
    }

    if (retryBtn) {
        retryBtn.addEventListener("click", () => {
            showState("idle");
        });
    }

    // ==========================================
    // 7. XUẤT / NHẬP FILE SRT (TRUNG - VIỆT)
    // ==========================================
    const btnExportSrtZh = document.getElementById("btn-export-srt-zh");
    const btnExportSrtVi = document.getElementById("btn-export-srt-vi");
    const btnOpenImportSrt = document.getElementById("btn-open-import-srt");
    const modalSrtImport = document.getElementById("modal-srt-import");
    const btnCloseSrtModal = document.getElementById("btn-close-srt-modal");
    const btnCancelSrtModal = document.getElementById("btn-cancel-srt-modal");
    const btnModalCopyZhSrt = document.getElementById("btn-modal-copy-zh-srt");
    const btnModalDownloadZhSrt = document.getElementById("btn-modal-download-zh-srt");
    const btnChooseSrtFile = document.getElementById("btn-choose-srt-file");
    const inputFileSrtVi = document.getElementById("input-file-srt-vi");
    const textareaImportSrt = document.getElementById("textarea-import-srt");
    const btnApplySrtImport = document.getElementById("btn-apply-srt-import");

    function formatSecToSrtTime(sec) {
        const s = Math.max(0, Number(sec || 0));
        const hrs = Math.floor(s / 3600);
        const mins = Math.floor((s % 3600) / 60);
        const secs = Math.floor(s % 60);
        const ms = Math.min(999, Math.round((s - Math.floor(s)) * 1000));
        return `${String(hrs).padStart(2, "0")}:${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
    }

    function buildLocalSrtString(lang = "zh") {
        const segs = collectEditedSegments();
        if (!segs || segs.length === 0) return "";
        return segs.map((seg, i) => {
            const st = formatSecToSrtTime(seg.start);
            const et = formatSecToSrtTime(seg.end);
            const content = lang === "zh" ? (seg.text || seg.translation || "") : (seg.translation || seg.text || "");
            return `${i + 1}\n${st} --> ${et}\n${content}\n`;
        }).join("\n");
    }

    async function downloadProjectSrt(lang = "zh") {
        if (!currentProjectId) {
            alert("Vui lòng mở hoặc tạo dự án trước.");
            return;
        }
        await saveSegmentsToServer();
        const url = `/api/project/${currentProjectId}/subtitles?lang=${encodeURIComponent(lang)}&t=${Date.now()}`;
        const a = document.createElement("a");
        a.href = url;
        a.download = `subtitles_${lang}_${currentProjectId.substring(0, 8)}.srt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    if (btnExportSrtZh) {
        btnExportSrtZh.addEventListener("click", () => downloadProjectSrt("zh"));
    }
    if (btnModalDownloadZhSrt) {
        btnModalDownloadZhSrt.addEventListener("click", () => downloadProjectSrt("zh"));
    }
    if (btnExportSrtVi) {
        btnExportSrtVi.addEventListener("click", () => downloadProjectSrt("vi"));
    }

    if (btnModalCopyZhSrt) {
        btnModalCopyZhSrt.addEventListener("click", async () => {
            const srtText = buildLocalSrtString("zh");
            if (!srtText) {
                alert("Chưa có phụ đề nào để copy.");
                return;
            }
            try {
                await navigator.clipboard.writeText(srtText);
                const oldHTML = btnModalCopyZhSrt.innerHTML;
                btnModalCopyZhSrt.innerHTML = `<i class="fa-solid fa-check"></i> Đã Copy SRT Trung!`;
                setTimeout(() => {
                    btnModalCopyZhSrt.innerHTML = oldHTML;
                }, 1800);
            } catch (e) {
                if (textareaImportSrt) {
                    textareaImportSrt.value = srtText;
                    textareaImportSrt.select();
                }
            }
        });
    }

    if (btnOpenImportSrt && modalSrtImport) {
        btnOpenImportSrt.addEventListener("click", () => {
            modalSrtImport.classList.remove("d-none");
        });
    }

    [btnCloseSrtModal, btnCancelSrtModal].forEach(btn => {
        if (btn && modalSrtImport) {
            btn.addEventListener("click", () => {
                modalSrtImport.classList.add("d-none");
            });
        }
    });

    if (btnChooseSrtFile && inputFileSrtVi) {
        btnChooseSrtFile.addEventListener("click", () => {
            inputFileSrtVi.value = "";
            inputFileSrtVi.click();
        });

        inputFileSrtVi.addEventListener("change", (e) => {
            const file = e.target.files && e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (evt) => {
                if (textareaImportSrt) {
                    textareaImportSrt.value = evt.target.result || "";
                }
            };
            reader.readAsText(file, "utf-8");
        });
    }

    if (btnApplySrtImport) {
        btnApplySrtImport.addEventListener("click", async () => {
            if (!currentProjectId) {
                alert("Chưa có dự án nào đang mở.");
                return;
            }
            const srtContent = textareaImportSrt ? textareaImportSrt.value.trim() : "";
            if (!srtContent) {
                alert("Vui lòng chọn file .SRT hoặc dán nội dung bản dịch tiếng Việt vào ô.");
                return;
            }

            const origHTML = btnApplySrtImport.innerHTML;
            btnApplySrtImport.disabled = true;
            btnApplySrtImport.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang gắn & đồng bộ...`;

            try {
                const res = await fetch(`/api/project/${currentProjectId}/import-srt`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        srt_content: srtContent,
                        target_field: "translation"
                    })
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể nhập file SRT.");
                }
                const data = await res.json();
                if (data.segments) {
                    renderSegmentsTable(data.segments);
                }
                if (modalSrtImport) {
                    modalSrtImport.classList.add("d-none");
                }
                setSaveStatus("saved", `Đã gắn ${data.count || 0} câu từ SRT!`);
                refreshPreviewDubbedAudio();
            } catch (err) {
                alert("Lỗi khi gắn SRT: " + err.message);
            } finally {
                btnApplySrtImport.disabled = false;
                btnApplySrtImport.innerHTML = origHTML;
            }
        });
    }

    // ==========================================
    // INITIALIZATION & PROJECT RESTORE
    // ==========================================
    async function initStudioSession() {
        const savedProjId = localStorage.getItem("current_project_id");
        if (savedProjId) {
            try {
                const res = await fetch(`/api/projects/${savedProjId}`);
                if (res.ok) {
                    await openProject(savedProjId, false);
                    return;
                }
            } catch (e) {
                console.warn("Could not restore saved project", e);
            }
        }

        // Check if there are any existing projects on server
        try {
            const listRes = await fetch("/api/projects");
            if (listRes.ok) {
                const list = await listRes.json();
                if (list && list.length > 0) {
                    await openProject(list[0].id, false);
                    return;
                }
            }
        } catch (e) {
            console.warn("Could not check project list", e);
        }

        // If no existing project, create a fresh draft project
        await createNewProject(false);
    }

    initStudioSession();

    // ==========================================
    // RVC MODEL LOADER & VISIBILITY LOGIC
    // ==========================================
    function updateRvcPitchVisibility() {
        if (!rvcPitchRow || !rvcModelSelectStep3) return;
        const isRvcActive = rvcModelSelectStep3.value && rvcModelSelectStep3.value !== "none";
        rvcPitchRow.style.display = isRvcActive ? "grid" : "none";
    }

    async function loadRvcModels(selectedModel = null) {
        if (!rvcModelSelectStep3) return;
        try {
            const res = await fetch("/api/rvc-models");
            if (res.ok) {
                const data = await res.json();
                const models = data.models || [];
                const currentVal = selectedModel || rvcModelSelectStep3.value || "none";
                rvcModelSelectStep3.innerHTML = '<option value="none">Không dùng (Chỉ giữ Edge-TTS gốc)</option>';
                if (models.length > 0) {
                    models.forEach(m => {
                        const opt = document.createElement("option");
                        opt.value = m.id;
                        opt.textContent = `${m.name} (${m.size_mb} MB${m.has_index ? " + index" : ""})`;
                        rvcModelSelectStep3.appendChild(opt);
                    });
                    if (rvcStatusHint) {
                        rvcStatusHint.textContent = `Đã tìm thấy ${models.length} model RVC trong app/models/rvc/`;
                        rvcStatusHint.style.color = "var(--success, #10b981)";
                    }
                } else {
                    if (rvcStatusHint) {
                        rvcStatusHint.innerHTML = 'Thả file <code>.pth</code> & <code>.index</code> vào <code>app/models/rvc/</code> để tự động nhận diện.';
                        rvcStatusHint.style.color = "var(--text-muted, #94a3b8)";
                    }
                }
                if (currentVal && (currentVal === "none" || models.some(m => m.id === currentVal))) {
                    rvcModelSelectStep3.value = currentVal;
                }
                updateRvcPitchVisibility();
            }
        } catch (e) {
            console.error("Lỗi khi quét RVC models:", e);
        }
    }

    if (rvcModelSelectStep3) {
        rvcModelSelectStep3.addEventListener("change", updateRvcPitchVisibility);
    }
    if (btnRefreshRvc) {
        btnRefreshRvc.addEventListener("click", () => {
            btnRefreshRvc.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
            loadRvcModels(rvcModelSelectStep3 ? rvcModelSelectStep3.value : null).finally(() => {
                btnRefreshRvc.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Quét lại';
            });
        });
    }
    if (rvcPitchSlider && rvcPitchVal) {
        rvcPitchSlider.addEventListener("input", () => {
            const val = parseInt(rvcPitchSlider.value);
            rvcPitchVal.textContent = val > 0 ? `+${val}` : val;
        });
    }

    // Load RVC models on startup
    loadRvcModels();

});
