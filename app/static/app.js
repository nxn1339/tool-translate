document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // GLOBAL TOAST NOTIFICATION SYSTEM
    // ==========================================
    function showToast(message, type = "info") {
        let container = document.getElementById("toast-global-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "toast-global-container";
            container.style.cssText = "position: fixed; top: 24px; right: 24px; z-index: 999999; display: flex; flex-direction: column; gap: 10px; pointer-events: none;";
            document.body.appendChild(container);
        }
        const toast = document.createElement("div");
        const colors = {
            success: { bg: "#10b981", icon: "fa-solid fa-circle-check" },
            error: { bg: "#ef4444", icon: "fa-solid fa-circle-xmark" },
            warning: { bg: "#f59e0b", icon: "fa-solid fa-triangle-exclamation" },
            info: { bg: "#0095f6", icon: "fa-solid fa-circle-info" }
        };
        const conf = colors[type] || colors.info;
        toast.style.cssText = `background: rgba(15, 23, 42, 0.95); border: 1px solid ${conf.bg}; border-left: 5px solid ${conf.bg}; color: #ffffff; padding: 12px 18px; border-radius: 10px; font-size: 0.92rem; font-weight: 600; box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: flex; align-items: center; gap: 10px; min-width: 260px; max-width: 440px; pointer-events: auto; transform: translateX(50px); opacity: 0; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);`;
        toast.innerHTML = `<i class="${conf.icon}" style="color: ${conf.bg}; font-size: 1.15rem;"></i> <span>${message}</span>`;
        container.appendChild(toast);
        requestAnimationFrame(() => {
            toast.style.transform = "translateX(0)";
            toast.style.opacity = "1";
        });
        setTimeout(() => {
            toast.style.transform = "translateX(50px)";
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
    window.showToast = showToast;

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
    let logoBoxCoords = { x: 78, y: 5, w: 18, h: 12, opacity: 1.0, enabled: false, filename: null, image_path: null, keep_aspect: true };

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
    const bboxLogo = document.getElementById("bbox-logo");
    const bboxLogoImg = document.getElementById("bbox-logo-img");
    const bboxLogoPlaceholder = document.getElementById("bbox-logo-placeholder");
    const logoEnabled = document.getElementById("logo-enabled");
    const logoStatusLabel = document.getElementById("logo-status-label");
    const logoControlsBody = document.getElementById("logo-controls-body");
    const logoFileInput = document.getElementById("logo-file-input");
    const btnUploadLogo = document.getElementById("btn-upload-logo");
    const btnToggleLogoBoxPreview = document.getElementById("btn-toggle-logo-box-preview");
    const logoFilenameDisplay = document.getElementById("logo-filename-display");
    const logoSliderW = document.getElementById("logo-slider-w");
    const logoWVal = document.getElementById("logo-w-val");
    const logoSliderOpacity = document.getElementById("logo-slider-opacity");
    const logoOpacityVal = document.getElementById("logo-opacity-val");
    const logoSliderX = document.getElementById("logo-slider-x");
    const logoXVal = document.getElementById("logo-x-val");
    const logoSliderY = document.getElementById("logo-slider-y");
    const logoYVal = document.getElementById("logo-y-val");
    const summaryLogoStatus = document.getElementById("summary-logo-status");
    const logoPosBtns = document.querySelectorAll(".logo-pos-btn");
    const step3LogoToolbar = document.getElementById("step3-logo-toolbar");
    const step3LogoEnabled = document.getElementById("step3-logo-enabled");
    const step3LogoStatusLabel = document.getElementById("step3-logo-status-label");
    const step3LogoOptions = document.getElementById("step3-logo-options");
    const step3LogoFileInput = document.getElementById("step3-logo-file-input");
    const step3BtnUploadLogo = document.getElementById("step3-btn-upload-logo");
    const step3BtnToggleLogoBox = document.getElementById("step3-btn-toggle-logo-box");
    const step3LogoFilenameDisplay = document.getElementById("step3-logo-filename-display");
    const step3LogoSliderW = document.getElementById("step3-logo-slider-w");
    const step3LogoWVal = document.getElementById("step3-logo-w-val");
    const step3LogoSliderOpacity = document.getElementById("step3-logo-slider-opacity");
    const step3LogoOpacityVal = document.getElementById("step3-logo-opacity-val");
    const step3LogoSliderX = document.getElementById("step3-logo-slider-x");
    const step3LogoXVal = document.getElementById("step3-logo-x-val");
    const step3LogoSliderY = document.getElementById("step3-logo-slider-y");
    const step3LogoYVal = document.getElementById("step3-logo-y-val");
    const btnQuickCanvasLogo = document.getElementById("btn-quick-canvas-logo");

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
        if (bboxLogo) {
            bboxLogo.style.left = logoBoxCoords.x + "%";
            bboxLogo.style.top = logoBoxCoords.y + "%";
            bboxLogo.style.width = logoBoxCoords.w + "%";
            bboxLogo.style.height = logoBoxCoords.h + "%";
            if (bboxLogoImg) {
                bboxLogoImg.style.opacity = logoBoxCoords.opacity;
            }
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
                triggerDebouncedAutoSave(600);
            }

            document.addEventListener("mousemove", onMouseMove);
            document.addEventListener("mouseup", onMouseUp);
        });
    }

    // Setup Red Box (Mask) Drag & Resize - Luôn đồng bộ Khung Xanh theo Khung Đỏ
    setupDragAndResize(
        bboxMask,
        () => maskBoxCoords,
        (newCoords) => {
            maskBoxCoords = newCoords;
            subBoxCoords = { ...newCoords };
            applyBoxStyles();
        },
        (newCoords) => {
            subBoxCoords = { ...newCoords };
            applyBoxStyles();
        }
    );

    // Setup Green Box (Subtitle) Drag & Resize - Luôn đồng bộ vùng che mờ (maskBoxCoords) theo Khung Xanh
    setupDragAndResize(
        bboxSub,
        () => subBoxCoords,
        (newCoords) => {
            subBoxCoords = newCoords;
            maskBoxCoords = { ...newCoords };
            applyBoxStyles();
        },
        (newCoords) => {
            maskBoxCoords = { ...newCoords };
            applyBoxStyles();
        }
    );

    // Setup Blue/Amber Box (Logo) Drag & Resize
    if (bboxLogo) {
        setupDragAndResize(
            bboxLogo,
            () => logoBoxCoords,
            (newCoords) => {
                logoBoxCoords.x = Math.round(newCoords.x);
                logoBoxCoords.y = Math.round(newCoords.y);
                logoBoxCoords.w = Math.round(newCoords.w);
                logoBoxCoords.h = Math.round(newCoords.h);
                syncLogoSlidersFromCoords();
                triggerDebouncedAutoSave(1000);
            },
            null
        );
    }

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
            subBoxCoords = { ...maskBoxCoords };
            applyBoxStyles();
            triggerDebouncedAutoSave(500);
        });
    }

    if (btnPresetTop) {
        btnPresetTop.addEventListener("click", () => {
            maskBoxCoords = { x: 10, y: 8, w: 80, h: 14 };
            subBoxCoords = { ...maskBoxCoords };
            applyBoxStyles();
            triggerDebouncedAutoSave(500);
        });
    }

    if (btnPresetReset) {
        btnPresetReset.addEventListener("click", () => {
            maskBoxCoords = { x: 10, y: 78, w: 80, h: 14 };
            subBoxCoords = { x: 10, y: 78, w: 80, h: 14 };
            applyBoxStyles();
            triggerDebouncedAutoSave(500);
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

    // Terminal Elements - Step 1
    const step1TerminalBox = document.getElementById("step1-terminal-box");
    const step1TerminalLogs = document.getElementById("step1-terminal-logs");
    const step1TerminalBody = document.getElementById("step1-terminal-body");
    const step1TerminalStatusTag = document.getElementById("step1-terminal-status-tag");
    const btnStep1TerminalToggle = document.getElementById("btn-step1-terminal-toggle");
    const step1TerminalToggleIcon = document.getElementById("step1-terminal-toggle-icon");
    const step1TerminalToggleText = document.getElementById("step1-terminal-toggle-text");
    const btnStep1TerminalCopy = document.getElementById("btn-step1-terminal-copy");
    const btnStep1TerminalClear = document.getElementById("btn-step1-terminal-clear");
    let lastRenderedLogsCount = 0;
    let autoScrollTerminal = true;

    if (step1TerminalBody) {
        step1TerminalBody.addEventListener("scroll", () => {
            const isNearBottom = (step1TerminalBody.scrollHeight - step1TerminalBody.scrollTop - step1TerminalBody.clientHeight) < 30;
            autoScrollTerminal = isNearBottom;
        });
    }

    function parseLogLine(rawLine) {
        const m = rawLine.match(/^\[(\d{2}:\d{2}:\d{2})\]\s*(?:\[(INFO|WARN|ERROR|SUCCESS|Cảnh báo|Lỗi)\])?\s*(.*)$/i);
        if (m) {
            const time = m[1];
            let lvl = (m[2] || "INFO").toUpperCase();
            if (lvl === "CẢNH BÁO") lvl = "WARN";
            if (lvl === "LỖI") lvl = "ERROR";
            const text = m[3];
            return { time, level: lvl, text };
        }
        return { time: "", level: "INFO", text: rawLine };
    }

    function appendTerminalLog(rawLine) {
        if (!step1TerminalLogs) return;
        const { time, level, text } = parseLogLine(rawLine);
        const lineEl = document.createElement("div");
        lineEl.className = `terminal-line term-type-${level.toLowerCase()}`;

        let badgeClass = "term-badge-info";
        let badgeLabel = level;
        if (level === "WARN") { badgeClass = "term-badge-warn"; badgeLabel = "CẢNH BÁO"; }
        else if (level === "ERROR") { badgeClass = "term-badge-error"; badgeLabel = "LỖI"; }
        else if (level === "SUCCESS") { badgeClass = "term-badge-success"; badgeLabel = "XONG"; }

        lineEl.innerHTML = `
            ${time ? `<span class="term-time">[${time}]</span>` : ''}
            <span class="term-badge ${badgeClass}">[${badgeLabel}]</span>
            <span class="term-text">${escapeHtml(text)}</span>
        `;
        step1TerminalLogs.appendChild(lineEl);

        if (autoScrollTerminal && step1TerminalBody) {
            step1TerminalBody.scrollTop = step1TerminalBody.scrollHeight;
        }
    }

    let lastRenderedLogsList = [];

    function clearTerminalUI() {
        if (step1TerminalLogs) step1TerminalLogs.innerHTML = "";
        lastRenderedLogsList = [];
        lastRenderedLogsCount = 0;
    }

    function updateTerminalLogs(logs) {
        if (!Array.isArray(logs) || !step1TerminalLogs) return;
        if (logs.length === 0) return;

        // If nothing is rendered yet, render all
        if (lastRenderedLogsList.length === 0) {
            step1TerminalLogs.innerHTML = "";
            for (const line of logs) {
                appendTerminalLog(line);
            }
            lastRenderedLogsList = [...logs];
            lastRenderedLogsCount = logs.length;
            return;
        }

        const lastOld = lastRenderedLogsList[lastRenderedLogsList.length - 1];
        const lastNew = logs[logs.length - 1];
        if (lastOld === lastNew && lastRenderedLogsList.length === logs.length) {
            return;
        }

        // Find match of lastOld in logs
        let lastMatchedIndex = -1;
        for (let i = logs.length - 1; i >= 0; i--) {
            if (logs[i] === lastOld) {
                lastMatchedIndex = i;
                break;
            }
        }

        if (lastMatchedIndex !== -1) {
            for (let i = lastMatchedIndex + 1; i < logs.length; i++) {
                appendTerminalLog(logs[i]);
            }
            lastRenderedLogsList = [...logs];
            lastRenderedLogsCount = logs.length;
        } else {
            // Either sliding window passed or project switched
            if (logs[0] !== lastRenderedLogsList[0]) {
                step1TerminalLogs.innerHTML = "";
                for (const line of logs) {
                    appendTerminalLog(line);
                }
            } else {
                const renderedSet = new Set(lastRenderedLogsList);
                for (const line of logs) {
                    if (!renderedSet.has(line)) {
                        appendTerminalLog(line);
                    }
                }
            }
            lastRenderedLogsList = [...logs];
            lastRenderedLogsCount = logs.length;
        }
    }

    const btnToggleTerminalGlobal = document.getElementById("btn-toggle-terminal-global");
    const lblToggleTerminalGlobal = document.getElementById("lbl-toggle-terminal-global");

    function setTerminalVisible(visible) {
        if (!step1TerminalBox) return;
        if (visible) {
            step1TerminalBox.classList.remove("d-none");
            if (lblToggleTerminalGlobal) lblToggleTerminalGlobal.textContent = "Ẩn Terminal";
        } else {
            step1TerminalBox.classList.add("d-none");
            if (lblToggleTerminalGlobal) lblToggleTerminalGlobal.textContent = "Mở Terminal";
        }
    }

    if (btnToggleTerminalGlobal) {
        btnToggleTerminalGlobal.addEventListener("click", () => {
            if (!step1TerminalBox) return;
            const isCurrentlyHidden = step1TerminalBox.classList.contains("d-none");
            setTerminalVisible(isCurrentlyHidden);
            if (isCurrentlyHidden && step1TerminalBody) {
                step1TerminalBody.scrollTop = step1TerminalBody.scrollHeight;
            }
        });
    }

    if (btnStep1TerminalToggle) {
        btnStep1TerminalToggle.addEventListener("click", () => {
            if (!step1TerminalBox) return;
            const isCollapsed = step1TerminalBox.classList.toggle("collapsed");
            if (step1TerminalToggleIcon) {
                step1TerminalToggleIcon.className = isCollapsed ? "fa-solid fa-chevron-down" : "fa-solid fa-chevron-up";
            }
            if (step1TerminalToggleText) {
                step1TerminalToggleText.textContent = isCollapsed ? "Mở rộng" : "Thu gọn";
            }
        });
    }

    if (btnStep1TerminalClear) {
        btnStep1TerminalClear.addEventListener("click", () => {
            clearTerminalUI();
        });
    }

    if (btnStep1TerminalCopy) {
        btnStep1TerminalCopy.addEventListener("click", () => {
            if (!step1TerminalLogs) return;
            const text = step1TerminalLogs.innerText;
            navigator.clipboard.writeText(text).then(() => {
                const origHtml = btnStep1TerminalCopy.innerHTML;
                btnStep1TerminalCopy.innerHTML = '<i class="fa-solid fa-check"></i> <span>Đã chép</span>';
                setTimeout(() => { btnStep1TerminalCopy.innerHTML = origHtml; }, 1500);
            });
        });
    }

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
        2: "Bước 2: Quét Chữ Gốc",
        3: "Bước 3: Dịch Phụ Đề",
        4: "Bước 4: Tạo Giọng Đọc",
        5: "Bước 5: Chèn Logo",
        6: "Bước 6: Xuất Video"
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
                bg_volume: bgVolumeSlider ? parseFloat(bgVolumeSlider.value) : 0.15,
                tts_volume: ttsVolumeSlider ? parseFloat(ttsVolumeSlider.value) : 1.0,
                auto_extend_video: document.getElementById("chk-auto-extend-video") ? document.getElementById("chk-auto-extend-video").checked : false,
                logo_box: {
                    enabled: Boolean(logoBoxCoords.enabled),
                    x: Number(logoBoxCoords.x ?? 78),
                    y: Number(logoBoxCoords.y ?? 5),
                    w: Number(logoBoxCoords.w ?? 18),
                    h: Number(logoBoxCoords.h ?? 12),
                    opacity: Number(logoBoxCoords.opacity ?? 1.0),
                    keep_aspect: Boolean(logoBoxCoords.keep_aspect ?? true),
                    filename: logoBoxCoords.filename || null,
                    image_path: logoBoxCoords.image_path || null
                },
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

            logoBoxCoords = { x: 78, y: 5, w: 18, h: 12, opacity: 1.0, enabled: false, filename: null, image_path: null, keep_aspect: true };
            updateLogoUIFromState();
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

            // Populate logo_box
            if (meta.logo_box) {
                logoBoxCoords = {
                    x: meta.logo_box.x ?? 78,
                    y: meta.logo_box.y ?? 5,
                    w: meta.logo_box.w ?? 18,
                    h: meta.logo_box.h ?? 12,
                    opacity: meta.logo_box.opacity ?? 1.0,
                    enabled: Boolean(meta.logo_box.enabled),
                    filename: meta.logo_box.filename || null,
                    image_path: meta.logo_box.image_path || null,
                    keep_aspect: meta.logo_box.keep_aspect ?? true
                };
                updateLogoUIFromState();
            } else {
                logoBoxCoords.enabled = false;
                updateLogoUIFromState();
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
            [1, 2, 3, 4, 5].forEach(s => {
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
            const targetStep = meta.current_step || (completed.length > 0 ? Math.min(Math.max(...completed) + 1, 6) : 1);
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

            // Sync status logs to live terminal
            try {
                const statusRes = await fetch(`/api/project/${meta.id}/status`);
                if (statusRes.ok) {
                    const statusData = await statusRes.json();
                    if (statusData.logs && statusData.logs.length > 0) {
                        updateTerminalLogs(statusData.logs);
                        setTerminalVisible(true);
                    }
                }
            } catch (e) {
                console.warn("Could not sync terminal logs on project open", e);
            }

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
            // Bước 1: Ẩn tất cả khung
            bboxMask.classList.add("d-none");
            bboxSub.classList.add("d-none");
            if (bboxLogo) bboxLogo.classList.add("d-none");
        } else if (currentStudioStep === 2) {
            // Bước 2: Chỉ hiện khung OCR tiếng Trung (nếu chọn mode OCR)
            bboxSub.classList.add("d-none");
            if (bboxLogo) {
                if (logoBoxCoords.enabled) bboxLogo.classList.remove("d-none");
                else bboxLogo.classList.add("d-none");
            }
            if (currentTranscribeMode === "ocr") {
                bboxMask.classList.remove("d-none");
            } else {
                bboxMask.classList.add("d-none");
            }
        } else if (currentStudioStep === 3 || currentStudioStep === 4) {
            // Bước 3 & 4: Hiện khung Sub Việt và khung Logo (nếu đang bật)
            bboxSub.classList.remove("d-none");
            bboxMask.classList.add("d-none");
            if (bboxLogo) {
                if (logoBoxCoords.enabled) bboxLogo.classList.remove("d-none");
                else bboxLogo.classList.add("d-none");
            }
        } else if (currentStudioStep === 5) {
            // Bước 5: Chèn Logo -> Luôn hiện khung Logo (hoặc nếu enabled) và Sub Việt để dễ căn chỉnh
            bboxSub.classList.remove("d-none");
            bboxMask.classList.add("d-none");
            if (bboxLogo) {
                if (logoBoxCoords.enabled || logoBoxCoords.filename || logoBoxCoords.image_path) {
                    bboxLogo.classList.remove("d-none");
                } else {
                    bboxLogo.classList.remove("d-none");
                }
            }
        } else if (currentStudioStep === 6) {
            // Bước 6: Xuất video hoàn chỉnh
            bboxSub.classList.remove("d-none");
            bboxMask.classList.add("d-none");
            if (bboxLogo) {
                if (logoBoxCoords.enabled) bboxLogo.classList.remove("d-none");
                else bboxLogo.classList.add("d-none");
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

        // Hiển thị / ẩn bảng phụ đề bên dưới player (Hiện ở Bước 2, 3, 4, 5 nếu đã có sub)
        if (subtitleEditorCard) {
            if ((stepNum >= 2 && stepNum <= 5) && segmentsData && segmentsData.length > 0) {
                subtitleEditorCard.classList.remove("d-none");
            } else if (stepNum === 1 || stepNum === 6) {
                subtitleEditorCard.classList.add("d-none");
            }
        }

        // Cập nhật tóm tắt khi sang Bước 6
        if (stepNum === 6) {
            updateStep4Summary();
        } else if (stepNum === 4) {
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

            if (step1TerminalBox) {
                step1TerminalBox.classList.remove("d-none");
                step1TerminalBox.classList.remove("collapsed");
            }
            if (step1TerminalStatusTag) {
                step1TerminalStatusTag.className = "terminal-status-tag";
                step1TerminalStatusTag.textContent = "Đang tải";
            }
            if (step1TerminalLogs) {
                step1TerminalLogs.innerHTML = `<div class="terminal-line"><span class="term-time">[${new Date().toTimeString().slice(0, 8)}]</span><span class="term-badge term-badge-info">[Bắt đầu]</span><span class="term-text">Khởi tạo kết nối tải video từ: ${escapeHtml(url)}...</span></div>`;
            }
            lastRenderedLogsCount = 1;
            autoScrollTerminal = true;

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

                        const curPct = Math.min(100, Math.max(0, parseInt(statusData.progress) || 0));
                        if (step1ProgressBar) step1ProgressBar.style.width = `${curPct}%`;
                        if (step1ProgressPct) step1ProgressPct.textContent = `${curPct}%`;
                        if (step1ProgressMsg) step1ProgressMsg.textContent = statusData.message || `Đang tải... (${curPct}%)`;

                        if (statusData.logs && Array.isArray(statusData.logs)) {
                            updateTerminalLogs(statusData.logs);
                        }

                        if (statusData.status === "downloaded") {
                            clearInterval(pollingInterval);
                            btnStep1Download.disabled = false;
                            if (step1ProgressBar) step1ProgressBar.style.width = "100%";
                            if (step1ProgressPct) step1ProgressPct.textContent = "100%";
                            if (step1ProgressMsg) step1ProgressMsg.textContent = "Tải video hoàn tất!";
                            if (step1TerminalStatusTag) {
                                step1TerminalStatusTag.className = "terminal-status-tag status-done";
                                step1TerminalStatusTag.textContent = "Hoàn tất";
                            }

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
                            if (step1TerminalStatusTag) {
                                step1TerminalStatusTag.className = "terminal-status-tag status-error";
                                step1TerminalStatusTag.textContent = "Thất bại";
                            }
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
                if (step1TerminalStatusTag) {
                    step1TerminalStatusTag.className = "terminal-status-tag status-error";
                    step1TerminalStatusTag.textContent = "Lỗi";
                }
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
            return `<span class="badge-pace badge-warn" title="Hơi nhiều từ, sẽ đọc nhanh hơn một chút"><i class="fa-solid fa-triangle-exclamation"></i> ${words} từ / ${dur.toFixed(1)}s • Đọc nhanh ~${(pace / 3.4).toFixed(1)}x</span>`;
        } else {
            return `<span class="badge-pace badge-danger" title="Quá nhiều từ so với số giây video! Nên gọt bớt chữ để giọng đọc rõ nét"><i class="fa-solid fa-bolt"></i> ${words} từ / ${dur.toFixed(1)}s • Quá dài (~${(pace / 3.4).toFixed(1)}x)! Nên rút gọn</span>`;
        }
    }

    function updateFailedTtsUI(failedCount) {
        const btnRetryFailedTTS = document.getElementById("btn-retry-failed-tts");
        const failedTtsCount = document.getElementById("failed-tts-count");
        if (btnRetryFailedTTS) {
            if (failedCount > 0) {
                btnRetryFailedTTS.classList.remove("d-none");
                if (failedTtsCount) failedTtsCount.textContent = failedCount;
            } else {
                btnRetryFailedTTS.classList.add("d-none");
            }
        }
    }

    let filterOnlyChineseWarn = false;
    const FOREIGN_SCRIPT_REGEX = /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af\u0400-\u04ff]+/g;

    function extractForeignChars(text) {
        if (!text) return "";
        const matches = String(text).match(FOREIGN_SCRIPT_REGEX);
        return matches ? matches.join("") : "";
    }

    function getForeignWarningBadgeHTML(text) {
        const chars = extractForeignChars(text);
        if (!chars) return "";
        const displayChars = chars.length > 8 ? chars.slice(0, 8) + "..." : chars;
        return `<span class="badge-chinese-warn" style="display:inline-flex;align-items:center;gap:4px;background:rgba(249,115,22,0.22);color:#fdba74;border:1px solid rgba(249,115,22,0.55);border-radius:4px;padding:1px 6px;font-size:0.72rem;margin-left:6px;font-weight:700;" title="Cảnh báo: Câu dịch vẫn còn ký tự tiếng Trung / ngoại ngữ chưa dịch hết (${chars})"><i class="fa-solid fa-language"></i> Sót chữ Hán: ${displayChars}</span>`;
    }

    function applyChineseFilterToTable() {
        if (!subtitleTableBody) return;
        const rows = subtitleTableBody.querySelectorAll("tr");
        rows.forEach(tr => {
            if (!filterOnlyChineseWarn) {
                tr.style.display = "";
            } else {
                const isFlagged = tr.dataset.hasForeign === "1" || tr.dataset.hasTransErr === "1";
                tr.style.display = isFlagged ? "" : "none";
            }
        });
    }

    function updateChineseWarnUI(chineseWarnCount) {
        const btnFilterChinese = document.getElementById("btn-filter-chinese");
        const countSpan = document.getElementById("count-chinese-warn");
        if (!btnFilterChinese) return;

        if (chineseWarnCount > 0) {
            btnFilterChinese.classList.remove("d-none");
            if (filterOnlyChineseWarn) {
                btnFilterChinese.style.background = "rgba(249, 115, 22, 0.35)";
                btnFilterChinese.style.borderColor = "#fb923c";
                btnFilterChinese.innerHTML = `<i class="fa-solid fa-filter-circle-xmark"></i> Đang lọc câu sót (<span id="count-chinese-warn">${chineseWarnCount}</span>) - Hiện tất cả`;
            } else {
                btnFilterChinese.style.background = "rgba(249, 115, 22, 0.15)";
                btnFilterChinese.style.borderColor = "#f97316";
                btnFilterChinese.innerHTML = `<i class="fa-solid fa-language"></i> Sót tiếng Trung (<span id="count-chinese-warn">${chineseWarnCount}</span>)`;
            }
        } else {
            filterOnlyChineseWarn = false;
            btnFilterChinese.classList.add("d-none");
            if (countSpan) countSpan.textContent = "0";
            applyChineseFilterToTable();
        }
    }

    const btnFilterChineseEl = document.getElementById("btn-filter-chinese");
    if (btnFilterChineseEl) {
        btnFilterChineseEl.addEventListener("click", () => {
            filterOnlyChineseWarn = !filterOnlyChineseWarn;
            const currentWarnCount = (segmentsData || []).filter(s => Boolean(extractForeignChars(s.translation))).length;
            updateChineseWarnUI(currentWarnCount);
            applyChineseFilterToTable();
        });
    }

    function updateFailedTransUI(failedCount) {
        const btnStep3Retry = document.getElementById("btn-step3-retry-failed-translate");
        const step3FailedCount = document.getElementById("step3-failed-trans-count");
        const btnTableRetry = document.getElementById("btn-retry-failed-translate");
        const tableFailedCount = document.getElementById("table-failed-trans-count");

        if (btnStep3Retry) {
            if (failedCount > 0) {
                btnStep3Retry.classList.remove("d-none");
                if (step3FailedCount) step3FailedCount.textContent = failedCount;
            } else {
                btnStep3Retry.classList.add("d-none");
            }
        }
        if (btnTableRetry) {
            if (failedCount > 0) {
                btnTableRetry.classList.remove("d-none");
                if (tableFailedCount) tableFailedCount.textContent = failedCount;
            } else {
                btnTableRetry.classList.add("d-none");
            }
        }
    }

    function renderSegmentsTable(segments) {
        segmentsData = segments;
        if (!subtitleTableBody) return;
        subtitleTableBody.innerHTML = "";
        if (segmentsCount) segmentsCount.textContent = segments.length;

        let failedCount = 0;
        let failedTransCount = 0;
        let chineseWarnCount = 0;

        segments.forEach((seg, index) => {
            const tr = document.createElement("tr");
            const startVal = seg.start != null ? Number(seg.start).toFixed(1) : "0.0";
            const endVal = seg.end != null ? Number(seg.end).toFixed(1) : "0.0";
            const dur = Math.max(0.1, Number(endVal) - Number(startVal));
            const curSpeed = seg.speed != null ? Number(seg.speed) : 1.0;

            const hasSourceText = Boolean(seg.text && seg.text.trim());
            const hasTranslation = Boolean(seg.translation && seg.translation.trim());
            const foreignChars = extractForeignChars(seg.translation);
            const hasForeignText = Boolean(foreignChars);
            const hasTransError = hasSourceText && (Boolean(seg.translation_error) || !hasTranslation);

            tr.dataset.hasForeign = hasForeignText ? "1" : "0";
            tr.dataset.hasTransErr = hasTransError ? "1" : "0";

            if (hasForeignText) {
                chineseWarnCount++;
            }

            if (hasTransError || hasForeignText) {
                failedTransCount++;
                tr.style.backgroundColor = hasTransError ? "rgba(239, 68, 68, 0.08)" : "rgba(249, 115, 22, 0.09)";
            }

            const hasError = hasTranslation && (Boolean(seg.tts_error) || !seg.audio_path || Number(seg.actual_duration) <= 0.05);
            if (hasError) {
                failedCount++;
                if (!hasTransError && !hasForeignText) tr.style.backgroundColor = "rgba(245, 158, 11, 0.08)";
            }

            const errorBadge = hasError ? `<span class="badge-tts-error" style="display:inline-flex;align-items:center;gap:3px;background:rgba(245,158,11,0.2);color:#fbbf24;border:1px solid rgba(245,158,11,0.45);border-radius:4px;padding:1px 6px;font-size:0.72rem;margin-left:6px;font-weight:700;" title="Chưa tạo được giọng đọc câu này"><i class="fa-solid fa-circle-exclamation"></i> Lỗi giọng</span>` : '';
            const transErrorBadge = hasTransError ? `<span class="badge-tts-error" style="display:inline-flex;align-items:center;gap:3px;background:rgba(239,68,68,0.2);color:#fca5a5;border:1px solid rgba(239,68,68,0.45);border-radius:4px;padding:1px 6px;font-size:0.72rem;margin-left:6px;font-weight:700;" title="Câu này chưa có bản dịch tiếng Việt"><i class="fa-solid fa-triangle-exclamation"></i> Chưa dịch</span>` : '';
            const foreignWarnBadge = getForeignWarningBadgeHTML(seg.translation);
            const inputWarnStyle = hasForeignText ? 'border-color: #f97316; background: rgba(249, 115, 22, 0.08);' : '';

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
                        <input type="text" class="sub-edit-input ${hasForeignText ? 'has-chinese-warn' : ''}" style="${inputWarnStyle}" data-index="${index}" value="${seg.translation ? seg.translation.replace(/"/g, '&quot;') : ''}" placeholder="Nhập bản dịch tiếng Việt (để trống = không đọc)...">
                        <div class="sub-duration-badge" id="sub-badge-${index}">${getDurationBadgeHTML(seg.translation, dur)}${transErrorBadge}${foreignWarnBadge}${errorBadge}</div>
                    </div>
                </td>
                <td style="text-align: center;">
                    <button type="button" class="btn-table-action btn-tts ${hasError ? 'btn-tts-err' : ''}" data-index="${index}" style="${hasError ? 'color: #f87171;' : ''}" title="${hasError ? 'Câu này chưa có âm thanh. Nhấn để tạo thử' : 'Nghe thử TTS câu này'}"><i class="fa-solid ${hasError ? 'fa-triangle-exclamation' : 'fa-volume-high'}"></i></button>
                    <button type="button" class="btn-table-action btn-del" data-index="${index}" title="Xóa dòng này"><i class="fa-solid fa-trash-can"></i></button>
                </td>
            `;
            subtitleTableBody.appendChild(tr);
        });

        updateFailedTtsUI(failedCount);
        updateFailedTransUI(failedTransCount);
        updateChineseWarnUI(chineseWarnCount);
        applyChineseFilterToTable();

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
                    const hasForeignNow = Boolean(extractForeignChars(input.value));
                    const tr = input.closest("tr");
                    if (tr) {
                        tr.dataset.hasForeign = hasForeignNow ? "1" : "0";
                        const isEmptyNow = !input.value.trim();
                        tr.dataset.hasTransErr = isEmptyNow ? "1" : "0";
                        tr.style.backgroundColor = isEmptyNow ? "rgba(239, 68, 68, 0.08)" : (hasForeignNow ? "rgba(249, 115, 22, 0.09)" : "");
                    }
                    input.style.borderColor = hasForeignNow ? "#f97316" : "";
                    input.style.background = hasForeignNow ? "rgba(249, 115, 22, 0.08)" : "";

                    const badge = document.getElementById(`sub-badge-${idx}`);
                    if (badge) {
                        const dur = Math.max(0.1, (segmentsData[idx].end || 0) - (segmentsData[idx].start || 0));
                        const foreignWarnBadge = getForeignWarningBadgeHTML(input.value);
                        badge.innerHTML = `${getDurationBadgeHTML(input.value, dur)}${foreignWarnBadge}`;
                    }

                    const newWarnCount = segmentsData.filter(s => Boolean(extractForeignChars(s.translation))).length;
                    const newFailedTransCount = segmentsData.filter(s => (s.text && s.text.trim()) && (Boolean(s.translation_error) || !(s.translation && s.translation.trim()) || Boolean(extractForeignChars(s.translation)))).length;
                    updateChineseWarnUI(newWarnCount);
                    updateFailedTransUI(newFailedTransCount);
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
            const res = await fetch(`/api/project/${currentProjectId}/preview-audio`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ voice })
            });
            if (res.ok) {
                try {
                    const stRes = await fetch(`/api/project/${currentProjectId}/status`);
                    if (stRes.ok) {
                        const stData = await stRes.json();
                        if (stData.logs) updateTerminalLogs(stData.logs);
                    }
                } catch (_) { }
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
                dubbingAudio.play().catch(e => { });
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

    // ==========================================
    // LIGHTWEIGHT VIDEO SCRUBBER BAR CONTROLLER (ZERO LAG)
    // ==========================================
    const videoSeekSlider = document.getElementById("video-seek-slider");
    const scrubberTrackFill = document.getElementById("scrubber-track-fill");
    const scrubCurrentTime = document.getElementById("scrub-current-time");
    const scrubTotalTime = document.getElementById("scrub-total-time");
    const btnScrubPlay = document.getElementById("btn-scrub-play");
    const iconScrubPlay = document.getElementById("icon-scrub-play");
    const btnScrubBack5 = document.getElementById("btn-scrub-back5");
    const btnScrubFwd5 = document.getElementById("btn-scrub-fwd5");
    const btnScrubPrevSub = document.getElementById("btn-scrub-prev-sub");
    const btnScrubNextSub = document.getElementById("btn-scrub-next-sub");

    let isScrubbingSlider = false;

    function updateScrubberUI(curTime, totalDur) {
        if (!totalDur || isNaN(totalDur) || totalDur <= 0) {
            totalDur = getTimelineTotalDuration();
        }
        if (curTime == null || isNaN(curTime)) {
            curTime = previewVideoElement ? (previewVideoElement.currentTime || 0) : 0;
        }

        if (scrubCurrentTime) scrubCurrentTime.textContent = formatTime(curTime);
        if (scrubTotalTime) scrubTotalTime.textContent = formatTime(totalDur);

        const pct = Math.max(0, Math.min(100, (curTime / totalDur) * 100));
        if (scrubberTrackFill) {
            scrubberTrackFill.style.width = `${pct}%`;
        }
        if (videoSeekSlider && !isScrubbingSlider) {
            videoSeekSlider.max = String(totalDur);
            videoSeekSlider.value = String(curTime);
        }

        if (iconScrubPlay && previewVideoElement) {
            iconScrubPlay.className = previewVideoElement.paused ? "fa-solid fa-play" : "fa-solid fa-pause";
        }
    }

    if (videoSeekSlider) {
        videoSeekSlider.addEventListener("input", () => {
            isScrubbingSlider = true;
            const targetTime = parseFloat(videoSeekSlider.value) || 0;
            const totalDur = getTimelineTotalDuration();
            const pct = Math.max(0, Math.min(100, (targetTime / totalDur) * 100));
            if (scrubberTrackFill) scrubberTrackFill.style.width = `${pct}%`;
            if (scrubCurrentTime) scrubCurrentTime.textContent = formatTime(targetTime);

            if (previewVideoElement) {
                previewVideoElement.currentTime = targetTime;
                updatePreviewSubtitle();
            }
        });

        videoSeekSlider.addEventListener("change", () => {
            const targetTime = parseFloat(videoSeekSlider.value) || 0;
            if (previewVideoElement) {
                previewVideoElement.currentTime = targetTime;
                updatePreviewSubtitle();
                syncDubbingAudioSeek();
            }
            setTimeout(() => {
                isScrubbingSlider = false;
            }, 50);
        });

        videoSeekSlider.addEventListener("pointerdown", () => { isScrubbingSlider = true; });
        videoSeekSlider.addEventListener("pointerup", () => { isScrubbingSlider = false; });
    }

    if (btnScrubPlay) {
        btnScrubPlay.addEventListener("click", () => {
            if (!previewVideoElement) return;
            if (previewVideoElement.paused) {
                previewVideoElement.play();
            } else {
                previewVideoElement.pause();
            }
        });
    }

    if (btnScrubBack5) {
        btnScrubBack5.addEventListener("click", () => {
            if (!previewVideoElement) return;
            previewVideoElement.currentTime = Math.max(0, (previewVideoElement.currentTime || 0) - 5);
            updateScrubberUI(previewVideoElement.currentTime, getTimelineTotalDuration());
            updatePreviewSubtitle();
            syncDubbingAudioSeek();
        });
    }

    if (btnScrubFwd5) {
        btnScrubFwd5.addEventListener("click", () => {
            if (!previewVideoElement) return;
            const totalDur = getTimelineTotalDuration();
            previewVideoElement.currentTime = Math.min(totalDur, (previewVideoElement.currentTime || 0) + 5);
            updateScrubberUI(previewVideoElement.currentTime, totalDur);
            updatePreviewSubtitle();
            syncDubbingAudioSeek();
        });
    }

    if (btnScrubPrevSub) {
        btnScrubPrevSub.addEventListener("click", () => {
            if (!segmentsData || segmentsData.length === 0 || !previewVideoElement) return;
            const cur = previewVideoElement.currentTime || 0;
            let prevIdx = -1;
            for (let i = segmentsData.length - 1; i >= 0; i--) {
                const s = Number(segmentsData[i].start || 0);
                if (s < cur - 0.3) {
                    prevIdx = i;
                    break;
                }
            }
            if (prevIdx >= 0) {
                selectClip(prevIdx, true);
            } else if (segmentsData.length > 0) {
                selectClip(0, true);
            }
        });
    }

    if (btnScrubNextSub) {
        btnScrubNextSub.addEventListener("click", () => {
            if (!segmentsData || segmentsData.length === 0 || !previewVideoElement) return;
            const cur = previewVideoElement.currentTime || 0;
            let nextIdx = -1;
            for (let i = 0; i < segmentsData.length; i++) {
                const s = Number(segmentsData[i].start || 0);
                if (s > cur + 0.1) {
                    nextIdx = i;
                    break;
                }
            }
            if (nextIdx >= 0) {
                selectClip(nextIdx, true);
            }
        });
    }

    if (previewVideoElement) {
        previewVideoElement.addEventListener("timeupdate", () => {
            updatePreviewSubtitle();
            syncTimelinePlayhead();
            syncDubbingAudioTime();
            updateScrubberUI();
        });
        previewVideoElement.addEventListener("seeked", () => {
            updatePreviewSubtitle();
            syncTimelinePlayhead();
            syncDubbingAudioSeek();
            updateScrubberUI();
        });
        previewVideoElement.addEventListener("loadedmetadata", () => {
            syncPreviewVideoVolume();
            applySubStylingToUI();
            updatePreviewSubtitle();
            renderTimeline();
            loadPreviewDubbedAudio();
            updateScrubberUI();
        });
        previewVideoElement.addEventListener("play", () => {
            syncPreviewVideoVolume();
            syncTimelinePlayhead();
            playDubbingAudio();
            updateScrubberUI();
        });
        previewVideoElement.addEventListener("pause", () => {
            syncTimelinePlayhead();
            pauseDubbingAudio();
            updateScrubberUI();
        });
        previewVideoElement.addEventListener("ended", () => {
            syncTimelinePlayhead();
            pauseDubbingAudio();
            if (dubbingAudio) dubbingAudio.currentTime = 0;
            updateScrubberUI();
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
        // Đã vô hiệu hóa để giải phóng hơn 10.000 phần tử DOM, triệt tiêu hoàn toàn giật lag
        return;
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
                translation: "",
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

    // Keyboard Shortcuts (Space: Play/Pause, S/C: Split, Delete: Delete, ArrowLeft/Right: Seek 5s)
    document.addEventListener("keydown", (e) => {
        const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : "";
        if (tag === "input" || tag === "textarea" || tag === "select") return;

        if (e.code === "Space") {
            e.preventDefault();
            if (previewVideoElement) {
                if (previewVideoElement.paused) previewVideoElement.play();
                else previewVideoElement.pause();
            }
        } else if (e.code === "ArrowLeft") {
            e.preventDefault();
            if (previewVideoElement) {
                previewVideoElement.currentTime = Math.max(0, (previewVideoElement.currentTime || 0) - 5);
                updateScrubberUI(previewVideoElement.currentTime, getTimelineTotalDuration());
                updatePreviewSubtitle();
                syncDubbingAudioSeek();
            }
        } else if (e.code === "ArrowRight") {
            e.preventDefault();
            if (previewVideoElement) {
                const totalDur = getTimelineTotalDuration();
                previewVideoElement.currentTime = Math.min(totalDur, (previewVideoElement.currentTime || 0) + 5);
                updateScrubberUI(previewVideoElement.currentTime, totalDur);
                updatePreviewSubtitle();
                syncDubbingAudioSeek();
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

            setTerminalVisible(true);
            if (step1TerminalStatusTag) {
                step1TerminalStatusTag.className = "terminal-status-tag";
                step1TerminalStatusTag.textContent = "Đang quét OCR";
            }
            appendTerminalLog(`[${new Date().toTimeString().slice(0, 8)}] [INFO] Bắt đầu quét phụ đề (${currentTranscribeMode.toUpperCase()})...`);

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

                        if (statusData.logs && Array.isArray(statusData.logs)) {
                            updateTerminalLogs(statusData.logs);
                        }

                        if (statusData.status === "transcribed") {
                            clearInterval(pollingInterval);
                            btnStep2Transcribe.disabled = false;
                            if (step2ProgressBox) step2ProgressBox.classList.add("d-none");

                            if (step1TerminalStatusTag) {
                                step1TerminalStatusTag.className = "terminal-status-tag status-done";
                                step1TerminalStatusTag.textContent = "Hoàn tất";
                            }
                            renderSegmentsTable(statusData.segments || []);

                            // Hiển thị hộp kết quả quét và số câu
                            const step2ResultBox = document.getElementById("step2-result-box");
                            const step2ScannedCount = document.getElementById("step2-scanned-count");
                            if (step2ResultBox) step2ResultBox.classList.remove("d-none");
                            if (step2ScannedCount) step2ScannedCount.textContent = (statusData.segments || []).length;

                            currentProjectMeta = statusData.project || currentProjectMeta;
                            setSaveStatus("saved", "Đã quét phụ đề gốc thành công");
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

        // Khi bật lồng tiếng, video gốc đóng vai trò nhạc nền nhẹ (mặc định 10% theo yêu cầu người dùng)
        let vol = 0.10;
        if (bgVolumeSlider) {
            vol = parseFloat(bgVolumeSlider.value);
        } else if (sharedBgVol) {
            vol = parseFloat(sharedBgVol.value);
        }
        if (isNaN(vol)) vol = 0.10;
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
                logo_box: {
                    enabled: Boolean(logoBoxCoords.enabled),
                    x: Number(logoBoxCoords.x),
                    y: Number(logoBoxCoords.y),
                    w: Number(logoBoxCoords.w),
                    h: Number(logoBoxCoords.h),
                    opacity: Number(logoBoxCoords.opacity),
                    keep_aspect: true,
                    filename: logoBoxCoords.filename || null,
                    image_path: logoBoxCoords.image_path || null
                },
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

                    if (statusData.logs) updateTerminalLogs(statusData.logs);
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

            setTerminalVisible(true);
            if (step1TerminalStatusTag) {
                step1TerminalStatusTag.className = "terminal-status-tag";
                step1TerminalStatusTag.textContent = "Đang xuất video";
            }
            appendTerminalLog(`[${new Date().toTimeString().slice(0, 8)}] [INFO] Bắt đầu kết xuất video (TTS & Hardsub)...`);

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
                        logo_box: {
                            enabled: Boolean(logoBoxCoords.enabled),
                            x: Number(logoBoxCoords.x),
                            y: Number(logoBoxCoords.y),
                            w: Number(logoBoxCoords.w),
                            h: Number(logoBoxCoords.h),
                            opacity: Number(logoBoxCoords.opacity),
                            keep_aspect: true,
                            filename: logoBoxCoords.filename || null,
                            image_path: logoBoxCoords.image_path || null
                        },
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

                        if (statusData.logs) updateTerminalLogs(statusData.logs);
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
                            markStepDone(5);

                            currentProjectMeta = statusData.project || currentProjectMeta;
                            setSaveStatus("saved", "Đã xuất video hoàn tất!");
                            showState("success");

                            // Hiển thị hộp tải video hoàn thiện ở Bước 5
                            const step3SuccessBox = document.getElementById("step3-success-box");
                            if (step3SuccessBox) {
                                step3SuccessBox.classList.remove("d-none");
                            }
                            const btnStep3RenderDownload = document.getElementById("btn-step3-render-download");
                            if (btnStep3RenderDownload) {
                                btnStep3RenderDownload.href = statusData.download_url || `/api/project/${currentProjectId}/download`;
                            }
                            const btnStep3DownloadAudio = document.getElementById("btn-step3-download-audio");
                            if (btnStep3DownloadAudio) {
                                btnStep3DownloadAudio.href = `/api/project/${currentProjectId}/download-audio`;
                            }

                            if (videoPreview) {
                                const rawUrl = statusData.video_url || `/api/project/${currentProjectId}/video-dubbed`;
                                videoPreview.src = rawUrl + (rawUrl.includes("?") ? "&" : "?") + `t=${Date.now()}`;
                                videoPreview.load();
                            }
                            if (downloadBtn) downloadBtn.href = statusData.download_url || `/api/project/${currentProjectId}/download`;
                            if (downloadSrtBtn) downloadSrtBtn.href = statusData.subtitles_url || `/api/project/${currentProjectId}/subtitles`;

                            if (step1TerminalStatusTag) {
                                step1TerminalStatusTag.className = "terminal-status-tag tag-success";
                                step1TerminalStatusTag.textContent = "Hoàn tất";
                            }

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
                            const errMsg = statusData.error || statusData.message || "Xuất video thất bại.";
                            if (errorMessage) errorMessage.textContent = errMsg;
                            if (step4ProgressMsg) {
                                step4ProgressMsg.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i> ${escapeHtml(errMsg)}`;
                            }
                            if (step1TerminalStatusTag) {
                                step1TerminalStatusTag.className = "terminal-status-tag tag-error";
                                step1TerminalStatusTag.textContent = "Lỗi xuất video";
                            }
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
                setSaveStatus("saved", `Đã gắn ${data.count || 0} câu từ SRT! Hãy bấm "Tạo giọng đọc" để tạo lại âm thanh.`);
                // Old voice files were deleted server-side; drop the cached preview track in the browser too
                pauseDubbingAudio();
                dubbingAudio.removeAttribute("src");
                dubbingAudio.load();
                isDubbingAudioLoaded = false;
                isDubbingAudioLoading = false;
            } catch (err) {
                alert("Lỗi khi gắn SRT: " + err.message);
            } finally {
                btnApplySrtImport.disabled = false;
                btnApplySrtImport.innerHTML = origHTML;
            }
        });
    }

    // ==========================================
    // SPA ROUTER & HOME HUB CONTROLLER (SIÊU TOOL CỦA NGATCT)
    // ==========================================
    const homeView = document.getElementById("home-view");
    const storyTtsView = document.getElementById("story-tts-view");
    const socialVideoView = document.getElementById("social-video-view");
    const btnNavHome = document.getElementById("btn-nav-home");
    const btnNavDubber = document.getElementById("btn-nav-dubber");
    const btnNavStoryTts = document.getElementById("btn-nav-story-tts");
    const btnNavSocialVideo = document.getElementById("btn-nav-social-video");
    const btnNavSettings = document.getElementById("btn-nav-settings");
    const btnBackToHome = document.getElementById("btn-back-to-home");
    const btnStoryBackHome = document.getElementById("btn-story-back-home");
    const btnSocialBackHome = document.getElementById("btn-social-back-home");
    const headerLogo = document.getElementById("header-logo");

    const btnHomeOpenDubber = document.getElementById("btn-home-open-dubber");
    const btnHomeNewDubber = document.getElementById("btn-home-new-dubber");
    const btnHomeOpenStoryTts = document.getElementById("btn-home-open-story-tts");
    const btnHomeOpenSocialVideo = document.getElementById("btn-home-open-social-video");
    const btnHomeCreateProject = document.getElementById("btn-home-create-project");
    const btnHomeEmptyCreate = document.getElementById("btn-home-empty-create");
    const btnHomeRefreshProjects = document.getElementById("btn-home-refresh-projects");
    const btnHomeQuickSettings = document.getElementById("btn-home-quick-settings");

    const modalApiSettings = document.getElementById("modal-api-settings");
    const btnCloseApiSettingsModal = document.getElementById("btn-close-api-settings-modal");
    const btnCancelApiSettingsModal = document.getElementById("btn-cancel-api-settings-modal");
    const modalSelectEngine = document.getElementById("modal-select-translation-engine");
    const modalInputGroqKey = document.getElementById("modal-input-groq-key");
    const modalInputGeminiKey = document.getElementById("modal-input-gemini-key");
    const modalGroqWrap = document.getElementById("modal-groq-key-wrap");
    const modalGeminiWrap = document.getElementById("modal-gemini-key-wrap");
    const btnModalSaveGroqKey = document.getElementById("btn-modal-save-groq-key");
    const btnModalSaveGeminiKey = document.getElementById("btn-modal-save-gemini-key");

    function switchView(viewName, updateHash = true) {
        if (viewName === "dubber") {
            if (homeView) homeView.classList.add("d-none");
            if (storyTtsView) storyTtsView.classList.add("d-none");
            if (socialVideoView) socialVideoView.classList.add("d-none");
            if (workspaceLayout) workspaceLayout.classList.remove("d-none");
            if (btnNavDubber) btnNavDubber.classList.add("active");
            if (btnNavHome) btnNavHome.classList.remove("active");
            if (btnNavStoryTts) btnNavStoryTts.classList.remove("active");
            if (btnNavSocialVideo) btnNavSocialVideo.classList.remove("active");
            if (updateHash) {
                history.pushState(null, "", "#dubber");
            }
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else if (viewName === "story-tts") {
            if (homeView) homeView.classList.add("d-none");
            if (workspaceLayout) workspaceLayout.classList.add("d-none");
            if (socialVideoView) socialVideoView.classList.add("d-none");
            if (storyTtsView) storyTtsView.classList.remove("d-none");
            if (btnNavStoryTts) btnNavStoryTts.classList.add("active");
            if (btnNavHome) btnNavHome.classList.remove("active");
            if (btnNavDubber) btnNavDubber.classList.remove("active");
            if (btnNavSocialVideo) btnNavSocialVideo.classList.remove("active");
            if (updateHash) {
                history.pushState(null, "", "#story-tts");
            }
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else if (viewName === "social-video") {
            if (homeView) homeView.classList.add("d-none");
            if (workspaceLayout) workspaceLayout.classList.add("d-none");
            if (storyTtsView) storyTtsView.classList.add("d-none");
            if (socialVideoView) socialVideoView.classList.remove("d-none");
            if (btnNavSocialVideo) btnNavSocialVideo.classList.add("active");
            if (btnNavHome) btnNavHome.classList.remove("active");
            if (btnNavDubber) btnNavDubber.classList.remove("active");
            if (btnNavStoryTts) btnNavStoryTts.classList.remove("active");
            if (updateHash) {
                history.pushState(null, "", "#social-video");
            }
            loadSocialBackgrounds();
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else {
            // Default to 'home'
            if (workspaceLayout) workspaceLayout.classList.add("d-none");
            if (storyTtsView) storyTtsView.classList.add("d-none");
            if (socialVideoView) socialVideoView.classList.add("d-none");
            if (homeView) homeView.classList.remove("d-none");
            if (btnNavHome) btnNavHome.classList.add("active");
            if (btnNavDubber) btnNavDubber.classList.remove("active");
            if (btnNavStoryTts) btnNavStoryTts.classList.remove("active");
            if (btnNavSocialVideo) btnNavSocialVideo.classList.remove("active");
            if (updateHash) {
                history.pushState(null, "", "#home");
            }
            loadHomeRecentProjects();
            updateHomeEngineStatus();
            window.scrollTo({ top: 0, behavior: "smooth" });
        }
    }

    async function updateHomeEngineStatus() {
        const homeEngineLabel = document.getElementById("home-engine-label");
        const statusChip = document.getElementById("home-status-engine");
        if (!homeEngineLabel) return;

        try {
            const res = await fetch("/api/settings");
            if (!res.ok) throw new Error("API settings error");
            const s = await res.json();
            const engine = s.translation_engine || "groq";

            const pulseEl = statusChip ? statusChip.querySelector(".dot-pulse") : null;

            if (engine === "groq") {
                if (s.has_groq_key) {
                    homeEngineLabel.textContent = `Groq AI (${s.groq_model || 'llama-3.3-70b-versatile'}) • Sẵn sàng`;
                    if (pulseEl) pulseEl.className = "dot-pulse";
                } else {
                    homeEngineLabel.textContent = "Groq AI • Chưa nạp API Key";
                    if (pulseEl) pulseEl.className = "dot-pulse warn";
                }
            } else if (engine === "gemini") {
                if (s.has_gemini_key) {
                    homeEngineLabel.textContent = `Gemini AI (${s.gemini_model || 'gemini-3.5-flash'}) • Sẵn sàng`;
                    if (pulseEl) pulseEl.className = "dot-pulse";
                } else {
                    homeEngineLabel.textContent = "Gemini AI • Chưa nạp API Key";
                    if (pulseEl) pulseEl.className = "dot-pulse warn";
                }
            } else {
                homeEngineLabel.textContent = "Google Dịch • Sẵn sàng (Dịch máy cơ bản)";
                if (pulseEl) pulseEl.className = "dot-pulse";
            }
        } catch (e) {
            console.warn("Could not update home engine status:", e);
        }
    }

    async function loadHomeRecentProjects() {
        const listContainer = document.getElementById("home-recent-projects-list");
        const emptyContainer = document.getElementById("home-projects-empty");
        if (!listContainer) return;

        try {
            listContainer.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: #94a3b8;"><i class="fa-solid fa-spinner fa-spin"></i> Đang tải danh sách dự án gần đây...</div>`;
            const res = await fetch("/api/projects");
            if (!res.ok) throw new Error("Không thể tải danh sách dự án.");
            const projects = await res.json();

            if (!projects || projects.length === 0) {
                listContainer.innerHTML = "";
                if (emptyContainer) emptyContainer.classList.remove("d-none");
                return;
            }

            if (emptyContainer) emptyContainer.classList.add("d-none");
            listContainer.innerHTML = "";

            projects.slice(0, 12).forEach(p => {
                const card = document.createElement("div");
                card.className = "home-project-card";
                card.dataset.id = p.id;

                const stepName = STEP_NAMES[p.current_step] || `Bước ${p.current_step || 1}`;
                const title = escapeHtml(p.name || "Dự án không tên");
                const timeStr = p.updated_at ? new Date(p.updated_at).toLocaleString("vi-VN", { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : "Mới đây";

                card.innerHTML = `
                    <div class="home-project-top">
                        <div class="home-project-icon-title">
                            <div class="home-project-icon">
                                <i class="fa-solid fa-film"></i>
                            </div>
                            <div style="min-width: 0;">
                                <div class="home-project-title" title="${title}">${title}</div>
                                <div class="home-project-meta">
                                    <span><i class="fa-regular fa-clock"></i> ${timeStr}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="home-project-bottom">
                        <span class="home-project-step-pill"><i class="fa-solid fa-list-check"></i> ${stepName}</span>
                        <div class="home-project-btns">
                            <button type="button" class="primary-btn btn-sm btn-accent btn-home-open-proj" title="Mở dự án này">
                                <i class="fa-solid fa-arrow-right"></i> Tiếp Tục
                            </button>
                            <button type="button" class="btn-icon-subtle text-danger btn-home-del-proj" title="Xóa dự án">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </div>
                `;

                // Handle click on card or open button
                const btnOpen = card.querySelector(".btn-home-open-proj");
                const openHandler = async (e) => {
                    e.stopPropagation();
                    await openProject(p.id, false);
                    switchView("dubber");
                };
                card.addEventListener("click", openHandler);
                if (btnOpen) btnOpen.addEventListener("click", openHandler);

                // Handle delete button
                const btnDel = card.querySelector(".btn-home-del-proj");
                if (btnDel) {
                    btnDel.addEventListener("click", async (e) => {
                        e.stopPropagation();
                        const ok = await showConfirmDialog(
                            "Xóa Dự Án Này?",
                            `Bạn có chắc chắn muốn xóa vĩnh viễn dự án "${title}" không? Thao tác này không thể hoàn tác.`,
                            true
                        );
                        if (!ok) return;

                        try {
                            const delRes = await fetch(`/api/projects/${p.id}`, { method: "DELETE" });
                            if (delRes.ok) {
                                if (currentProjectId === p.id) {
                                    await createNewProject(false);
                                }
                                await loadHomeRecentProjects();
                                if (typeof fetchProjectsList === "function") {
                                    fetchProjectsList("");
                                }
                            } else {
                                alert("Không thể xóa dự án.");
                            }
                        } catch (err) {
                            console.error(err);
                            alert("Lỗi khi xóa dự án: " + err.message);
                        }
                    });
                }

                listContainer.appendChild(card);
            });
        } catch (e) {
            console.error("Home projects error", e);
            if (listContainer) {
                listContainer.innerHTML = `<div style="grid-column: 1/-1; color: #f87171; text-align: center; padding: 1.5rem;">Lỗi nạp danh sách dự án: ${e.message}</div>`;
            }
        }
    }

    // Modal API Settings Handlers
    function openApiSettingsModal() {
        if (!modalApiSettings) return;
        modalApiSettings.classList.remove("d-none");
        loadModalApiSettings();
    }

    function closeApiSettingsModal() {
        if (modalApiSettings) modalApiSettings.classList.add("d-none");
    }

    async function loadModalApiSettings() {
        try {
            const res = await fetch("/api/settings");
            if (!res.ok) return;
            const s = await res.json();
            if (modalSelectEngine) {
                modalSelectEngine.value = s.translation_engine || "groq";
                toggleModalKeyFields(modalSelectEngine.value);
            }
            if (modalInputGroqKey) modalInputGroqKey.placeholder = s.groq_api_key_masked || "gsk_... hoặc dán key mới";
            if (modalInputGeminiKey) modalInputGeminiKey.placeholder = s.gemini_api_key_masked || "AIzaSy... hoặc dán key mới";
        } catch (e) {
            console.warn(e);
        }
    }

    function toggleModalKeyFields(engine) {
        if (modalGroqWrap) modalGroqWrap.classList.toggle("d-none", engine !== "groq");
        if (modalGeminiWrap) modalGeminiWrap.classList.toggle("d-none", engine !== "gemini");
    }

    if (modalSelectEngine) {
        modalSelectEngine.addEventListener("change", async (e) => {
            const val = e.target.value;
            toggleModalKeyFields(val);
            try {
                await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ translation_engine: val })
                });
                await loadAppSettings();
                updateHomeEngineStatus();
            } catch (err) {
                console.warn(err);
            }
        });
    }

    if (btnModalSaveGroqKey && modalInputGroqKey) {
        btnModalSaveGroqKey.addEventListener("click", async () => {
            const rawKey = modalInputGroqKey.value.trim();
            if (!rawKey) return;
            try {
                const res = await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        translation_engine: "groq",
                        groq_api_key: rawKey
                    })
                });
                if (res.ok) {
                    alert("Đã lưu Groq API Key thành công!");
                    modalInputGroqKey.value = "";
                    await loadAppSettings();
                    await loadModalApiSettings();
                    updateHomeEngineStatus();
                }
            } catch (err) {
                alert("Lỗi khi lưu Groq API Key: " + err.message);
            }
        });
    }

    if (btnModalSaveGeminiKey && modalInputGeminiKey) {
        btnModalSaveGeminiKey.addEventListener("click", async () => {
            const rawKey = modalInputGeminiKey.value.trim();
            if (!rawKey) return;
            try {
                const res = await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        translation_engine: "gemini",
                        gemini_api_key: rawKey
                    })
                });
                if (res.ok) {
                    alert("Đã lưu Gemini API Key thành công!");
                    modalInputGeminiKey.value = "";
                    await loadAppSettings();
                    await loadModalApiSettings();
                    updateHomeEngineStatus();
                }
            } catch (err) {
                alert("Lỗi khi lưu Gemini API Key: " + err.message);
            }
        });
    }

    if (btnNavHome) btnNavHome.addEventListener("click", () => switchView("home"));
    if (btnNavDubber) btnNavDubber.addEventListener("click", () => switchView("dubber"));
    if (btnNavSettings) btnNavSettings.addEventListener("click", openApiSettingsModal);
    if (btnHomeQuickSettings) btnHomeQuickSettings.addEventListener("click", openApiSettingsModal);
    if (btnCloseApiSettingsModal) btnCloseApiSettingsModal.addEventListener("click", closeApiSettingsModal);
    if (btnCancelApiSettingsModal) btnCancelApiSettingsModal.addEventListener("click", closeApiSettingsModal);
    if (modalApiSettings) {
        modalApiSettings.addEventListener("click", (e) => {
            if (e.target === modalApiSettings) closeApiSettingsModal();
        });
    }

    if (headerLogo) headerLogo.addEventListener("click", () => switchView("home"));
    if (btnBackToHome) btnBackToHome.addEventListener("click", () => switchView("home"));
    if (btnStoryBackHome) btnStoryBackHome.addEventListener("click", () => switchView("home"));

    if (btnNavHome) btnNavHome.addEventListener("click", () => switchView("home"));
    if (btnNavDubber) btnNavDubber.addEventListener("click", () => switchView("dubber"));
    if (btnNavStoryTts) btnNavStoryTts.addEventListener("click", () => switchView("story-tts"));

    if (btnHomeOpenDubber) btnHomeOpenDubber.addEventListener("click", () => switchView("dubber"));
    if (btnHomeOpenStoryTts) btnHomeOpenStoryTts.addEventListener("click", () => switchView("story-tts"));
    if (btnHomeNewDubber) {
        btnHomeNewDubber.addEventListener("click", async () => {
            await createNewProject(true);
            switchView("dubber");
        });
    }
    if (btnHomeCreateProject) {
        btnHomeCreateProject.addEventListener("click", async () => {
            await createNewProject(true);
            switchView("dubber");
        });
    }
    if (btnHomeEmptyCreate) {
        btnHomeEmptyCreate.addEventListener("click", async () => {
            await createNewProject(true);
            switchView("dubber");
        });
    }
    if (btnHomeRefreshProjects) btnHomeRefreshProjects.addEventListener("click", loadHomeRecentProjects);
    if (btnNavSocialVideo) btnNavSocialVideo.addEventListener("click", () => switchView("social-video"));
    if (btnHomeOpenSocialVideo) btnHomeOpenSocialVideo.addEventListener("click", () => switchView("social-video"));
    if (btnSocialBackHome) btnSocialBackHome.addEventListener("click", () => switchView("home"));

    const cardFeatureSocialVideo = document.getElementById("card-feature-social-video");
    if (cardFeatureSocialVideo) cardFeatureSocialVideo.addEventListener("click", () => switchView("social-video"));

    const cardFeatureStoryTts = document.getElementById("card-feature-story-tts");
    if (cardFeatureStoryTts) cardFeatureStoryTts.addEventListener("click", () => switchView("story-tts"));

    const cardFeatureDubber = document.getElementById("card-feature-dubber");
    if (cardFeatureDubber) cardFeatureDubber.addEventListener("click", () => switchView("dubber"));

    // Browser navigation back/forward support
    window.addEventListener("popstate", () => {
        if (window.location.hash === "#social-video") {
            switchView("social-video", false);
        } else if (window.location.hash === "#story-tts") {
            switchView("story-tts", false);
        } else if (window.location.hash === "#dubber") {
            switchView("dubber", false);
        } else {
            switchView("home", false);
        }
    });

    // ==========================================
    // STORY TTS STUDIO CONTROLLER
    // ==========================================
    function initStoryTtsStudio() {
        const tabSourceText = document.getElementById("tab-source-text");
        const tabSourceYt = document.getElementById("tab-source-yt");
        const boxSourceYt = document.getElementById("box-source-yt");
        const inputYtUrl = document.getElementById("input-yt-url");
        const btnExtractYt = document.getElementById("btn-extract-yt");
        const ytExtractStatus = document.getElementById("yt-extract-status");
        const ytExtractStatusText = document.getElementById("yt-extract-status-text");

        const storyRawText = document.getElementById("story-raw-text");
        const storyCharCount = document.getElementById("story-char-count");
        const storyWordCount = document.getElementById("story-word-count");
        const storyEstDuration = document.getElementById("story-est-duration");

        const storyRewriteStyle = document.getElementById("story-rewrite-style");
        const storyRewriteInstruction = document.getElementById("story-rewrite-instruction");
        const btnStoryAiRewrite = document.getElementById("btn-story-ai-rewrite");
        const storyRewriteStatus = document.getElementById("story-rewrite-status");
        const storyRewriteStatusText = document.getElementById("story-rewrite-status-text");

        const storyVoiceSelect = document.getElementById("story-voice-select");
        const btnStoryPreviewVoice = document.getElementById("btn-story-preview-voice");
        const storyPauseSlider = document.getElementById("story-pause-slider");
        const storyPauseVal = document.getElementById("story-pause-val");

        const btnStoryGenerateAudio = document.getElementById("btn-story-generate-audio");
        const storyProgressBox = document.getElementById("story-progress-box");
        const storyProgressText = document.getElementById("story-progress-text");
        const storyResultBox = document.getElementById("story-result-box");
        const resultStatSentences = document.getElementById("result-stat-sentences");
        const resultStatDuration = document.getElementById("result-stat-duration");
        const resultStatVoice = document.getElementById("result-stat-voice");
        const storyAudioPlayer = document.getElementById("story-audio-player");
        const btnStoryDownloadMp3 = document.getElementById("btn-story-download-mp3");
        const btnStoryDownloadSrt = document.getElementById("btn-story-download-srt");
        const btnStoryClearAll = document.getElementById("btn-story-clear-all");

        if (!storyRawText) return;

        // Source Tab Switching
        if (tabSourceText && tabSourceYt && boxSourceYt) {
            tabSourceText.addEventListener("click", () => {
                tabSourceText.classList.add("active");
                tabSourceYt.classList.remove("active");
                boxSourceYt.classList.add("d-none");
            });
            tabSourceYt.addEventListener("click", () => {
                tabSourceYt.classList.add("active");
                tabSourceText.classList.remove("active");
                boxSourceYt.classList.remove("d-none");
            });
        }

        // Stats Counter
        function updateStoryStats() {
            const text = storyRawText.value || "";
            const chars = text.length;
            const words = text.trim() ? text.trim().split(/\s+/).length : 0;
            const minutes = Math.ceil(words / 150);

            if (storyCharCount) storyCharCount.textContent = `${chars.toLocaleString()} ký tự`;
            if (storyWordCount) storyWordCount.textContent = `${words.toLocaleString()} từ`;
            if (storyEstDuration) storyEstDuration.textContent = `~${minutes} phút đọc`;
        }
        storyRawText.addEventListener("input", updateStoryStats);

        // Pause Slider
        if (storyPauseSlider && storyPauseVal) {
            storyPauseSlider.addEventListener("input", () => {
                storyPauseVal.textContent = `${storyPauseSlider.value} ms`;
            });
        }

        // YouTube Extraction
        if (btnExtractYt && inputYtUrl) {
            btnExtractYt.addEventListener("click", async () => {
                const url = inputYtUrl.value.trim();
                if (!url) {
                    showToast("Vui lòng nhập link video YouTube", "warning");
                    return;
                }
                btnExtractYt.disabled = true;
                if (ytExtractStatus) {
                    ytExtractStatus.classList.remove("d-none");
                    if (ytExtractStatusText) ytExtractStatusText.textContent = "Đang kết nối YouTube & trích xuất phụ đề...";
                }

                try {
                    const res = await fetch("/api/story-tts/extract-youtube", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ url })
                    });
                    const data = await res.json();
                    if (!res.ok || data.status !== "ok") {
                        throw new Error(data.message || "Lỗi khi trích xuất YouTube.");
                    }

                    if (data.transcript) {
                        storyRawText.value = data.transcript;
                        updateStoryStats();
                        showToast(`Đã lấy phụ đề từ video: "${data.title}"`, "success");
                    } else {
                        showToast(data.message || "Không tìm thấy phụ đề cho video này.", "warning");
                    }
                } catch (e) {
                    showToast(e.message || "Không thể bóc tách từ YouTube.", "error");
                } finally {
                    btnExtractYt.disabled = false;
                    if (ytExtractStatus) ytExtractStatus.classList.add("d-none");
                }
            });
        }

        // AI Rewriter
        if (btnStoryAiRewrite) {
            btnStoryAiRewrite.addEventListener("click", async () => {
                const text = storyRawText.value.trim();
                if (!text) {
                    showToast("Vui lòng nhập hoặc dán nội dung kịch bản trước khi xào nấu.", "warning");
                    return;
                }

                const style = storyRewriteStyle ? storyRewriteStyle.value : "storytelling";
                const custom_instruction = storyRewriteInstruction ? storyRewriteInstruction.value.trim() : "";

                btnStoryAiRewrite.disabled = true;
                if (storyRewriteStatus) {
                    storyRewriteStatus.classList.remove("d-none");
                    if (storyRewriteStatusText) storyRewriteStatusText.textContent = "AI đang xào nấu kịch bản, lọc bỏ rác video và viết lại...";
                }

                try {
                    const res = await fetch("/api/story-tts/rewrite", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text, style, custom_instruction })
                    });
                    const data = await res.json();
                    if (!res.ok || data.status !== "ok") {
                        throw new Error(data.message || "Lỗi khi xào nấu kịch bản.");
                    }

                    storyRawText.value = data.rewritten_text;
                    updateStoryStats();
                    showToast(`Đã xào nấu kịch bản thành công bằng ${data.engine}!`, "success");
                } catch (e) {
                    showToast(e.message || "Không thể xào nấu kịch bản.", "error");
                } finally {
                    btnStoryAiRewrite.disabled = false;
                    if (storyRewriteStatus) storyRewriteStatus.classList.add("d-none");
                }
            });
        }

        // Voice Preview
        let storyAudioPreviewObj = null;
        if (btnStoryPreviewVoice && storyVoiceSelect) {
            btnStoryPreviewVoice.addEventListener("click", async () => {
                if (storyAudioPreviewObj && !storyAudioPreviewObj.paused) {
                    storyAudioPreviewObj.pause();
                    storyAudioPreviewObj = null;
                    btnStoryPreviewVoice.innerHTML = '<i class="fa-solid fa-volume-high"></i> Nghe Thử';
                    return;
                }
                const voiceKey = storyVoiceSelect.value;
                const sampleText = "Xin chào, đây là giọng đọc thử nghiệm kịch bản của Siêu Tool.";
                btnStoryPreviewVoice.disabled = true;
                btnStoryPreviewVoice.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tải...';
                try {
                    const res = await fetch("/api/tts-preview", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text: sampleText, voice: voiceKey })
                    });
                    if (!res.ok) throw new Error("Không thể tạo giọng mẫu.");
                    const blob = await res.blob();
                    const audioUrl = URL.createObjectURL(blob);
                    storyAudioPreviewObj = new Audio(audioUrl);
                    storyAudioPreviewObj.onended = () => {
                        btnStoryPreviewVoice.innerHTML = '<i class="fa-solid fa-volume-high"></i> Nghe Thử';
                    };
                    storyAudioPreviewObj.play();
                    btnStoryPreviewVoice.innerHTML = '<i class="fa-solid fa-stop"></i> Dừng';
                } catch (e) {
                    showToast("Lỗi khi nghe thử giọng: " + e.message, "warning");
                    btnStoryPreviewVoice.innerHTML = '<i class="fa-solid fa-volume-high"></i> Nghe Thử';
                } finally {
                    btnStoryPreviewVoice.disabled = false;
                }
            });
        }

        // Synthesize Full Story Audio (MP3 + SRT)
        if (btnStoryGenerateAudio) {
            btnStoryGenerateAudio.addEventListener("click", async () => {
                const text = storyRawText.value.trim();
                if (!text) {
                    showToast("Vui lòng nhập nội dung kịch bản để tạo audio.", "warning");
                    return;
                }

                const voice = storyVoiceSelect ? storyVoiceSelect.value : "capcut_cogaithoatngon";
                const pause_ms = storyPauseSlider ? parseInt(storyPauseSlider.value, 10) : 350;

                btnStoryGenerateAudio.disabled = true;
                if (storyProgressBox) storyProgressBox.classList.remove("d-none");
                if (storyResultBox) storyResultBox.classList.add("d-none");
                if (storyProgressText) storyProgressText.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang phân tích câu, sinh giọng đọc TikTok và ghép nối...';

                try {
                    const res = await fetch("/api/story-tts/synthesize", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text, voice, pause_ms })
                    });
                    const data = await res.json();
                    if (!res.ok || data.status !== "ok") {
                        throw new Error(data.message || "Lỗi tạo audio kịch bản.");
                    }

                    // Render Result
                    if (storyResultBox) storyResultBox.classList.remove("d-none");
                    if (resultStatSentences) resultStatSentences.innerHTML = `<i class="fa-solid fa-list-ol"></i> ${data.total_sentences} câu`;
                    
                    const totalSec = Math.round(data.total_duration_sec);
                    const durMins = Math.floor(totalSec / 60);
                    const durSecs = totalSec % 60;
                    const durStr = `${durMins}:${durSecs.toString().padStart(2, '0')}`;
                    if (resultStatDuration) resultStatDuration.innerHTML = `<i class="fa-solid fa-clock"></i> ${durStr}`;
                    if (resultStatVoice) resultStatVoice.innerHTML = `<i class="fa-brands fa-tiktok"></i> ${data.voice_name || voice}`;

                    const audioDownloadUrl = `/api/story-tts/download/${data.task_id}/audio`;
                    const srtDownloadUrl = `/api/story-tts/download/${data.task_id}/srt`;

                    if (storyAudioPlayer) {
                        storyAudioPlayer.src = audioDownloadUrl;
                        storyAudioPlayer.load();
                    }
                    if (btnStoryDownloadMp3) btnStoryDownloadMp3.href = audioDownloadUrl;
                    if (btnStoryDownloadSrt) btnStoryDownloadSrt.href = srtDownloadUrl;

                    showToast("🎉 Đã tạo hoàn tất bản thu âm và phụ đề SRT!", "success");
                } catch (e) {
                    showToast(e.message || "Không thể tạo bản thu âm.", "error");
                } finally {
                    btnStoryGenerateAudio.disabled = false;
                    if (storyProgressBox) storyProgressBox.classList.add("d-none");
                }
            });
        }

        // Clear All
        if (btnStoryClearAll) {
            btnStoryClearAll.addEventListener("click", () => {
                storyRawText.value = "";
                updateStoryStats();
                if (storyResultBox) storyResultBox.classList.add("d-none");
                if (inputYtUrl) inputYtUrl.value = "";
                showToast("Đã xóa trắng nội dung kịch bản.", "info");
            });
        }
    }

    initStoryTtsStudio();

    // ==========================================
    // SOCIAL VIDEO STUDIO CONTROLLER (THREADS & FACEBOOK)
    // ==========================================
    async function loadSocialBackgrounds() {
        const sel = document.getElementById("social-select-bg-video");
        if (!sel) return;
        try {
            const res = await fetch("/api/social/backgrounds");
            if (res.ok) {
                const data = await res.json();
                const currentVal = sel.value;
                sel.innerHTML = '<option value="">-- Mặc định: Nền Tối Gradient Chuyển Động --</option>';
                if (data.backgrounds && data.backgrounds.length > 0) {
                    data.backgrounds.forEach(bg => {
                        const opt = document.createElement("option");
                        opt.value = bg;
                        opt.textContent = `🎬 ${bg}`;
                        sel.appendChild(opt);
                    });
                }
                if (currentVal) sel.value = currentVal;
            }
        } catch (e) {
            console.warn("Could not load backgrounds:", e);
        }
    }

    function initSocialVideoController() {
        const inputUrl = document.getElementById("social-input-url");
        const inputCookie = document.getElementById("social-input-cookie");
        const platformIcon = document.getElementById("social-platform-icon");
        const platformBadge = document.getElementById("social-platform-badge");
        const btnFetch = document.getElementById("btn-social-fetch");
        const btnQuickRender = document.getElementById("btn-social-quick-render");
        const selectPlatform = document.getElementById("social-post-platform");
        const authorName = document.getElementById("social-author-name");
        const authorHandle = document.getElementById("social-author-handle");
        const postContent = document.getElementById("social-post-content");
        const postVoice = document.getElementById("social-post-voice");
        const postLikes = document.getElementById("social-post-likes");
        const postReplies = document.getElementById("social-post-replies");
        const commentsContainer = document.getElementById("social-comments-container");
        const btnAddComment = document.getElementById("btn-social-add-comment");
        const selectBgVideo = document.getElementById("social-select-bg-video");
        const themeDark = document.getElementById("social-theme-dark");
        const btnBuildVideo = document.getElementById("btn-social-build-video");

        const btnModeQuick = document.getElementById("btn-mode-quick");
        const btnModeStep = document.getElementById("btn-mode-step");
        const editorSection = document.getElementById("social-editor-section");

        const resultSection = document.getElementById("social-result-section");
        const progressWrap = document.getElementById("social-progress-wrap");
        const progressMsg = document.getElementById("social-progress-msg");
        const progressPercent = document.getElementById("social-progress-percent");
        const progressBar = document.getElementById("social-progress-bar");
        const videoPreviewWrap = document.getElementById("social-video-preview-wrap");
        const resultVideo = document.getElementById("social-result-video");
        const btnDownloadVideo = document.getElementById("btn-social-download-video");

        let currentActiveMode = "quick"; // "quick" or "step"

        // Mode Switching
        if (btnModeQuick && btnModeStep) {
            btnModeQuick.addEventListener("click", () => {
                currentActiveMode = "quick";
                btnModeQuick.classList.add("active");
                btnModeStep.classList.remove("active");
                showToast("Đã chuyển sang chế độ Tạo Nhanh 1 Chạm.", "info");
            });
            btnModeStep.addEventListener("click", () => {
                currentActiveMode = "step";
                btnModeStep.classList.add("active");
                btnModeQuick.classList.remove("active");
                showToast("Đã chuyển sang chế độ Từng Bước (Kiểm Soát).", "info");
            });
        }

        // Helper update platform badge icon
        function updatePlatformBadge(platform) {
            if (!platformBadge || !platformIcon) return;
            platformBadge.classList.remove("threads", "facebook");
            if (platform === "threads") {
                platformBadge.classList.add("threads");
                platformIcon.className = "fa-brands fa-threads";
            } else if (platform === "facebook") {
                platformBadge.classList.add("facebook");
                platformIcon.className = "fa-brands fa-facebook";
            } else {
                platformIcon.className = "fa-solid fa-link";
            }
        }

        // URL input listener to auto-detect platform
        if (inputUrl) {
            inputUrl.addEventListener("input", () => {
                const val = inputUrl.value.trim().toLowerCase();
                if (val.includes("threads.net") || val.includes("threads.com")) {
                    updatePlatformBadge("threads");
                    if (selectPlatform) selectPlatform.value = "threads";
                } else if (val.includes("facebook.com") || val.includes("fb.com") || val.includes("fb.watch")) {
                    updatePlatformBadge("facebook");
                    if (selectPlatform) selectPlatform.value = "facebook";
                } else {
                    updatePlatformBadge("");
                }
            });
        }

        // Render single comment item HTML with polished styling
        function createCommentElement(comment, index) {
            const card = document.createElement("div");
            card.className = "social-comment-card";
            card.dataset.commentIndex = index;

            const isChecked = comment.selected !== false ? "checked" : "";
            const cAuthor = comment.author?.name || `Bình luận viên ${index + 1}`;
            const cContent = comment.content || "";
            const cLikes = comment.likes || "32";
            const cVoice = comment.voice || (index % 2 === 0 ? "capcut_thanhnientutin" : "capcut_nhongotngao");

            card.innerHTML = `
                <div class="comment-card-top">
                    <label class="comment-checkbox-label">
                        <input type="checkbox" class="comment-check" ${isChecked}>
                        <span class="comment-badge-idx"><i class="fa-solid fa-comment-dots"></i> Bình luận #${index + 1}</span>
                    </label>
                    <button type="button" class="btn-comment-delete" title="Xóa bình luận này">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
                <div class="comment-fields-grid">
                    <div class="comment-field-item">
                        <span class="comment-field-tag"><i class="fa-solid fa-user"></i> Người bình luận</span>
                        <input type="text" class="social-input comment-author" value="${cAuthor}" placeholder="Tên tác giả comment">
                    </div>
                    <div class="comment-field-item">
                        <span class="comment-field-tag"><i class="fa-solid fa-microphone-lines"></i> Giọng đọc AI</span>
                        <select class="social-select comment-voice">
                            <option value="capcut_cogaithoatngon" ${cVoice === 'capcut_cogaithoatngon' ? 'selected' : ''}>🔥 Cô Gái Hoạt Ngôn (CapCut)</option>
                            <option value="capcut_thanhnientutin" ${cVoice === 'capcut_thanhnientutin' ? 'selected' : ''}>🔥 Thanh Niên Tự Tin (CapCut)</option>
                            <option value="capcut_nhongotngao" ${cVoice === 'capcut_nhongotngao' ? 'selected' : ''}>🌸 Nhỏ Ngọt Ngào (CapCut)</option>
                            <option value="capcut_namtram" ${cVoice === 'capcut_namtram' ? 'selected' : ''}>🎙️ Nam Trầm Ấm (CapCut)</option>
                            <option value="vi-VN-HoaiMyNeural" ${cVoice === 'vi-VN-HoaiMyNeural' ? 'selected' : ''}>Edge TTS Hoài My</option>
                            <option value="vi-VN-NamMinhNeural" ${cVoice === 'vi-VN-NamMinhNeural' ? 'selected' : ''}>Edge TTS Nam Minh</option>
                        </select>
                    </div>
                    <div class="comment-field-item">
                        <span class="comment-field-tag"><i class="fa-solid fa-heart"></i> Lượt thích</span>
                        <input type="text" class="social-input comment-likes" value="${cLikes}" placeholder="15">
                    </div>
                </div>
                <div class="comment-field-item">
                    <span class="comment-field-tag"><i class="fa-solid fa-align-left"></i> Nội dung bình luận</span>
                    <textarea class="social-textarea comment-content" rows="2" placeholder="Nội dung bình luận...">${cContent}</textarea>
                </div>
            `;

            const btnRemove = card.querySelector(".btn-comment-delete");
            if (btnRemove) {
                btnRemove.addEventListener("click", () => {
                    card.remove();
                });
            }

            return card;
        }

        // Add manual comment
        if (btnAddComment && commentsContainer) {
            btnAddComment.addEventListener("click", () => {
                const count = commentsContainer.children.length;
                const newCard = createCommentElement({
                    author: { name: `Người dùng ${count + 1}` },
                    content: "Bình luận mới...",
                    likes: "15",
                    selected: true
                }, count);
                commentsContainer.appendChild(newCard);
                newCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
            });
        }

        // Parse Social URL
        async function fetchSocialData() {
            const url = inputUrl ? inputUrl.value.trim() : "";
            if (!url) {
                showToast("Vui lòng nhập link bài viết Threads hoặc Facebook.", "error");
                if (inputUrl) inputUrl.focus();
                return null;
            }

            if (btnFetch) {
                btnFetch.disabled = true;
                btnFetch.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lấy dữ liệu...';
            }

            try {
                const cookieVal = inputCookie ? inputCookie.value.trim() : "";
                const maxCommentsInput = document.getElementById("social-max-comments");
                const includeOpChainInput = document.getElementById("social-include-op-chain");

                const maxCommentsVal = maxCommentsInput ? parseInt(maxCommentsInput.value, 10) || 3 : 3;
                const includeOpChainVal = includeOpChainInput ? includeOpChainInput.checked : true;

                const res = await fetch("/api/social/parse", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        url: url,
                        cookie_raw: cookieVal,
                        max_comments: maxCommentsVal,
                        include_op_chain: includeOpChainVal
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể lấy dữ liệu bài viết.");
                }

                const data = await res.json();

                // Populate UI
                const detectedPlat = data.platform || "threads";
                if (selectPlatform) selectPlatform.value = detectedPlat;
                updatePlatformBadge(detectedPlat);

                if (authorName) authorName.value = data.author?.name || "Người dùng Threads";
                if (authorHandle) authorHandle.value = data.author?.handle || "threads_user";
                if (postContent) postContent.value = data.content || "";
                if (postLikes) postLikes.value = data.likes || "1.2K";
                if (postReplies) postReplies.value = data.replies || (data.comments ? String(data.comments.length) : "24");

                // Show thread chain badge if multiple parts detected
                const badgeBox = document.getElementById("social-chain-badge-box");
                const badgeText = document.getElementById("social-chain-count-text");
                if (badgeBox && badgeText) {
                    if (data.story_parts_count && data.story_parts_count > 1) {
                        badgeBox.classList.remove("d-none");
                        badgeText.textContent = `Đã tự động nối ${data.story_parts_count} phần bài viết của tác giả`;
                    } else {
                        badgeBox.classList.add("d-none");
                    }
                }

                // Render comments
                if (commentsContainer) {
                    commentsContainer.innerHTML = "";
                    const comments = data.comments || [];
                    if (comments.length === 0) {
                        comments.push({
                            author: { name: "Bình luận 1" },
                            content: "Thực sự rất đồng cảm với tác giả!",
                            likes: "45",
                            selected: true
                        });
                        comments.push({
                            author: { name: "Bình luận 2" },
                            content: "Kể chi tiết hơn phần sau đi bạn ơi...",
                            likes: "28",
                            selected: true
                        });
                    }

                    comments.forEach((c, i) => {
                        c.selected = true; // Auto-select all filtered comments up to max_comments
                        const el = createCommentElement(c, i);
                        commentsContainer.appendChild(el);
                    });
                }

                showToast("Đã tải thông tin bài viết và bình luận thành công!", "success");
                return data;
            } catch (err) {
                showToast(err.message, "error");
                return null;
            } finally {
                if (btnFetch) {
                    btnFetch.disabled = false;
                    btnFetch.innerHTML = '<i class="fa-solid fa-cloud-arrow-down"></i> Lấy Dữ Liệu';
                }
            }
        }

        if (btnFetch) {
            btnFetch.addEventListener("click", fetchSocialData);
        }

        // Start video generation
        async function triggerVideoGeneration() {
            const content = postContent ? postContent.value.trim() : "";
            if (!content) {
                showToast("Nội dung bài viết không được để trống.", "error");
                return;
            }

            // Gather selected comments
            const comments = [];
            if (commentsContainer) {
                const commentCards = commentsContainer.querySelectorAll(".social-comment-card");
                commentCards.forEach((cCard, i) => {
                    const check = cCard.querySelector(".comment-check");
                    if (check && check.checked) {
                        const cText = cCard.querySelector(".comment-content")?.value?.trim() || "";
                        if (cText) {
                            comments.push({
                                id: `c_${i + 1}`,
                                author: {
                                    name: cCard.querySelector(".comment-author")?.value?.trim() || `Bình luận viên ${i + 1}`
                                },
                                content: cText,
                                likes: cCard.querySelector(".comment-likes")?.value?.trim() || "20",
                                voice: cCard.querySelector(".comment-voice")?.value || "capcut_thanhnientutin"
                            });
                        }
                    }
                });
            }

            const payload = {
                platform: selectPlatform ? selectPlatform.value : "threads",
                author_name: authorName ? authorName.value.trim() : "Tác giả",
                author_handle: authorHandle ? authorHandle.value.trim() : "user",
                post_content: content,
                post_likes: postLikes ? postLikes.value.trim() : "1.5K",
                post_replies: postReplies ? postReplies.value.trim() : String(comments.length),
                comments: comments,
                post_voice: postVoice ? postVoice.value : "capcut_cogaithoatngon",
                background_video: selectBgVideo ? selectBgVideo.value : "",
                dark_mode: themeDark ? themeDark.checked : true
            };

            // Show result section & reset progress
            if (resultSection) resultSection.classList.remove("d-none");
            if (videoPreviewWrap) videoPreviewWrap.classList.add("d-none");
            if (progressWrap) progressWrap.classList.remove("d-none");
            if (progressBar) progressBar.style.width = "5%";
            if (progressPercent) progressPercent.textContent = "5%";
            if (progressMsg) progressMsg.textContent = "Đang gửi yêu cầu khởi tạo...";

            if (resultSection) {
                resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }

            try {
                const res = await fetch("/api/social/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể khởi tạo tác vụ tạo video.");
                }

                const data = await res.json();
                const taskId = data.task_id;

                pollSocialVideoTask(taskId);

            } catch (e) {
                showToast(e.message, "error");
                if (progressMsg) progressMsg.textContent = `Thất bại: ${e.message}`;
            }
        }

        // Poll task status
        function pollSocialVideoTask(taskId) {
            const timer = setInterval(async () => {
                try {
                    const res = await fetch(`/api/social/status/${taskId}`);
                    if (!res.ok) return;
                    const task = await res.json();

                    if (progressBar) progressBar.style.width = `${task.progress || 0}%`;
                    if (progressPercent) progressPercent.textContent = `${task.progress || 0}%`;
                    if (progressMsg) progressMsg.textContent = task.message || "Đang xử lý...";

                    if (task.status === "completed") {
                        clearInterval(timer);
                        try { showToast("Đã tạo video hoàn tất!", "success"); } catch (e) {}

                        if (progressWrap) progressWrap.classList.add("d-none");
                        if (videoPreviewWrap) {
                            videoPreviewWrap.classList.remove("d-none");
                            videoPreviewWrap.scrollIntoView({ behavior: "smooth", block: "center" });
                        }

                        if (resultVideo) {
                            resultVideo.src = task.video_url;
                            resultVideo.load();
                        }
                        if (btnDownloadVideo) {
                            btnDownloadVideo.href = task.video_url;
                        }
                    } else if (task.status === "failed") {
                        clearInterval(timer);
                        try { showToast(`Lỗi tạo video: ${task.message}`, "error"); } catch (e) {}
                    }
                } catch (err) {
                    console.warn("Polling error:", err);
                }
            }, 1500);
        }

        if (btnBuildVideo) {
            btnBuildVideo.addEventListener("click", triggerVideoGeneration);
        }

        // Quick 1-Click Render Button
        if (btnQuickRender) {
            btnQuickRender.addEventListener("click", async () => {
                if (!postContent || !postContent.value.trim()) {
                    const parsed = await fetchSocialData();
                    if (!parsed) return;
                }
                triggerVideoGeneration();
            });
        }
    }

    initSocialVideoController();

    // ==========================================
    // INITIALIZATION & PROJECT RESTORE
    // ==========================================
    async function initStudioSession() {
        const savedProjId = localStorage.getItem("current_project_id");
        let projectLoaded = false;
        if (savedProjId) {
            try {
                const res = await fetch(`/api/projects/${savedProjId}`);
                if (res.ok) {
                    await openProject(savedProjId, false);
                    projectLoaded = true;
                }
            } catch (e) {
                console.warn("Could not restore saved project", e);
            }
        }

        if (!projectLoaded) {
            // Check if there are any existing projects on server
            try {
                const listRes = await fetch("/api/projects");
                if (listRes.ok) {
                    const list = await listRes.json();
                    if (list && list.length > 0) {
                        await openProject(list[0].id, false);
                        projectLoaded = true;
                    }
                }
            } catch (e) {
                console.warn("Could not check project list", e);
            }
        }

        // If no existing project, create a fresh draft project
        if (!projectLoaded) {
            await createNewProject(false);
        }

        // Initial Routing based on URL hash
        if (window.location.hash === "#social-video") {
            switchView("social-video", false);
        } else if (window.location.hash === "#story-tts") {
            switchView("story-tts", false);
        } else if (window.location.hash === "#dubber") {
            switchView("dubber", false);
        } else {
            switchView("home", false);
        }
    }

    initStudioSession();


    // ==========================================
    // LOGO / WATERMARK OVERLAY ENGINE (TWO-WAY SYNC)
    // ==========================================
    function updateLogoUIFromState() {
        const isEn = Boolean(logoBoxCoords.enabled);

        // 1. Sync Step 5 controls (always keep logoControlsBody visible so user can click upload button anytime)
        if (logoEnabled) logoEnabled.checked = isEn;
        if (logoStatusLabel) logoStatusLabel.textContent = isEn ? "Bật" : "Tắt";
        if (logoControlsBody) logoControlsBody.classList.remove("d-none");
        if (summaryLogoStatus) {
            summaryLogoStatus.textContent = isEn ? (logoBoxCoords.filename ? `Đang bật (${logoBoxCoords.filename})` : "Đang bật") : "Chưa bật";
            summaryLogoStatus.className = "summary-val " + (isEn ? "text-success" : "");
        }

        // 2. Sync Step 3 controls
        if (step3LogoEnabled) step3LogoEnabled.checked = isEn;
        if (step3LogoStatusLabel) step3LogoStatusLabel.textContent = isEn ? "Bật" : "Tắt";
        if (step3LogoOptions) step3LogoOptions.classList.toggle("d-none", !isEn);

        // 3. Sync Quick Canvas Pill & Buttons
        if (btnQuickCanvasLogo) {
            btnQuickCanvasLogo.classList.toggle("active", isEn);
            btnQuickCanvasLogo.innerHTML = isEn
                ? '<i class="fa-solid fa-stamp"></i> Logo: Bật'
                : '<i class="fa-solid fa-stamp"></i> Ghép Logo';
        }
        if (step3BtnToggleLogoBox) {
            step3BtnToggleLogoBox.classList.toggle("active", isEn);
        }
        if (btnToggleLogoBoxPreview) {
            btnToggleLogoBoxPreview.classList.toggle("active", isEn);
        }

        // 4. Sync Bounding Box on Video Canvas
        if (bboxLogo) {
            const shouldShow = (isEn && (currentStudioStep >= 2 || (previewVideoElement && previewVideoElement.src))) || currentStudioStep === 5;
            bboxLogo.classList.toggle("d-none", !shouldShow);
        }

        syncLogoSlidersFromCoords();

        // 5. Sync Images & Placeholders
        const fname = logoBoxCoords.filename || (logoBoxCoords.image_path ? "logo.png" : "");
        if (logoFilenameDisplay) logoFilenameDisplay.textContent = fname || "Chưa chọn ảnh";
        if (step3LogoFilenameDisplay) step3LogoFilenameDisplay.textContent = fname || "Chưa chọn ảnh";

        if (fname || logoBoxCoords.image_path) {
            if (bboxLogoImg) {
                if (!bboxLogoImg.src || bboxLogoImg.src.indexOf("blob:") === -1) {
                    if (currentProjectId) {
                        bboxLogoImg.src = `/api/project/${currentProjectId}/logo?t=${Date.now()}`;
                    }
                }
                bboxLogoImg.classList.remove("d-none");
            }
            if (bboxLogoPlaceholder) bboxLogoPlaceholder.classList.add("d-none");
        } else {
            if (bboxLogoImg && bboxLogoImg.src.indexOf("blob:") === -1) {
                bboxLogoImg.classList.add("d-none");
            }
            if (bboxLogoPlaceholder) bboxLogoPlaceholder.classList.remove("d-none");
        }

        applyBoxStyles();
    }

    function syncLogoSlidersFromCoords() {
        // Step 4 Sliders
        if (logoSliderW) logoSliderW.value = logoBoxCoords.w;
        if (logoWVal) logoWVal.textContent = `${logoBoxCoords.w}%`;
        if (logoSliderOpacity) logoSliderOpacity.value = Math.round(logoBoxCoords.opacity * 100);
        if (logoOpacityVal) logoOpacityVal.textContent = `${Math.round(logoBoxCoords.opacity * 100)}%`;
        if (logoSliderX) logoSliderX.value = logoBoxCoords.x;
        if (logoXVal) logoXVal.textContent = `${logoBoxCoords.x}%`;
        if (logoSliderY) logoSliderY.value = logoBoxCoords.y;
        if (logoYVal) logoYVal.textContent = `${logoBoxCoords.y}%`;

        // Step 3 Sliders
        if (step3LogoSliderW) step3LogoSliderW.value = logoBoxCoords.w;
        if (step3LogoWVal) step3LogoWVal.textContent = `${logoBoxCoords.w}%`;
        if (step3LogoSliderOpacity) step3LogoSliderOpacity.value = Math.round(logoBoxCoords.opacity * 100);
        if (step3LogoOpacityVal) step3LogoOpacityVal.textContent = `${Math.round(logoBoxCoords.opacity * 100)}%`;
        if (step3LogoSliderX) step3LogoSliderX.value = logoBoxCoords.x;
        if (step3LogoXVal) step3LogoXVal.textContent = `${logoBoxCoords.x}%`;
        if (step3LogoSliderY) step3LogoSliderY.value = logoBoxCoords.y;
        if (step3LogoYVal) step3LogoYVal.textContent = `${logoBoxCoords.y}%`;
    }

    async function handleLogoFileUpload(file) {
        if (!file) return;

        const blobUrl = URL.createObjectURL(file);
        if (bboxLogoImg) {
            bboxLogoImg.src = blobUrl;
            bboxLogoImg.classList.remove("d-none");
        }
        if (bboxLogoPlaceholder) bboxLogoPlaceholder.classList.add("d-none");
        if (logoFilenameDisplay) logoFilenameDisplay.textContent = file.name;
        if (step3LogoFilenameDisplay) step3LogoFilenameDisplay.textContent = file.name;

        logoBoxCoords.enabled = true;
        logoBoxCoords.filename = file.name;

        updateLogoUIFromState();

        if (!currentProjectId) {
            await createNewProject(false);
        }

        if (currentProjectId) {
            const fd = new FormData();
            fd.append("file", file);
            try {
                const res = await fetch(`/api/project/${currentProjectId}/logo`, {
                    method: "POST",
                    body: fd
                });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || "Không thể tải ảnh logo lên server.");
                }
                const data = await res.json();
                if (data && data.logo_box) {
                    logoBoxCoords.image_path = data.logo_box.image_path;
                    logoBoxCoords.filename = data.logo_box.filename || file.name;
                    logoBoxCoords.enabled = true;
                }
                updateLogoUIFromState();
                await autoSaveProjectState();
                setSaveStatus("saved", `Đã gắn logo: ${file.name}`);
            } catch (err) {
                console.error("Lỗi khi tải logo lên server:", err);
                alert("Lỗi tải ảnh logo: " + err.message);
            }
        }
    }

    function applyLogoPreset(pos) {
        const w = logoBoxCoords.w || 18;
        const h = logoBoxCoords.h || 12;
        if (pos === "top-left") {
            logoBoxCoords.x = 4;
            logoBoxCoords.y = 4;
        } else if (pos === "top-right") {
            logoBoxCoords.x = Math.max(0, 100 - w - 4);
            logoBoxCoords.y = 4;
        } else if (pos === "bottom-left") {
            logoBoxCoords.x = 4;
            logoBoxCoords.y = Math.max(0, 100 - h - 5);
        } else if (pos === "bottom-right") {
            logoBoxCoords.x = Math.max(0, 100 - w - 4);
            logoBoxCoords.y = Math.max(0, 100 - h - 5);
        } else if (pos === "center") {
            logoBoxCoords.x = Math.max(0, Math.round((100 - w) / 2));
            logoBoxCoords.y = Math.max(0, Math.round((100 - h) / 2));
        }
        document.querySelectorAll(".logo-pos-btn").forEach(btn => {
            btn.classList.toggle("active", btn.getAttribute("data-pos") === pos);
        });
        syncLogoSlidersFromCoords();
        applyBoxStyles();
        triggerDebouncedAutoSave(1000);
    }

    // Connect File Uploaders (Step 3 & Step 5)
    if (btnUploadLogo && logoFileInput) {
        btnUploadLogo.addEventListener("click", () => {
            logoFileInput.value = "";
            logoFileInput.click();
        });
        logoFileInput.addEventListener("change", (e) => handleLogoFileUpload(e.target.files && e.target.files[0]));
    }
    if (step3BtnUploadLogo && step3LogoFileInput) {
        step3BtnUploadLogo.addEventListener("click", () => {
            step3LogoFileInput.value = "";
            step3LogoFileInput.click();
        });
        step3LogoFileInput.addEventListener("change", (e) => handleLogoFileUpload(e.target.files && e.target.files[0]));
    }
    if (bboxLogoPlaceholder && logoFileInput) {
        bboxLogoPlaceholder.style.cursor = "pointer";
        bboxLogoPlaceholder.title = "Nhấp để chọn ảnh Logo";
        bboxLogoPlaceholder.addEventListener("click", (e) => {
            e.stopPropagation();
            logoFileInput.value = "";
            logoFileInput.click();
        });
    }

    // Connect Switches (Step 3 & Step 5)
    if (logoEnabled) {
        logoEnabled.addEventListener("change", () => {
            logoBoxCoords.enabled = logoEnabled.checked;
            updateLogoUIFromState();
            triggerDebouncedAutoSave(1000);
            if (logoBoxCoords.enabled && !logoBoxCoords.filename && !logoBoxCoords.image_path && logoFileInput) {
                logoFileInput.value = "";
                logoFileInput.click();
            }
        });
    }
    if (step3LogoEnabled) {
        step3LogoEnabled.addEventListener("change", () => {
            logoBoxCoords.enabled = step3LogoEnabled.checked;
            updateLogoUIFromState();
            triggerDebouncedAutoSave(1000);
        });
    }

    // Connect Toggle Box Visibility Buttons
    const toggleBoxAction = () => {
        if (!bboxLogo) return;
        const isHidden = bboxLogo.classList.contains("d-none");
        bboxLogo.classList.toggle("d-none", !isHidden);
        const labelText = isHidden ? '<i class="fa-solid fa-eye-slash"></i> Ẩn khung Logo' : '<i class="fa-solid fa-vector-square"></i> Hiện khung Logo';
        if (btnToggleLogoBoxPreview) btnToggleLogoBoxPreview.innerHTML = labelText;
        if (step3BtnToggleLogoBox) step3BtnToggleLogoBox.innerHTML = labelText;
    };
    if (btnToggleLogoBoxPreview) btnToggleLogoBoxPreview.addEventListener("click", toggleBoxAction);
    if (step3BtnToggleLogoBox) step3BtnToggleLogoBox.addEventListener("click", toggleBoxAction);

    // Connect Quick Canvas Logo Button (below video)
    if (btnQuickCanvasLogo) {
        btnQuickCanvasLogo.addEventListener("click", () => {
            if (!logoBoxCoords.enabled) {
                logoBoxCoords.enabled = true;
                updateLogoUIFromState();
                if (!logoBoxCoords.filename && !logoBoxCoords.image_path) {
                    if (step3LogoFileInput) step3LogoFileInput.click();
                    else if (logoFileInput) logoFileInput.click();
                }
            } else {
                toggleBoxAction();
            }
        });
    }

    // Connect Step 5 Sliders
    [
        { el: logoSliderW, field: "w", isInt: true },
        { el: logoSliderOpacity, field: "opacity", isOpacity: true },
        { el: logoSliderX, field: "x", isInt: true },
        { el: logoSliderY, field: "y", isInt: true }
    ].forEach(({ el, field, isInt, isOpacity }) => {
        if (el) {
            el.addEventListener("input", () => {
                if (isOpacity) logoBoxCoords.opacity = parseInt(el.value) / 100.0;
                else logoBoxCoords[field] = parseInt(el.value);
                syncLogoSlidersFromCoords();
                applyBoxStyles();
                triggerDebouncedAutoSave(1000);
            });
        }
    });

    // Connect Step 3 Sliders
    [
        { el: step3LogoSliderW, field: "w", isInt: true },
        { el: step3LogoSliderOpacity, field: "opacity", isOpacity: true },
        { el: step3LogoSliderX, field: "x", isInt: true },
        { el: step3LogoSliderY, field: "y", isInt: true }
    ].forEach(({ el, field, isInt, isOpacity }) => {
        if (el) {
            el.addEventListener("input", () => {
                if (isOpacity) logoBoxCoords.opacity = parseInt(el.value) / 100.0;
                else logoBoxCoords[field] = parseInt(el.value);
                syncLogoSlidersFromCoords();
                applyBoxStyles();
                triggerDebouncedAutoSave(1000);
            });
        }
    });

    // Connect all Preset buttons across the page
    document.querySelectorAll(".logo-pos-btn").forEach(btn => {
        btn.addEventListener("click", () => applyLogoPreset(btn.getAttribute("data-pos")));
    });

    // Initialize logo UI on load
    updateLogoUIFromState();

    // ==========================================
    // STEP 3: EXPLICIT GENERATE TTS BUTTON LOGIC
    // ==========================================
    const btnStep3GenerateTTS = document.getElementById("btn-step3-generate-tts");
    const btnRetryFailedTTS = document.getElementById("btn-retry-failed-tts");
    let ttsGenPollingInterval = null;

    async function startTtsGeneration(failedOnly = false) {
        if (!currentProjectId) {
            alert("Chưa có dự án.");
            return;
        }

        const voice = voiceSelectStep3 ? voiceSelectStep3.value : "female_hoaimy";

        if (failedOnly) {
            if (btnRetryFailedTTS) {
                btnRetryFailedTTS.disabled = true;
                btnRetryFailedTTS.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang tạo lại câu lỗi...`;
            }
        } else {
            if (btnStep3GenerateTTS) {
                btnStep3GenerateTTS.disabled = true;
                btnStep3GenerateTTS.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang tạo giọng đọc...`;
            }
        }

        if (step3ProgressBox) step3ProgressBox.classList.remove("d-none");
        if (step3ProgressBar) step3ProgressBar.style.width = "0%";
        if (step3ProgressPct) step3ProgressPct.textContent = "0%";
        if (step3ProgressMsg) step3ProgressMsg.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${failedOnly ? "Đang tạo lại các câu thoại bị lỗi..." : "Đang khởi động tạo giọng đọc AI..."}`;

        setTerminalVisible(true);
        if (step1TerminalStatusTag) {
            step1TerminalStatusTag.className = "terminal-status-tag";
            step1TerminalStatusTag.textContent = failedOnly ? "Đang tạo lại câu lỗi" : "Đang tạo giọng đọc";
        }
        appendTerminalLog(`[${new Date().toTimeString().slice(0, 8)}] [INFO] Bắt đầu ${failedOnly ? "tạo lại các câu thoại bị lỗi" : "sinh giọng đọc AI"} (${voice})...`);

        try {
            const res = await fetch(`/api/project/${currentProjectId}/generate-tts`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ voice, failed_only: failedOnly, use_original: false })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Không thể khởi động tạo giọng đọc.");
            }

            if (ttsGenPollingInterval) clearInterval(ttsGenPollingInterval);
            ttsGenPollingInterval = setInterval(async () => {
                try {
                    const statusRes = await fetch(`/api/project/${currentProjectId}/status`);
                    if (!statusRes.ok) return;
                    const statusData = await statusRes.json();

                    if (statusData.logs) updateTerminalLogs(statusData.logs);

                    const progress = statusData.progress || 0;
                    const msg = statusData.message || "Đang tạo giọng đọc...";

                    if (step3ProgressBar) step3ProgressBar.style.width = `${progress}%`;
                    if (step3ProgressPct) step3ProgressPct.textContent = `${progress}%`;
                    if (step3ProgressMsg) step3ProgressMsg.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${msg}`;

                    if (statusData.status === "tts_ready") {
                        clearInterval(ttsGenPollingInterval);
                        if (btnStep3GenerateTTS) {
                            btnStep3GenerateTTS.disabled = false;
                            btnStep3GenerateTTS.innerHTML = `<i class="fa-solid fa-circle-check"></i> Đã Tạo Xong! Nhấn Để Tạo Lại`;
                        }
                        if (btnRetryFailedTTS) {
                            btnRetryFailedTTS.disabled = false;
                            btnRetryFailedTTS.innerHTML = `<i class="fa-solid fa-rotate-right"></i> Tạo lại câu lỗi (<span id="failed-tts-count">0</span>)`;
                        }

                        // Reload updated segments from backend to refresh status and errors in table
                        try {
                            const segsRes = await fetch(`/api/project/${currentProjectId}/segments`);
                            if (segsRes.ok) {
                                segmentsData = await segsRes.json();
                                renderSegmentsTable(segmentsData);
                                renderTimeline();
                            }
                        } catch (e) {
                            console.warn("Could not reload segments:", e);
                        }

                        const remainingFailed = statusData.failed_count || 0;
                        if (remainingFailed > 0) {
                            if (step3ProgressMsg) {
                                step3ProgressMsg.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #fbbf24;"></i> Đã xử lý xong. Còn <strong>${remainingFailed}</strong> câu chưa tạo được tiếng. Hãy bấm <em>'Tạo lại câu lỗi'</em> ở Bảng Phụ Đề để thử lại.`;
                            }
                        } else {
                            if (step3ProgressMsg) {
                                step3ProgressMsg.innerHTML = `<i class="fa-solid fa-circle-check" style="color: #4ade80;"></i> Toàn bộ câu thoại đã được tạo giọng đọc thành công! Bấm nút Phát để nghe thử.`;
                            }
                        }

                        loadPreviewDubbedAudio(true);
                        unlockStep(4);
                        unlockStep(5);
                        markStepDone(3);
                        setSaveStatus("saved", "Đã cập nhật giọng đọc thành công!");
                    } else if (statusData.status === "error") {
                        clearInterval(ttsGenPollingInterval);
                        if (btnStep3GenerateTTS) {
                            btnStep3GenerateTTS.disabled = false;
                            btnStep3GenerateTTS.innerHTML = `<i class="fa-solid fa-rotate-right"></i> Thử Tạo Lại Giọng Đọc`;
                        }
                        if (btnRetryFailedTTS) {
                            btnRetryFailedTTS.disabled = false;
                            btnRetryFailedTTS.innerHTML = `<i class="fa-solid fa-rotate-right"></i> Tạo lại câu lỗi`;
                        }
                        if (step3ProgressMsg) step3ProgressMsg.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i> ${statusData.message || "Lỗi tạo giọng đọc"}`;
                    }
                } catch (e) {
                    console.error(e);
                }
            }, 1200);
        } catch (err) {
            console.error("Start generate-tts failed:", err);
            if (btnStep3GenerateTTS) {
                btnStep3GenerateTTS.disabled = false;
                btnStep3GenerateTTS.innerHTML = `<i class="fa-solid fa-microphone-lines"></i> 3. Bắt Đầu Tạo Giọng Đọc Cho Video`;
            }
            if (btnRetryFailedTTS) {
                btnRetryFailedTTS.disabled = false;
                btnRetryFailedTTS.innerHTML = `<i class="fa-solid fa-rotate-right"></i> Tạo lại câu lỗi`;
            }
            alert("Lỗi: " + err.message);
        }
    }

    if (btnStep3GenerateTTS) {
        btnStep3GenerateTTS.addEventListener("click", () => startTtsGeneration(false));
    }
    const btnResetToOriginal = document.getElementById("btn-reset-to-original");
    if (btnResetToOriginal) {
        btnResetToOriginal.addEventListener("click", async () => {
            if (!currentProjectId) return;
            if (!confirm("Bạn có chắc chắn muốn khôi phục lại câu gốc từ Bước 2? Mọi đoạn tự thêm/cắt ở Bước 3 sẽ bị xóa.")) return;
            try {
                btnResetToOriginal.disabled = true;
                btnResetToOriginal.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang khôi phục...`;
                const res = await fetch(`/api/project/${currentProjectId}/reset-to-original`, { method: "POST" });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể khôi phục.");
                }
                const data = await res.json();
                segmentsData = data.segments || [];
                renderSegmentsTable(segmentsData);
                renderTimeline();
                setSaveStatus("saved", "Đã khôi phục câu gốc từ Bước 2 thành công!");
                alert("Đã khôi phục 100% câu thoại gốc từ Bước 2 thành công!");
            } catch (e) {
                alert("Lỗi: " + e.message);
            } finally {
                btnResetToOriginal.disabled = false;
                btnResetToOriginal.innerHTML = `<i class="fa-solid fa-rotate-left"></i> Khôi phục câu gốc từ Bước 2`;
            }
        });
    }
    if (btnRetryFailedTTS) {
        btnRetryFailedTTS.addEventListener("click", () => startTtsGeneration(true));
    }

    // Drop the browser-side preview audio so no stale track keeps playing after a cleanup
    function resetDubbingAudioElement() {
        pauseDubbingAudio();
        dubbingAudio.removeAttribute("src");
        dubbingAudio.load();
        isDubbingAudioLoaded = false;
        isDubbingAudioLoading = false;
    }

    async function runClearAction(btn, url, confirmMsg, doneMsg) {
        if (!currentProjectId) return;
        if (!confirm(confirmMsg)) return;
        const origHTML = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang xóa...`;
        try {
            const res = await fetch(`/api/project/${currentProjectId}/${url}`, { method: "POST" });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Không thể xóa dữ liệu.");
            }
            const data = await res.json();
            segmentsData = data.segments || [];
            resetDubbingAudioElement();
            renderSegmentsTable(segmentsData);
            renderTimeline();
            setSaveStatus("saved", `${doneMsg} (đã xóa ${data.removed_audio_files || 0} file âm thanh)`);
        } catch (e) {
            alert("Lỗi: " + e.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = origHTML;
        }
    }

    const btnClearTranslations = document.getElementById("btn-clear-translations");
    if (btnClearTranslations) {
        btnClearTranslations.addEventListener("click", () => runClearAction(
            btnClearTranslations,
            "clear-translations",
            "Xóa TOÀN BỘ bản dịch tiếng Việt và âm thanh đã tạo? Không thể hoàn tác.",
            "Đã xóa toàn bộ bản dịch"
        ));
    }
    const btnClearAudio = document.getElementById("btn-clear-audio");
    if (btnClearAudio) {
        btnClearAudio.addEventListener("click", () => runClearAction(
            btnClearAudio,
            "clear-audio",
            "Xóa TOÀN BỘ âm thanh đã tạo? (Bản dịch được giữ nguyên)",
            "Đã xóa toàn bộ âm thanh"
        ));
    }

    // ==========================================
    // STEP 2: XUẤT / COPY SRT GỐC
    // ==========================================
    const btnStep2CopyZhSrt = document.getElementById("btn-step2-copy-zh-srt");
    const btnStep2DownloadZhSrt = document.getElementById("btn-step2-download-zh-srt");
    if (btnStep2CopyZhSrt) {
        btnStep2CopyZhSrt.addEventListener("click", async () => {
            const srtText = buildLocalSrtString("zh");
            if (!srtText) {
                alert("Chưa có phụ đề gốc nào để copy.");
                return;
            }
            try {
                await navigator.clipboard.writeText(srtText);
                const oldText = btnStep2CopyZhSrt.innerHTML;
                btnStep2CopyZhSrt.innerHTML = `<i class="fa-solid fa-check"></i> Đã Copy SRT Gốc!`;
                setTimeout(() => { btnStep2CopyZhSrt.innerHTML = oldText; }, 1800);
            } catch (e) {
                alert("Không thể copy: " + e.message);
            }
        });
    }
    if (btnStep2DownloadZhSrt) {
        btnStep2DownloadZhSrt.addEventListener("click", () => downloadProjectSrt("zh"));
    }

    // ==========================================
    // STEP 3: DỊCH PHỤ ĐỀ (AI HOẶC NẠP SRT NGOÀI)
    // ==========================================
    const btnTabTranslateAi = document.getElementById("btn-tab-translate-ai");
    const btnTabTranslateSrt = document.getElementById("btn-tab-translate-srt");
    const paneTranslateAi = document.getElementById("pane-translate-ai");
    const paneTranslateSrt = document.getElementById("pane-translate-srt");

    if (btnTabTranslateAi && btnTabTranslateSrt) {
        btnTabTranslateAi.addEventListener("click", () => {
            btnTabTranslateAi.classList.add("active");
            btnTabTranslateSrt.classList.remove("active");
            if (paneTranslateAi) paneTranslateAi.classList.remove("d-none");
            if (paneTranslateSrt) paneTranslateSrt.classList.add("d-none");
        });
        btnTabTranslateSrt.addEventListener("click", () => {
            btnTabTranslateSrt.classList.add("active");
            btnTabTranslateAi.classList.remove("active");
            if (paneTranslateSrt) paneTranslateSrt.classList.remove("d-none");
            if (paneTranslateAi) paneTranslateAi.classList.add("d-none");
        });
    }

    async function loadAppSettings() {
        try {
            const res = await fetch("/api/settings");
            if (res.ok) {
                const s = await res.json();
                const selEngine = document.getElementById("select-translation-engine");
                const inpGroqKey = document.getElementById("input-groq-key");
                const inpGemKey = document.getElementById("input-gemini-key");
                const groqWrap = document.getElementById("groq-key-wrap");
                const gemWrap = document.getElementById("gemini-key-wrap");
                const statusTag = document.getElementById("translation-status-tag");

                const engine = s.translation_engine || "groq";
                if (selEngine) {
                    selEngine.value = engine;
                }

                if (groqWrap && gemWrap) {
                    if (engine === "groq") {
                        groqWrap.classList.remove("d-none");
                        gemWrap.classList.add("d-none");
                    } else if (engine === "gemini") {
                        gemWrap.classList.remove("d-none");
                        groqWrap.classList.add("d-none");
                    } else {
                        groqWrap.classList.add("d-none");
                        gemWrap.classList.add("d-none");
                    }
                }

                if (inpGroqKey && s.groq_api_key_masked) {
                    inpGroqKey.value = s.groq_api_key_masked;
                }
                if (inpGemKey && s.gemini_api_key_masked) {
                    inpGemKey.value = s.gemini_api_key_masked;
                }

                if (statusTag) {
                    if (engine === "groq") {
                        if (s.has_groq_key) {
                            statusTag.className = "status-pill status-ready";
                            statusTag.innerHTML = `<i class="fa-solid fa-circle-check"></i> Groq Qwen 3.8 27B (Sẵn sàng)`;
                        } else {
                            statusTag.className = "status-pill";
                            statusTag.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Groq: Chưa có Key`;
                        }
                    } else if (engine === "gemini") {
                        if (s.has_gemini_key) {
                            statusTag.className = "status-pill status-ready";
                            statusTag.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${s.gemini_model || "Gemini 3.5 Flash"} (Sẵn sàng)`;
                        } else {
                            statusTag.className = "status-pill";
                            statusTag.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Gemini: Chưa có Key`;
                        }
                    } else {
                        statusTag.className = "status-pill status-ready";
                        statusTag.innerHTML = `<i class="fa-solid fa-circle-check"></i> Google Dịch (Sẵn sàng)`;
                    }
                }
            }
        } catch (e) {
            console.warn("Could not load settings", e);
        }
    }

    const btnSaveGroqKey = document.getElementById("btn-save-groq-key");
    if (btnSaveGroqKey) {
        btnSaveGroqKey.addEventListener("click", async () => {
            const inpKey = document.getElementById("input-groq-key");
            const rawKey = inpKey ? inpKey.value.trim() : "";
            try {
                const res = await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        translation_engine: "groq",
                        groq_api_key: rawKey
                    })
                });
                if (res.ok) {
                    alert("Đã lưu Groq API Key thành công!");
                    await loadAppSettings();
                }
            } catch (e) {
                alert("Lỗi lưu cấu hình Groq: " + e.message);
            }
        });
    }

    const btnSaveGeminiKey = document.getElementById("btn-save-gemini-key");
    if (btnSaveGeminiKey) {
        btnSaveGeminiKey.addEventListener("click", async () => {
            const inpKey = document.getElementById("input-gemini-key");
            const rawKey = inpKey ? inpKey.value.trim() : "";
            try {
                const res = await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        translation_engine: "gemini",
                        gemini_api_key: rawKey
                    })
                });
                if (res.ok) {
                    alert("Đã lưu Gemini API Key thành công!");
                    await loadAppSettings();
                }
            } catch (e) {
                alert("Lỗi lưu cấu hình Gemini: " + e.message);
            }
        });
    }

    const selTranslationEngine = document.getElementById("select-translation-engine");
    if (selTranslationEngine) {
        selTranslationEngine.addEventListener("change", async () => {
            const val = selTranslationEngine.value;
            const groqWrap = document.getElementById("groq-key-wrap");
            const gemWrap = document.getElementById("gemini-key-wrap");
            if (groqWrap && gemWrap) {
                if (val === "groq") {
                    groqWrap.classList.remove("d-none");
                    gemWrap.classList.add("d-none");
                } else if (val === "gemini") {
                    gemWrap.classList.remove("d-none");
                    groqWrap.classList.add("d-none");
                } else {
                    groqWrap.classList.add("d-none");
                    gemWrap.classList.add("d-none");
                }
            }
            try {
                await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ translation_engine: val })
                });
                await loadAppSettings();
            } catch (e) {
                console.warn(e);
            }
        });
    }

    // Step 3: Dịch tự động bằng AI / Dịch lại câu lỗi
    const btnStep3StartAi = document.getElementById("btn-step3-start-ai");
    const btnStep3RetryFailedTranslate = document.getElementById("btn-step3-retry-failed-translate");
    const btnTableRetryFailedTranslate = document.getElementById("btn-retry-failed-translate");

    async function startTranslationProcess(failedOnly = false) {
        if (!currentProjectId) {
            alert("Vui lòng tải hoặc mở một dự án trước!");
            return;
        }
        if (!segmentsData || segmentsData.length === 0) {
            alert("Chưa có phụ đề gốc từ Bước 2 để dịch. Vui lòng quét Bước 2 trước.");
            return;
        }

        const selEngine = document.getElementById("select-translation-engine");
        const engine = selEngine ? selEngine.value : "groq";

        if (btnStep3StartAi) btnStep3StartAi.disabled = true;
        if (btnStep3RetryFailedTranslate) btnStep3RetryFailedTranslate.disabled = true;
        if (btnTableRetryFailedTranslate) btnTableRetryFailedTranslate.disabled = true;

        const pBox = document.getElementById("step3-progress-box");
        const pBar = document.getElementById("step3-progress-bar");
        const pMsg = document.getElementById("step3-progress-msg");
        const pPct = document.getElementById("step3-progress-pct");
        if (pBox) pBox.classList.remove("d-none");
        if (pBar) pBar.style.width = "10%";
        if (pMsg) pMsg.textContent = failedOnly ? `Đang dịch lại các câu lỗi bằng ${engine.toUpperCase()}...` : `Đang kết nối dịch bằng ${engine.toUpperCase()}...`;

        setTerminalVisible(true);
        if (step1TerminalStatusTag) {
            step1TerminalStatusTag.className = "terminal-status-tag";
            step1TerminalStatusTag.textContent = failedOnly ? "Đang dịch lại câu lỗi" : "Đang dịch AI";
        }
        appendTerminalLog(`[${new Date().toTimeString().slice(0, 8)}] [INFO] ${failedOnly ? "Bắt đầu dịch lại các câu lỗi/sót chữ Hán" : "Bắt đầu dịch tự động"} (${engine.toUpperCase()})...`);

        try {
            const res = await fetch(`/api/project/${currentProjectId}/translate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ engine, failed_only: failedOnly })
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Không thể khởi động dịch.");
            }

            let pollTranslate = setInterval(async () => {
                try {
                    const sRes = await fetch(`/api/project/${currentProjectId}/status`);
                    if (!sRes.ok) return;
                    const sData = await sRes.json();
                    if (sData.logs) updateTerminalLogs(sData.logs);
                    if (pBar) pBar.style.width = `${sData.progress || 0}%`;
                    if (pPct) pPct.textContent = `${sData.progress || 0}%`;
                    if (pMsg) pMsg.textContent = sData.message || "Đang dịch...";

                    if (sData.status === "translated") {
                        clearInterval(pollTranslate);
                        if (btnStep3StartAi) btnStep3StartAi.disabled = false;
                        if (btnStep3RetryFailedTranslate) btnStep3RetryFailedTranslate.disabled = false;
                        if (btnTableRetryFailedTranslate) btnTableRetryFailedTranslate.disabled = false;
                        if (pBox) pBox.classList.add("d-none");
                        if (step1TerminalStatusTag) {
                            step1TerminalStatusTag.className = "terminal-status-tag status-done";
                            step1TerminalStatusTag.textContent = "Đã dịch xong";
                        }

                        renderSegmentsTable(sData.segments || []);
                        loadPreviewDubbedAudio(false);
                        markStepDone(3);
                        unlockStep(4);
                        if (!failedOnly) {
                            switchStep(4);
                        }
                    } else if (sData.status === "translate_failed") {
                        clearInterval(pollTranslate);
                        if (btnStep3StartAi) btnStep3StartAi.disabled = false;
                        if (btnStep3RetryFailedTranslate) btnStep3RetryFailedTranslate.disabled = false;
                        if (btnTableRetryFailedTranslate) btnTableRetryFailedTranslate.disabled = false;
                        if (step1TerminalStatusTag) {
                            step1TerminalStatusTag.className = "terminal-status-tag tag-error";
                            step1TerminalStatusTag.textContent = "Lỗi dịch";
                        }
                        alert("Dịch thất bại: " + (sData.error || sData.message));
                    }
                } catch (pe) {
                    console.error(pe);
                }
            }, 1000);
        } catch (e) {
            if (btnStep3StartAi) btnStep3StartAi.disabled = false;
            if (btnStep3RetryFailedTranslate) btnStep3RetryFailedTranslate.disabled = false;
            if (btnTableRetryFailedTranslate) btnTableRetryFailedTranslate.disabled = false;
            if (pBox) pBox.classList.add("d-none");
            alert(e.message);
        }
    }

    if (btnStep3StartAi) {
        btnStep3StartAi.addEventListener("click", () => startTranslationProcess(false));
    }
    if (btnStep3RetryFailedTranslate) {
        btnStep3RetryFailedTranslate.addEventListener("click", () => startTranslationProcess(true));
    }
    if (btnTableRetryFailedTranslate) {
        btnTableRetryFailedTranslate.addEventListener("click", () => startTranslationProcess(true));
    }

    // Step 3: Nạp file / dán nội dung SRT tiếng Việt
    const btnStep3BrowseSrt = document.getElementById("btn-step3-browse-srt");
    const inputStep3SrtFile = document.getElementById("input-step3-srt-file");
    const step3SrtFileName = document.getElementById("step3-srt-file-name");
    const step3SrtPasteArea = document.getElementById("step3-srt-paste-area");
    const btnStep3ApplyCustomSrt = document.getElementById("btn-step3-apply-custom-srt");

    if (btnStep3BrowseSrt && inputStep3SrtFile) {
        btnStep3BrowseSrt.addEventListener("click", () => inputStep3SrtFile.click());
        inputStep3SrtFile.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                if (step3SrtFileName) step3SrtFileName.textContent = file.name;
                const reader = new FileReader();
                reader.onload = (evt) => {
                    if (step3SrtPasteArea) step3SrtPasteArea.value = evt.target.result;
                };
                reader.readAsText(file, "UTF-8");
            }
        });
    }

    if (btnStep3ApplyCustomSrt) {
        btnStep3ApplyCustomSrt.addEventListener("click", async () => {
            if (!currentProjectId) {
                alert("Vui lòng tải hoặc mở một dự án trước!");
                return;
            }
            const srtContent = step3SrtPasteArea ? step3SrtPasteArea.value.trim() : "";
            if (!srtContent) {
                alert("Vui lòng chọn file .srt hoặc dán nội dung bản dịch vào ô nhập trước khi áp dụng.");
                return;
            }

            btnStep3ApplyCustomSrt.disabled = true;
            const pBox = document.getElementById("step3-progress-box");
            const pBar = document.getElementById("step3-progress-bar");
            const pMsg = document.getElementById("step3-progress-msg");
            if (pBox) pBox.classList.remove("d-none");
            if (pBar) pBar.style.width = "20%";
            if (pMsg) pMsg.textContent = "Đang khớp mốc thời gian và áp dụng bản dịch...";

            try {
                const res = await fetch(`/api/project/${currentProjectId}/translate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ custom_srt: srtContent })
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Không thể áp dụng bản dịch.");
                }

                let pollCustom = setInterval(async () => {
                    try {
                        const sRes = await fetch(`/api/project/${currentProjectId}/status`);
                        if (!sRes.ok) return;
                        const sData = await sRes.json();
                        if (sData.status === "translated") {
                            clearInterval(pollCustom);
                            btnStep3ApplyCustomSrt.disabled = false;
                            if (pBox) pBox.classList.add("d-none");
                            renderSegmentsTable(sData.segments || []);
                            loadPreviewDubbedAudio(false);
                            markStepDone(3);
                            unlockStep(4);
                            switchStep(4);
                        } else if (sData.status === "translate_failed") {
                            clearInterval(pollCustom);
                            btnStep3ApplyCustomSrt.disabled = false;
                            alert("Áp dụng bản dịch thất bại: " + (sData.error || sData.message));
                        }
                    } catch (pe) {
                        console.error(pe);
                    }
                }, 1000);
            } catch (e) {
                btnStep3ApplyCustomSrt.disabled = false;
                if (pBox) pBox.classList.add("d-none");
                alert(e.message);
            }
        });
    }

    loadAppSettings();

    // ==========================================
    // STEP NAVIGATION BUTTONS (NEXT / PREV)
    // ==========================================
    const btnStep1Next = document.getElementById("btn-step1-next");
    const btnStep2Prev = document.getElementById("btn-step2-prev");
    const btnStep2Next = document.getElementById("btn-step2-next");
    const btnStep3Prev = document.getElementById("btn-step3-prev");
    const btnStep4Prev = document.getElementById("btn-step4-prev");
    const btnStep4Next = document.getElementById("btn-step4-next");
    const btnStep5Prev = document.getElementById("btn-step5-prev");
    const btnStep5Next = document.getElementById("btn-step5-next");
    const btnStep6Prev = document.getElementById("btn-step6-prev");

    if (btnStep1Next) btnStep1Next.addEventListener("click", () => { unlockStep(2); switchStep(2); });
    if (btnStep2Prev) btnStep2Prev.addEventListener("click", () => switchStep(1));
    if (btnStep2Next) btnStep2Next.addEventListener("click", async () => {
        try { await saveSegmentsToServer(); } catch (e) { console.warn(e); }
        markStepDone(2);
        unlockStep(3);
        switchStep(3);
    });
    if (btnStep3Prev) btnStep3Prev.addEventListener("click", () => switchStep(2));
    if (btnStep4Prev) btnStep4Prev.addEventListener("click", () => switchStep(3));
    if (btnStep4Next) btnStep4Next.addEventListener("click", () => {
        markStepDone(4);
        unlockStep(5);
        switchStep(5);
    });
    if (btnStep5Prev) btnStep5Prev.addEventListener("click", () => switchStep(4));
    if (btnStep5Next) btnStep5Next.addEventListener("click", () => {
        markStepDone(5);
        unlockStep(6);
        switchStep(6);
    });
    if (btnStep6Prev) btnStep6Prev.addEventListener("click", () => switchStep(5));

});
