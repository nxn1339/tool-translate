document.addEventListener("DOMContentLoaded", () => {
    // Translation Dictionary
    const TRANSLATIONS = {
        vi: {
            subtitle: "Dịch thuật & Lồng tiếng video Bilibili tự động bằng trí tuệ nhân tạo",
            config_title: "Cấu hình dự án",
            url_label: "Link video Bilibili / YouTube",
            voice_label: "Giọng đọc lồng tiếng",
            opt_voice_tiktok: "Cô gái hoạt ngôn (TikTok style - Nhanh, vui vẻ) 🌟",
            opt_voice_gentle: "Cô gái nhẹ nhàng (Truyền cảm, ngọt ngào)",
            opt_voice_warm: "Giọng nam trầm ấm (Thuyết minh phim/tài liệu)",
            opt_voice_fast: "Giọng nam năng động (Nhanh, tự tin)",
            lang_label: "Ngôn ngữ gốc",
            opt_lang_zh: "Tiếng Trung (Giản thể)",
            opt_lang_en: "Tiếng Anh",
            opt_lang_ja: "Tiếng Nhật",
            opt_lang_ko: "Tiếng Hàn",
            volume_title: "Căn chỉnh âm lượng",
            tts_vol_label: "Giọng lồng tiếng Việt (TTS)",
            bg_vol_label: "Âm thanh gốc/Nhạc nền (Background)",
            advanced_title: "Cấu hình nâng cao",
            cookie_label: "Bilibili Cookie (SESSDATA)",
            cookie_desc: "Nhập giá trị SESSDATA từ Cookie của Bilibili để khắc phục lỗi tải video (HTTP 412).",
            cookie_placeholder: "SESSDATA=xxxxxx; hoặc dán toàn bộ chuỗi Cookie từ trình duyệt của bạn...",
            start_btn: "Bắt Đầu Dịch & Lồng Tiếng",
            status_title: "Trạng thái xử lý",
            idle_tip: "Nhập link video và nhấn nút \"Bắt đầu\" để khởi chạy tiến trình.",
            badge_processing: "Đang xử lý",
            step_download: "Tải video & Tách âm thanh",
            step_translate: "Nhận dạng giọng nói & Dịch phụ đề",
            step_tts: "Tạo giọng lồng tiếng Việt",
            step_merge: "Ghép nối & Xuất video hoàn chỉnh",
            success_title: "Dịch video thành công!",
            download_btn: "Tải Video Thành Phẩm",
            reset_btn: "Dịch Video Khác",
            error_title: "Đã xảy ra lỗi!",
            retry_btn: "Thử Lại",
            footer: "Made with <i class=\"fa-solid fa-heart\"></i> &middot; Chạy hoàn toàn trên máy local của bạn",
            url_alert: "Vui lòng nhập đường link video Bilibili.",
            status_message_init: "Đang chuẩn bị tác vụ...",
            status_connect: "Đang kết nối và tải video từ Bilibili...",
            status_speech: "Đang nhận dạng giọng nói và dịch sang tiếng Việt...",
            status_tts_gen: "Đang khởi tạo giọng đọc lồng tiếng Việt...",
            status_merge_gen: "Đang ghép giọng lồng tiếng mới vào video gốc...",
            status_complete: "Hoàn tất! Video đã sẵn sàng tải về.",
            status_error: "Có lỗi xảy ra trong quá trình xử lý.",
            url_placeholder: "https://www.bilibili.com/video/BV...",
            err_connect: "Không thể kết nối lấy trạng thái.",
            err_backend: "Mất kết nối với Server backend.",
            err_start: "Không thể bắt đầu tác vụ.",
            err_status_api: "Không thể kết nối lấy trạng thái."
        },
        en: {
            subtitle: "Automatic Bilibili video translation & dubbing powered by AI",
            config_title: "Project Configuration",
            url_label: "Bilibili / YouTube Video Link",
            voice_label: "Dubbing Voice",
            opt_voice_tiktok: "Lively Girl (TikTok style - Fast, cheerful) 🌟",
            opt_voice_gentle: "Gentle Girl (Expressive, sweet)",
            opt_voice_warm: "Warm Man (Movie/Documentary narration)",
            opt_voice_fast: "Energetic Man (Fast, confident)",
            lang_label: "Source Language",
            opt_lang_zh: "Chinese (Simplified)",
            opt_lang_en: "English",
            opt_lang_ja: "Japanese",
            opt_lang_ko: "Korean",
            volume_title: "Volume Adjustment",
            tts_vol_label: "Dubbed Voice (TTS)",
            bg_vol_label: "Original Audio/Background Music",
            advanced_title: "Advanced Settings",
            cookie_label: "Bilibili Cookie (SESSDATA)",
            cookie_desc: "Enter the SESSDATA value from Bilibili's Cookie to fix download errors (HTTP 412).",
            cookie_placeholder: "SESSDATA=xxxxxx; or paste the full Cookie string from your browser...",
            start_btn: "Start Dubbing & Translation",
            status_title: "Processing Status",
            idle_tip: "Enter a video link and click \"Start\" to launch the process.",
            badge_processing: "Processing",
            step_download: "Download Video & Extract Audio",
            step_translate: "Speech Recognition & Translation",
            step_tts: "Generate Dubbed Voice",
            step_merge: "Merge & Export Final Video",
            success_title: "Video Translated Successfully!",
            download_btn: "Download Dubbed Video",
            reset_btn: "Translate Another Video",
            error_title: "An Error Occurred!",
            retry_btn: "Retry",
            footer: "Made with <i class=\"fa-solid fa-heart\"></i> &middot; Running locally on your machine",
            url_alert: "Please enter a Bilibili video link.",
            status_message_init: "Preparing task...",
            status_connect: "Connecting and downloading video from Bilibili...",
            status_speech: "Recognizing speech and translating to Vietnamese...",
            status_tts_gen: "Initializing dubbed voice...",
            status_merge_gen: "Merging dubbed audio into original video...",
            status_complete: "Finished! Video is ready for download.",
            status_error: "An error occurred during processing.",
            url_placeholder: "https://www.bilibili.com/video/BV...",
            err_connect: "Unable to retrieve status.",
            err_backend: "Lost connection to the backend server.",
            err_start: "Failed to initiate task.",
            err_status_api: "Unable to retrieve status."
        }
    };

    let currentLang = "vi";

    // DOM Elements
    const videoUrlInput = document.getElementById("video-url");
    const voiceSelect = document.getElementById("voice-select");
    const sourceLangSelect = document.getElementById("source-lang");
    const ttsVolumeInput = document.getElementById("tts-volume");
    const bgVolumeInput = document.getElementById("bg-volume");
    const ttsVolValue = document.getElementById("tts-vol-value");
    const bgVolValue = document.getElementById("bg-vol-value");
    
    // Advanced Settings & Cookie Elements
    const btnToggleAdvanced = document.getElementById("btn-toggle-advanced");
    const advancedSettingsContent = document.getElementById("advanced-settings-content");
    const bilibiliCookieInput = document.getElementById("bilibili-cookie");
    
    // Language buttons
    const btnLangVi = document.getElementById("btn-lang-vi");
    const btnLangEn = document.getElementById("btn-lang-en");
    
    // Main action buttons
    const startBtn = document.getElementById("start-btn");
    const resetBtn = document.getElementById("reset-btn");
    const retryBtn = document.getElementById("retry-btn");
    const downloadBtn = document.getElementById("download-btn");
    
    // State Containers
    const stateIdle = document.getElementById("state-idle");
    const stateProcessing = document.getElementById("state-processing");
    const stateSuccess = document.getElementById("state-success");
    const stateError = document.getElementById("state-error");
    
    // Progress Indicators
    const progressBar = document.getElementById("progress-bar");
    const progressPercent = document.getElementById("progress-percent");
    const statusMessage = document.getElementById("status-message");
    const videoPreview = document.getElementById("video-preview");
    const errorMessage = document.getElementById("error-message");
    
    // Steps timeline
    const stepDownload = document.getElementById("step-download");
    const stepTranslate = document.getElementById("step-translate");
    const stepTts = document.getElementById("step-tts");
    const stepMerge = document.getElementById("step-merge");

    let processingInterval = null;
    let currentTaskId = null;
    let currentMode = "local"; // Default to offline Whisper Local

    // 1. Language Toggle Logic
    function setLanguage(lang) {
        currentLang = lang;
        localStorage.setItem("app_lang", lang);

        if (lang === "vi") {
            btnLangVi.classList.add("active");
            btnLangEn.classList.remove("active");
        } else {
            btnLangEn.classList.add("active");
            btnLangVi.classList.remove("active");
        }

        const t = TRANSLATIONS[lang];

        // Helper function to safely set text content
        const safeSetText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        // Translate HTML text nodes safely
        safeSetText("i18n-subtitle", t.subtitle);
        safeSetText("i18n-config-title", t.config_title);
        safeSetText("i18n-url-label", t.url_label);
        safeSetText("i18n-voice-label", t.voice_label);
        
        safeSetText("opt-voice-tiktok", t.opt_voice_tiktok);
        safeSetText("opt-voice-gentle", t.opt_voice_gentle);
        safeSetText("opt-voice-warm", t.opt_voice_warm);
        safeSetText("opt-voice-fast", t.opt_voice_fast);

        safeSetText("i18n-lang-label", t.lang_label);
        safeSetText("opt-lang-zh", t.opt_lang_zh);
        safeSetText("opt-lang-en", t.opt_lang_en);
        safeSetText("opt-lang-ja", t.opt_lang_ja);
        safeSetText("opt-lang-ko", t.opt_lang_ko);

        if (videoUrlInput) videoUrlInput.placeholder = t.url_placeholder;

        safeSetText("i18n-volume-title", t.volume_title);
        safeSetText("i18n-tts-vol-label", t.tts_vol_label);
        safeSetText("i18n-bg-vol-label", t.bg_vol_label);
        
        // Translate advanced settings
        safeSetText("i18n-advanced-title", t.advanced_title);
        safeSetText("i18n-cookie-label", t.cookie_label);
        safeSetText("i18n-cookie-desc", t.cookie_desc);
        if (bilibiliCookieInput) bilibiliCookieInput.placeholder = t.cookie_placeholder;
        
        safeSetText("i18n-start-btn", t.start_btn);
        safeSetText("i18n-status-title", t.status_title);
        safeSetText("i18n-idle-tip", t.idle_tip);
        
        safeSetText("status-badge", t.badge_processing);
        
        safeSetText("i18n-step-download", t.step_download);
        safeSetText("i18n-step-translate", t.step_translate);
        safeSetText("i18n-step-tts", t.step_tts);
        safeSetText("i18n-step-merge", t.step_merge);
        
        safeSetText("i18n-success-title", t.success_title);
        safeSetText("i18n-download-btn", t.download_btn);
        safeSetText("i18n-reset-btn", t.reset_btn);
        
        safeSetText("i18n-error-title", t.error_title);
        safeSetText("i18n-retry-btn", t.retry_btn);
        
        const footer = document.getElementById("i18n-footer");
        if (footer) footer.innerHTML = t.footer;
    }

    btnLangVi.addEventListener("click", () => setLanguage("vi"));
    btnLangEn.addEventListener("click", () => setLanguage("en"));

    // Set initial language from storage
    const savedLang = localStorage.getItem("app_lang") || "vi";
    setLanguage(savedLang);

    // Running in offline Whisper Local mode.

    // Toggle advanced settings accordion
    btnToggleAdvanced.addEventListener("click", () => {
        btnToggleAdvanced.classList.toggle("active");
        advancedSettingsContent.classList.toggle("d-none");
    });

    // Load and save Bilibili Cookie
    const savedCookie = localStorage.getItem("bilibili_cookie");
    if (savedCookie) {
        bilibiliCookieInput.value = savedCookie;
    }
    bilibiliCookieInput.addEventListener("input", (e) => {
        localStorage.setItem("bilibili_cookie", e.target.value.trim());
    });

    // 5. Update Volume Slider Indicators
    ttsVolumeInput.addEventListener("input", (e) => {
        ttsVolValue.textContent = `${Math.round(e.target.value * 100)}%`;
    });

    bgVolumeInput.addEventListener("input", (e) => {
        bgVolValue.textContent = `${Math.round(e.target.value * 100)}%`;
    });

    // 6. Change UI States
    function showState(state) {
        stateIdle.classList.add("d-none");
        stateProcessing.classList.add("d-none");
        stateSuccess.classList.add("d-none");
        stateError.classList.add("d-none");

        if (state === "idle") {
            stateIdle.classList.remove("d-none");
            startBtn.removeAttribute("disabled");
        } else if (state === "processing") {
            stateProcessing.classList.remove("d-none");
            startBtn.setAttribute("disabled", "true");
        } else if (state === "success") {
            stateSuccess.classList.remove("d-none");
            startBtn.removeAttribute("disabled");
        } else if (state === "error") {
            stateError.classList.remove("d-none");
            startBtn.removeAttribute("disabled");
        }
    }

    // 7. Reset Timeline Visuals
    function resetTimeline() {
        [stepDownload, stepTranslate, stepTts, stepMerge].forEach(step => {
            step.classList.remove("active", "completed");
            step.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-circle-dot"></i>';
        });
        progressBar.style.width = "0%";
        progressPercent.textContent = "0%";
    }

    // Translate backend status messages dynamically if EN is selected
    function translateBackendMessage(message) {
        if (currentLang === "vi") return message;
        
        const te = TRANSLATIONS.en;
        
        if (message.includes("Đang kết nối và tải video")) return te.status_connect;
        if (message.includes("Đang tải video...")) {
            const match = message.match(/\((\d+\.\d+)\%\)/);
            if (match) {
                return `Downloading video... (${match[1]}%)`;
            }
            return "Downloading video...";
        }
        if (message.includes("Đang nhận dạng giọng nói")) return te.status_speech;
        if (message.includes("Đang khởi tạo giọng đọc")) return te.status_tts_gen;
        if (message.includes("Đang ghép giọng lồng tiếng")) return te.status_merge_gen;
        if (message.includes("Hoàn tất")) return te.status_complete;
        if (message.includes("Đang chuẩn bị tác vụ")) return te.status_message_init;
        if (message.includes("Có lỗi xảy ra")) return te.status_error;
        
        return message;
    }

    // 8. Update Timeline visual state
    function updateTimeline(status, progress, message) {
        progressBar.style.width = `${progress}%`;
        progressPercent.textContent = `${progress}%`;
        statusMessage.textContent = translateBackendMessage(message);

        resetTimeline();

        if (status === "downloading") {
            stepDownload.classList.add("active");
        } else if (status === "translating") {
            stepDownload.classList.add("completed");
            stepDownload.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-check"></i>';
            stepTranslate.classList.add("active");
        } else if (status === "tts") {
            stepDownload.classList.add("completed");
            stepDownload.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-check"></i>';
            stepTranslate.classList.add("completed");
            stepTranslate.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-check"></i>';
            stepTts.classList.add("active");
        } else if (status === "merging") {
            stepDownload.classList.add("completed");
            stepDownload.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-check"></i>';
            stepTranslate.classList.add("completed");
            stepTranslate.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-check"></i>';
            stepTts.classList.add("completed");
            stepTts.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-check"></i>';
            stepMerge.classList.add("active");
        } else if (status === "completed") {
            [stepDownload, stepTranslate, stepTts, stepMerge].forEach(step => {
                step.classList.add("completed");
                step.querySelector(".step-indicator").innerHTML = '<i class="fa-solid fa-check"></i>';
            });
        }
    }

    // 9. Poll Status Endpoint
    function pollTaskStatus(taskId) {
        processingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${taskId}`);
                if (!response.ok) {
                    throw new Error(TRANSLATIONS[currentLang].err_status_api);
                }
                const data = await response.json();

                updateTimeline(data.status, data.progress, data.message);

                if (data.status === "completed") {
                    clearInterval(processingInterval);
                    videoPreview.src = data.video_url;
                    downloadBtn.href = data.video_url;
                    showState("success");
                } else if (data.status === "failed") {
                    clearInterval(processingInterval);
                    errorMessage.textContent = data.error || TRANSLATIONS[currentLang].status_error;
                    showState("error");
                }
            } catch (err) {
                console.error("Lỗi polling:", err);
                clearInterval(processingInterval);
                errorMessage.textContent = TRANSLATIONS[currentLang].err_backend;
                showState("error");
            }
        }, 1000);
    }

    // 10. Start Processing Button Click
    async function startProcessing() {
        const url = videoUrlInput.value.trim();
        if (!url) {
            alert(TRANSLATIONS[currentLang].url_alert);
            videoUrlInput.focus();
            return;
        }

        const voice = voiceSelect.value;
        const sourceLang = sourceLangSelect.value;
        const ttsVolume = parseFloat(ttsVolumeInput.value);
        const bgVolume = parseFloat(bgVolumeInput.value);
        const bilibiliCookie = bilibiliCookieInput.value.trim();

        resetTimeline();
        showState("processing");

        try {
            const response = await fetch("/api/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    url: url,
                    voice: voice,
                    source_lang: sourceLang,
                    bg_volume: bgVolume,
                    tts_volume: ttsVolume,
                    bilibili_cookie: bilibiliCookie
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || TRANSLATIONS[currentLang].err_start);
            }

            const data = await response.json();
            currentTaskId = data.task_id;
            
            // Start polling progress
            pollTaskStatus(currentTaskId);

        } catch (err) {
            errorMessage.textContent = err.message;
            showState("error");
        }
    }

    // Event Listeners
    startBtn.addEventListener("click", startProcessing);
    
    resetBtn.addEventListener("click", () => {
        videoUrlInput.value = "";
        showState("idle");
    });
    
    retryBtn.addEventListener("click", () => {
        showState("idle");
    });
});
