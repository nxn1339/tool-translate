import os
import re
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for Whisper model to avoid reloading from disk on each request
_cached_whisper_model = None
_cached_whisper_device = None


def get_whisper_model():
    """
    Returns a cached instance of the Whisper model, loading it into memory once.
    Automatically detects and prioritizes CUDA GPU acceleration if available.
    """
    global _cached_whisper_model, _cached_whisper_device
    if _cached_whisper_model is not None:
        return _cached_whisper_model, _cached_whisper_device

    try:
        import whisper
        import torch
    except ImportError as e:
        raise ImportError(f"Required library missing: {e}. Please install openai-whisper and torch.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading Whisper 'base' model on device: {device.upper()}...")
    _cached_whisper_device = device
    _cached_whisper_model = whisper.load_model("base", device=device)
    logger.info(f"Whisper model loaded and cached on {device.upper()} successfully.")
    return _cached_whisper_model, _cached_whisper_device


# ==============================================================================
# STAGE 0: EXTERNAL GLOSSARY LOADER (app/data/zh_vi_glossary.json)
# ==============================================================================

GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "data", "zh_vi_glossary.json")


def load_zh_vi_glossary() -> Dict[str, Any]:
    if os.path.exists(GLOSSARY_PATH):
        try:
            with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load glossary from {GLOSSARY_PATH}: {e}")
    return {}


# ==============================================================================
# STAGE 1: CHINESE OCR TYPO CORRECTION & CONTEXT PRE-PROCESSING
# ==============================================================================

OCR_ZH_TYPO_FIXES: List[Tuple[str, str]] = [
    ("盖涩", "羞涩"),
    ("彼止", "彼此"),
    ("白清晨", "白清臣"),
    ("暖味", "暧昧"),
    ("入费豪门", "入赘豪门"),
    ("入费", "入赘"),
    ("一成为了", "一跃成为了"),
    ("一成为", "一跃成为"),
    ("偶遇了", "偶遇"),
    ("青梅竹马定下了娃娃亲", "青梅竹马订下了从小指腹为婚的婚约"),
    ("定下了娃娃亲", "订下了从小指腹为婚的婚约"),
    ("定了娃娃亲", "订了从小指腹为婚的婚约"),
    ("呕心沥血", "竭尽心血"),
    ("皇子弟弟们", "各位皇弟"),
    ("皇子弟弟", "皇弟"),
    ("穿越到古代", "穿越时空回到古代"),
    ("转世穿越到", "转世重生来到"),
]

FEMALE_CONTEXT_KEYWORDS = (
    "女总裁", "女医生", "校花", "美女", "老婆", "妻子", "圣女", "公主",
    "王妃", "姑娘", "小姐", "姐姐", "妹妹", "师姐", "师妹", "女神",
    "红颜", "青梅竹马", "秘书", "未婚妻", "女友", "女朋友", "妈妈", "母亲", "妇人", "女帝", "妖女"
)

STUDIO_WATERMARK_RE = re.compile(
    r'[\u4e00-\u9fffA-Za-z0-9]{1,6}(?:动画|动漫|剧场|影视|解说|出品|制作|工作室|字幕组|汉化组)$'
)


def preprocess_chinese_segments(
    texts: List[str],
    inline_hanviet: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Cleans OCR noise, fixes homograph typos, normalizes 1-char OCR character name variants across the script,
    and resolves pronoun gender ('他' -> '她') across consecutive lines.
    If inline_hanviet=True (used only for basic Google GTX word-by-word fallback), replaces proper nouns inline.
    For AI engines (Groq/Gemini), inline_hanviet=False preserves 100% pure Chinese sentences so LLMs never suffer
    from mixed-language context corruption.
    Returns (cleaned_display_zh, translator_ready_zh).
    """
    glossary = load_zh_vi_glossary()
    ext_typos: Dict[str, str] = glossary.get("ocr_typo_fixes", {})
    char_names: Dict[str, str] = glossary.get("character_names_zh_vi", {})

    cleaned_zh_list: List[str] = []
    for raw in texts:
        t = (raw or "").strip()
        parts = t.split()
        if len(parts) > 1:
            parts = [p for p in parts if not STUDIO_WATERMARK_RE.search(p)]
            t = " ".join(parts).strip()

        for bad_zh, good_zh in ext_typos.items():
            if bad_zh in t:
                t = t.replace(bad_zh, good_zh)

        t = t.replace("暖味", "暧昧").replace("入费豪门", "入赘豪门")
        if t.startswith("一成为"):
            t = "一跃" + t[1:]
        cleaned_zh_list.append(t)

    # Auto-normalize 1-char OCR homograph variants of recurring 3-char character names across the whole script
    try:
        from app.hanviet import normalize_ocr_character_names
        cleaned_zh_list, _ = normalize_ocr_character_names(cleaned_zh_list)
    except Exception as e_norm:
        logger.warning(f"normalize_ocr_character_names warning: {e_norm}")

    translator_zh_list: List[str] = []
    female_context_ttl = 0

    # Sort character names by length descending so 3-char names match before 2-char names
    sorted_char_names = sorted(char_names.items(), key=lambda x: len(x[0]), reverse=True)

    for idx, t in enumerate(cleaned_zh_list):
        if any(kw in t for kw in FEMALE_CONTEXT_KEYWORDS):
            female_context_ttl = 2

        work_t = t
        if female_context_ttl > 0 and "他" in work_t and not any(m in work_t for m in ("他们", "其他", "他人", "男")):
            work_t = work_t.replace("他", "她")
        if female_context_ttl > 0:
            female_context_ttl -= 1

        for src_pat, dst_pat in OCR_ZH_TYPO_FIXES:
            if src_pat in work_t:
                work_t = work_t.replace(src_pat, dst_pat)

        if inline_hanviet:
            # Replace known Chinese proper nouns / sect names with Sino-Vietnamese directly for Google GTX
            for zh_name, vi_name in sorted_char_names:
                if zh_name in work_t:
                    work_t = work_t.replace(zh_name, f" {vi_name} ")

        work_t = re.sub(r'连生(\d+)胎', r'连续生下\1个孩子', work_t)
        work_t = re.sub(r'创造第(\d+)胎', r'生第\1个孩子', work_t)

        translator_zh_list.append(re.sub(r'\s+', ' ', work_t).strip())

    # Dynamic Sino-Vietnamese entity inline replacement ONLY when inline_hanviet=True (Google GTX fallback)
    if inline_hanviet:
        try:
            from app.hanviet import enhance_chinese_with_hanviet_entities
            translator_zh_list, _ = enhance_chinese_with_hanviet_entities(translator_zh_list)
        except Exception as e_hv:
            logger.warning(f"enhance_chinese_with_hanviet_entities warning: {e_hv}")

    return cleaned_zh_list, translator_zh_list


# ==============================================================================
# STAGE 2: VIETNAMESE DUBBING NATURALIZER & DOMAIN GLOSSARY POST-PROCESSOR
# ==============================================================================

def refine_vietnamese_dub_line(
    source_zh: str,
    raw_vi: str,
    duration: float = 2.0,
    is_first_person: bool = True,
    is_ancient_context: bool = False
) -> str:
    """
    Post-processes machine-translated Vietnamese to:
    1. Enforce accurate Chinese-Vietnamese genre terminology (xianxia, romance, CEO, school, etc.)
    2. Fix unnatural literal translations and pronoun shifts
    3. Make phrasing concise and rhythmic so TTS matches the video duration naturally
    """
    if not raw_vi:
        return ""

    glossary = load_zh_vi_glossary()
    vi_domain_glossary = glossary.get("vi_domain_glossary", [])
    vi_concise_rules = glossary.get("vi_concise_spoken_rules", [])

    vi = raw_vi.strip()
    vi = re.sub(r'^\s*(?:\[\d+\]|\(\d+\)|\d+[\.\):])\s*', '', vi).strip()

    zh_clean = source_zh.strip()
    if zh_clean == "入赘豪门":
        return "ở rể hào môn"
    if zh_clean in ("出道就是巅峰", "出道即巅峰"):
        return "vừa ra mắt đã lên đỉnh cao"
    if zh_clean == "成功飞升":
        return "phi thăng thành công"
    if zh_clean == "穿越到古代":
        return "xuyên không về cổ đại"
    if zh_clean == "转世穿越到修仙世界":
        return "chuyển sinh đến thế giới tu tiên"
    if zh_clean == "每个都是当世人杰":
        return "đứa nào cũng là kỳ tài đương thời"
    if zh_clean == "我刚满周岁":
        return "Vừa tròn một tuổi"

    # Sino-Vietnamese Pinyin replacement (e.g. 'Xue Caiyi' -> 'Tiết Thải Y', 'Bai Qingchen' -> 'Bạch Thanh Trần')
    try:
        from app.hanviet import replace_pinyin_with_hanviet
        vi = replace_pinyin_with_hanviet(zh_clean, vi)
    except Exception as e_p:
        logger.warning(f"replace_pinyin_with_hanviet error: {e_p}")

    # Specific ancient / palace / drama adjustments
    if "皇妃娘娘" in zh_clean:
        vi = re.sub(r'\bvương phi\b|\bcông chúa\b', 'Hoàng phi nương nương', vi, flags=re.IGNORECASE)
    elif "皇妃" in zh_clean:
        vi = re.sub(r'\bcông chúa\b', 'Hoàng phi', vi, flags=re.IGNORECASE)
    if "彼此的呼吸" in zh_clean or "彼止的呼吸" in zh_clean:
        vi = "Hơi thở của nhau"
    if "喷洒在对方的耳畔" in zh_clean:
        vi = "phả vào bên tai đối phương"
    if "哪个女人不喜欢" in zh_clean:
        vi = "người phụ nữ nào mà không mê"
    if "盖涩地低声娇" in zh_clean or "羞涩地低声娇" in zh_clean:
        if "Tiết Thải Y" in vi:
            vi = "Tiết Thải Y e thẹn nũng nịu thì thầm"
    if "骨头都要融化掉了" in zh_clean:
        vi = "xương cốt như muốn tan chảy"
    if "我们薛彩衣的话" in zh_clean:
        vi = "Lời của Tiết Thải Y chúng ta"
    if "薛彩衣双臂" in zh_clean:
        vi = "Hai cánh tay Tiết Thải Y"
    if "环住白清臣的脖子" in zh_clean:
        vi = "ôm trọn lấy cổ Bạch Thanh Trần"
    if "品尝着薛彩衣的香甜" in zh_clean:
        vi = "nếm trọn vị ngọt ngào của Tiết Thải Y"

    # Apply external JSON domain glossary replacements
    for item in vi_domain_glossary:
        if isinstance(item, list) and len(item) == 2:
            src_phrase, dst_phrase = item
            if src_phrase.lower() in vi.lower():
                vi = re.sub(re.escape(src_phrase), dst_phrase, vi, flags=re.IGNORECASE)

    # Source-aware terminology corrections (using Chinese source cues)
    if "总裁" in zh_clean:
        vi = re.sub(r'\b[Nn]ữ tổng thống\b', 'nữ tổng tài', vi)
        vi = re.sub(r'\b[Tt]ổng thống\b', 'tổng tài', vi)
        vi = re.sub(r'\b[Cc]hủ tịch\b', 'tổng tài', vi)
        vi = re.sub(r'\bCEO\b', 'tổng tài', vi)
    if "霸道" in zh_clean:
        vi = re.sub(r'\bhống hách\b|\bđộc đoán\b|\bbá quyền\b|\báp đảo\b', 'bá đạo', vi, flags=re.IGNORECASE)

    if "校花" in zh_clean:
        vi = re.sub(r'\bcả trường\b|\btoàn trường\b|\bhoa trường\b|\bhoa khôi của trường\b', 'hoa khôi trường', vi, flags=re.IGNORECASE)
        if "hoa khôi" not in vi.lower():
            vi = re.sub(r'trường học', 'hoa khôi trường', vi, flags=re.IGNORECASE)

    if "红颜知己" in zh_clean:
        vi = re.sub(r'người bạn tâm giao(?: của tôi)?|bạn tri kỷ(?: của tôi)?', 'hồng nhan tri kỷ', vi, flags=re.IGNORECASE)

    if "青梅竹马" in zh_clean:
        vi = re.sub(r'Qingmei Bamboo Horse|ngựa tre xanh|thanh mai trúc mã của mình', 'thanh mai trúc mã', vi, flags=re.IGNORECASE)
        if "娃娃亲" in zh_clean:
            vi = "đã định hôn ước từ nhỏ với thanh mai trúc mã"

    if "暧昧" in zh_clean or "暖味" in zh_clean:
        vi = re.sub(r'sự ấm áp|hương vị ấm áp|sự mập mờ', 'lời tán tỉnh', vi, flags=re.IGNORECASE)
        if "拒绝" in zh_clean and "为我" in zh_clean:
            vi = "còn vì tôi mà từ chối mọi lời tán tỉnh"

    if "豪门" in zh_clean:
        vi = re.sub(r'gia đình giàu có|gia tộc giàu có|cửa sang trọng.*', 'hào môn', vi, flags=re.IGNORECASE)
        if "入赘" in zh_clean or "入费" in zh_clean:
            vi = "ở rể hào môn"

    if "星探" in zh_clean:
        vi = re.sub(r'các ngôi sao|nhà thám hiểm ngôi sao|người tìm kiếm tài năng', 'người săn ngôi sao', vi, flags=re.IGNORECASE)

    if "一跃成为" in zh_clean or "一成为" in zh_clean:
        vi = re.sub(r'^[Mm]ột khi bạn trở thành|[Bb]ước một bước trở thành|[Nn]hảy vọt trở thành', 'Một bước trở thành', vi)

    if "呕心沥血" in zh_clean:
        vi = re.sub(r'trở nên chán ghét và|nôn ra máu và|dốc toàn lực để', 'dốc hết tâm huyết', vi, flags=re.IGNORECASE)

    if "皇子弟弟" in zh_clean or "皇弟" in zh_clean:
        vi = re.sub(r'các đệ tử của hoàng tử|những người em trai hoàng tử|các anh em hoàng tử', 'các hoàng đệ', vi, flags=re.IGNORECASE)

    if "修仙" in zh_clean:
        vi = re.sub(r'tu luyện bất tử|tu luyện trường sinh|thế giới bất tử', 'tu tiên', vi, flags=re.IGNORECASE)
        if "修仙世界" in zh_clean and "thế giới tu tiên" not in vi.lower():
            vi = re.sub(r'tu tiên', 'thế giới tu tiên', vi, flags=re.IGNORECASE)

    if "双修" in zh_clean:
        vi = re.sub(r'tu luyện sinh đôi|tu luyện đôi|cùng tu luyện', 'song tu', vi, flags=re.IGNORECASE)

    if "圣女" in zh_clean:
        vi = re.sub(r'Sect Saintess|Saintess|nữ thánh của giáo phái|thánh nữ của giáo phái|thánh nữ môn phái', 'Thánh nữ tông môn', vi, flags=re.IGNORECASE)
        if "宗门圣女" in zh_clean and "song tu" in vi.lower():
            m_age = re.match(r'^(\d+)\s*岁', zh_clean)
            if m_age:
                vi = f"{m_age.group(1)} tuổi song tu cùng Thánh nữ tông môn"

    if "仙界" in zh_clean:
        vi = re.sub(r'thế giới bất tử|cõi bất tử|thế giới thần tiên', 'tiên giới', vi, flags=re.IGNORECASE)

    if "飞升" in zh_clean:
        vi = re.sub(r'thăng thiên|bay lên trời|lên thẳng', 'phi thăng', vi, flags=re.IGNORECASE)

    if "公敌" in zh_clean and "男性" in zh_clean:
        vi = "trở thành kẻ thù chung của mọi đàn ông"

    if "产房女医生" in zh_clean and "求爱" in zh_clean:
        vi = "Nữ bác sĩ phòng sinh tỏ tình ngay tại chỗ"

    # Spoken Vietnamese rhythm & conciseness cleanup
    compact_rules = [
        (r'^Khi tôi mới sinh ra,\s*vì tôi quá đẹp trai.*', 'Vừa sinh ra vì quá đẹp trai'),
        (r'^Khi tôi được sinh ra,\s*vì tôi quá đẹp trai.*', 'Vừa sinh ra vì quá đẹp trai'),
        (r'^Vừa mới sinh ra đã vì quá đẹp trai.*', 'Vừa sinh ra vì quá đẹp trai'),
        (r'^Khi tôi (\d+) tuổi,\s*tôi đã tình cờ gặp\b', r'Năm \1 tuổi, tình cờ gặp'),
        (r'^Khi tôi (\d+) tuổi,\s*tôi tình cờ gặp\b', r'Năm \1 tuổi, tình cờ gặp'),
        (r'^Khi tôi (\d+) tuổi,\s*tôi đã\b', r'Năm \1 tuổi, tôi'),
        (r'^Khi tôi (\d+) tuổi,\s*tôi được\b', r'Năm \1 tuổi, được'),
        (r'^Khi tôi (\d+) tuổi,\s*', r'Năm \1 tuổi, '),
        (r'\bVào năm (\d+) tuổi,\s*', r'Năm \1 tuổi, '),
        (r'\bcủa ngành công nghiệp giải trí\b', 'giới giải trí'),
        (r'\bngành công nghiệp giải trí\b', 'giới giải trí'),
        (r'\bvà sau đó kết hôn với cô ấy\b', 'rồi kết hôn với cô ấy'),
        (r'\bvà sau đó kết hôn với anh ta\b', 'rồi kết hôn với cô ấy'),
        (r'\bBị vợ của một nữ tổng tài phản bội\b', 'Bị cô vợ tổng tài phản bội'),
        (r'\bBị người vợ nữ tổng tài phản bội\b', 'Bị cô vợ tổng tài phản bội'),
        (r'\bcông ty niêm yết của riêng mình\b', 'công ty niêm yết riêng'),
        (r'\bcông ty đại chúng của riêng mình\b', 'công ty niêm yết riêng'),
        (r'\bmột cô thư ký riêng xinh đẹp\b', 'cô thư ký riêng xinh đẹp'),
        (r'\bmột cô thư ký xinh đẹp\b', 'cô thư ký riêng xinh đẹp'),
        (r'^Liên tiếp sinh hạ (\d+) người con$', r'sinh liền \1 đứa con'),
        (r'^Sinh liên tiếp (\d+) đứa con$', r'sinh liền \1 đứa con'),
        (r'^(\d+) lần sinh liên tiếp$', r'sinh liền \1 đứa con'),
        (r'\bvới người vợ thư ký của mình\b', 'cùng vợ thư ký'),
        (r'\bvới cô vợ thư ký của mình\b', 'cùng vợ thư ký'),
        (r'\btai nạn xe hơi khủng khiếp\b', 'tai nạn xe thảm khốc'),
        (r'\bmột vụ tai nạn xe hơi bi thảm\b', 'tai nạn xe thảm khốc'),
        (r'\bSống một cuộc sống thảnh thơi\b', 'Sống chuỗi ngày tự tại'),
        (r'\bsống một cuộc sống vô tư lự\b', 'sống chuỗi ngày tự tại'),
        (r'\btrong tiên giới với Thánh nữ\b', 'nơi tiên giới cùng Thánh nữ'),
    ]
    for pat, repl in compact_rules:
        vi = re.sub(pat, repl, vi, flags=re.IGNORECASE)

    # Cleanup known machine translation / pre-processing artifacts
    artifact_cleanups = [
        (r'\bĐó Cá\b', 'Ờ thì'),
        (r'\bĐó Chẩm,?\s*được rồi\b', 'Thế sao được'),
        (r'\bĐó Chẩm\b', 'Thế sao'),
        (r'\bPhòng Tử\b', 'Căn nhà'),
        (r'\bNhậm Hà Nhân\b', 'bất kỳ ai'),
        (r'\bNhậm Hà Sai\b', 'sai sót nào'),
        (r'\bNhậm Hà\b', 'bất kỳ ai'),
        (r'\bChung Vu\b', 'cuối cùng'),
        (r'\bNói Minh Thẩm Gia\b', 'Cho thấy Thẩm Gia'),
        (r'\bMinh Thẩm Gia\b', 'Thẩm Gia'),
        (r'\bThẩm Bá mẹ\b', 'Bác gái Thẩm'),
        (r'\bvé Quốc Cơ\b', 'vé máy bay về nước'),
        (r'\bvề Quốc Cơ\b', 'về nước'),
        (r'\bQuốc Cơ\b', 'máy bay'),
        (r'\bsân chim\b', 'trường đua ngựa'),
    ]
    for pat, repl in artifact_cleanups:
        vi = re.sub(pat, repl, vi, flags=re.IGNORECASE)

    if zh_clean in ("三二一", "321", "3, 2, 1", "3、2、1") and re.search(r'bốn,\s*ba,\s*hai,\s*một', vi, re.IGNORECASE):
        vi = "Ba, hai, một"

    for item in vi_concise_rules:
        if isinstance(item, list) and len(item) == 2:
            pat, repl = item
            vi = re.sub(pat, repl, vi, flags=re.IGNORECASE)

    # First-person narrative consistency: fix stray "bạn" when Chinese has no '你'
    if is_first_person and "你" not in zh_clean and "您" not in zh_clean:
        vi = re.sub(r'\bmột khi bạn\b', 'một bước', vi, flags=re.IGNORECASE)
        vi = re.sub(r'\bbạn sẽ\b', 'tôi', vi, flags=re.IGNORECASE)

    # If purely ancient/xianxia dialogue (and not modern-crossover autobiography), convert 'bạn' -> 'ngươi'
    if is_ancient_context and any(k in zh_clean for k in ("本座", "本尊", "本王", "朕", "陛下", "师尊", "老夫", "道友", "孽障")):
        vi = re.sub(r'\bbạn\b', 'ngươi', vi, flags=re.IGNORECASE)

    # Fallback: if a translated line still contains any Chinese characters (e.g. 'Thẩm毅 chuyển đi' or untranslated terms),
    # transliterate remaining Hanzi to Sino-Vietnamese so 0% Hanzi remain on screen.
    if re.search(r'[\u4e00-\u9fff]', vi):
        try:
            from app.hanviet import transliterate_remaining_hanzi
            vi = transliterate_remaining_hanzi(vi)
        except Exception as e_tr:
            logger.warning(f"transliterate_remaining_hanzi error: {e_tr}")

    vi = re.sub(r'\s+', ' ', vi).strip()
    vi = vi.rstrip('.,;:') if len(vi) < 35 else vi
    return vi


# ==============================================================================
# STAGE 3: RELIABLE BATCH GOOGLE TRANSLATOR (NO MYMEMORY GARBAGE)
# ==============================================================================

def normalize_lang_codes(source_code: str, target_code: str) -> Tuple[str, str]:
    s_clean = source_code.strip().lower()
    t_clean = target_code.strip().lower()
    g_source = "zh-CN" if s_clean in ("zh", "zh-cn", "chinese") else ("en" if s_clean.startswith("en") else s_clean)
    g_target = "vi" if t_clean in ("vi", "vi-vn", "vietnamese") else ("en" if t_clean.startswith("en") else t_clean)
    return g_source, g_target


def _raw_translate_query(text: str, g_source: str, g_target: str) -> Optional[str]:
    """
    Translates text with multi-layer fallback:
    1. Google Translate API (client=gtx) - fast, free, bypasses deep-translator web scraper 429 rate limit
    2. deep_translator GoogleTranslator
    3. MyMemoryTranslator as last resort
    """
    if not text or not text.strip():
        return ""

    import urllib.request
    import urllib.parse
    import json

    # 1. Google Translate gtx API endpoint
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={g_source}&tl={g_target}&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "*/*"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and data[0]:
                translated = "".join([part[0] for part in data[0] if part and part[0]]).strip()
                if translated:
                    return translated
    except Exception as e_gtx:
        logger.warning(f"Google gtx translate failed: {e_gtx}")

    # 2. deep_translator GoogleTranslator
    try:
        from deep_translator import GoogleTranslator
        res = GoogleTranslator(source=g_source, target=g_target).translate(text)
        if res and res.strip():
            return res.strip()
    except Exception as e_dt:
        logger.warning(f"deep_translator GoogleTranslator failed: {e_dt}")

    # 3. MyMemoryTranslator fallback
    try:
        from deep_translator import MyMemoryTranslator
        res = MyMemoryTranslator(source=g_source, target=g_target).translate(text)
        if res and res.strip():
            return res.strip()
    except Exception as e_mm:
        logger.warning(f"MyMemoryTranslator fallback failed: {e_mm}")

    return None


def batch_translate_texts(
    texts: List[str],
    source_code: str = "zh-CN",
    target_code: str = "vi",
    batch_size: int = 12,
    durations: Optional[List[float]] = None
) -> List[str]:
    """
    Translates a list of subtitle texts with:
    1. Pre-translation Chinese OCR typo, proper noun & gender context normalization
    2. Indexed batching via Google GTX API (prevents line merging and completely avoids rate limits)
    3. Post-translation Vietnamese dubbing naturalization & conciseness optimization
    """
    if not texts:
        return []

    g_source, g_target = normalize_lang_codes(source_code, target_code)

    from app.gemini_translator import load_settings
    settings = load_settings()
    active_engine = settings.get("translation_engine", "groq")

    is_chinese = g_source.startswith("zh")
    use_inline_hv = (active_engine == "google")
    if is_chinese:
        cleaned_zh, translator_zh = preprocess_chinese_segments(texts, inline_hanviet=use_inline_hv)
    else:
        cleaned_zh = [t.strip() for t in texts]
        translator_zh = list(cleaned_zh)

    raw_translated: List[str] = []

    # Priority 1: Groq High-Speed AI Translation Engine (Llama 3.3 70B)
    if active_engine == "groq" and settings.get("groq_api_key"):
        try:
            from app.groq_translator import groq_batch_translate
            logger.info("Translating with Groq Cloud AI engine (Llama 3.3 70B)...")
            groq_res, groq_failed = groq_batch_translate(
                translator_zh,
                source_code=g_source,
                target_code=g_target,
                durations=durations
            )
            raw_translated = groq_res
            logger.info(f"Groq AI translated {len(raw_translated) - len(groq_failed)}/{len(raw_translated)} lines successfully.")
        except Exception as e_groq:
            logger.error(f"Groq translation engine error: {e_groq}")
            raw_translated = [""] * len(translator_zh)

    # Priority 2: Gemini Contextual AI Translation Engine
    elif active_engine == "gemini" and settings.get("gemini_api_key"):
        try:
            from app.gemini_translator import gemini_batch_translate
            logger.info("Translating with Gemini Contextual AI engine...")
            gemini_res = gemini_batch_translate(translator_zh, source_code=g_source, target_code=g_target)
            if gemini_res:
                raw_translated = gemini_res
                logger.info(f"Gemini AI translated {len(raw_translated)} lines successfully.")
            else:
                logger.warning("Gemini translation returned empty/incomplete results.")
                raw_translated = [""] * len(translator_zh)
        except Exception as e_gem:
            logger.error(f"Gemini translation engine error: {e_gem}")
            raw_translated = [""] * len(translator_zh)

    # Priority 3: Google GTX batch translation (Only if explicitly selected as Google engine)
    elif active_engine == "google":
        logger.info("Translating with Google GTX engine...")
        for i in range(0, len(translator_zh), batch_size):
            chunk = translator_zh[i:i + batch_size]
            numbered_lines = [f"[{idx + 1}] {line}" for idx, line in enumerate(chunk)]
            joined_text = "\n".join(numbered_lines)
            chunk_map: Dict[int, str] = {}

            try:
                res = _raw_translate_query(joined_text, g_source, g_target)
                if res:
                    matches = re.findall(r'\[(\d+)\]\s*([^\n\[]+)', res)
                    for m_idx_str, m_text in matches:
                        m_idx = int(m_idx_str) - 1
                        if 0 <= m_idx < len(chunk) and m_text.strip():
                            chunk_map[m_idx] = m_text.strip()

                    if len(chunk_map) < len(chunk):
                        split_lines = [ln.strip() for ln in res.split("\n") if ln.strip()]
                        if len(split_lines) == len(chunk):
                            for idx_ln, ln in enumerate(split_lines):
                                clean_ln = re.sub(r'^\[\d+\]\s*', '', ln).strip()
                                if clean_ln:
                                    chunk_map[idx_ln] = clean_ln
            except Exception as e:
                logger.warning(f"Indexed batch translation warning on chunk {i // batch_size + 1}: {e}")

            for idx_in_chunk, item_text in enumerate(chunk):
                if idx_in_chunk in chunk_map and chunk_map[idx_in_chunk]:
                    raw_translated.append(chunk_map[idx_in_chunk])
                    continue

                if not item_text.strip():
                    raw_translated.append("")
                    continue

                single_res = None
                for attempt in range(2):
                    single_res = _raw_translate_query(item_text, g_source, g_target)
                    if single_res:
                        break
                    time.sleep(0.2)

                raw_translated.append(single_res if single_res else "")
    else:
        # No valid configured engine
        logger.warning(f"No valid API key or unknown engine '{active_engine}'. Subtitles left untranslated.")
        raw_translated = [""] * len(translator_zh)

    first_person_count = sum(1 for t in cleaned_zh if "我" in t)
    is_first_person = first_person_count >= max(1, len(cleaned_zh) // 6)

    glossary = load_zh_vi_glossary()
    ancient_kws = glossary.get("ancient_keywords", [])
    ancient_hits = sum(1 for t in cleaned_zh if any(k in t for k in ancient_kws))
    is_ancient_context = ancient_hits >= 2

    final_translations: List[str] = []
    for idx, (orig_zh, raw_vi) in enumerate(zip(cleaned_zh, raw_translated)):
        dur = durations[idx] if (durations and idx < len(durations)) else 2.0
        if not raw_vi or not raw_vi.strip():
            final_translations.append("")
            continue

        if is_chinese and g_target == "vi":
            refined = refine_vietnamese_dub_line(
                orig_zh,
                raw_vi,
                duration=dur,
                is_first_person=is_first_person,
                is_ancient_context=is_ancient_context
            )
        else:
            refined = re.sub(r'^\s*\[\d+\]\s*', '', raw_vi).strip()
        final_translations.append(refined)

    return final_translations


# ==============================================================================
# STAGE 4: SRT EXPORT & IMPORT ENGINE (CHINESE / VIETNAMESE / DUAL)
# ==============================================================================

def _sec_to_srt_ts(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _srt_ts_to_sec(ts_str: str) -> float:
    ts_clean = ts_str.strip().replace(",", ".")
    parts = ts_clean.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(ts_clean)


def export_segments_to_srt_string(segments: List[Dict[str, Any]], lang: str = "zh") -> str:
    """
    Exports segments into standard SubRip (.srt) format string.
    - lang="zh": exports original Chinese (`text`)
    - lang="vi": exports Vietnamese translation (`translation`)
    - lang="dual": exports Chinese on line 1 and Vietnamese on line 2
    """
    blocks: List[str] = []
    for idx, seg in enumerate(segments):
        start_ts = _sec_to_srt_ts(seg.get("start", 0.0))
        end_ts = _sec_to_srt_ts(seg.get("end", 0.0))
        zh_text = (seg.get("text") or "").strip()
        vi_text = (seg.get("translation") or "").strip()

        if lang == "zh":
            content = zh_text or vi_text
        elif lang == "dual":
            content = f"{zh_text}\n{vi_text}" if (zh_text and vi_text) else (vi_text or zh_text)
        else:
            content = vi_text or zh_text

        blocks.append(f"{idx + 1}\n{start_ts} --> {end_ts}\n{content}\n")

    return "\n".join(blocks)


def _clear_stale_translation_flags(
    segments: List[Dict[str, Any]],
    target_field: str
) -> List[Dict[str, Any]]:
    """Removes error flags left over from a previous translation run after importing new translations."""
    if target_field != "translation":
        return segments
    for seg in segments:
        seg.pop("translation_error", None)
        seg.pop("untranslated_warning", None)
        seg.pop("untranslated_chars", None)
    return segments


def import_srt_to_segments(
    srt_content: str,
    existing_segments: Optional[List[Dict[str, Any]]] = None,
    target_field: str = "translation"
) -> List[Dict[str, Any]]:
    """
    Parses an uploaded .SRT file (or pasted numbered/plain lines) and merges into project segments.
    Supports:
    1. Standard SubRip (.srt) blocks with `HH:MM:SS,mmm --> HH:MM:SS,mmm`
    2. Plain or numbered lines (`[1] ...`, `1. ...`, or one line per segment)
    Automatically invalidates `tts_raw_hash` on modified segments so TTS regenerates cleanly.
    """
    raw = (srt_content or "").replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").strip()
    if not raw:
        return existing_segments or []

    existing = list(existing_segments) if existing_segments else []

    # Detect standard SRT timecode lines
    timecode_pattern = re.compile(
        r'(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3}|\d{1,2}:\d{2}[,\.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3}|\d{1,2}:\d{2}[,\.]\d{1,3})'
    )

    parsed_blocks: List[Dict[str, Any]] = []
    if timecode_pattern.search(raw):
        # Split by blank lines or before index+timecode
        lines = raw.split("\n")
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Optional numeric index line before timecode
            tc_match = timecode_pattern.search(line)
            if not tc_match and (i + 1 < n):
                next_tc = timecode_pattern.search(lines[i + 1].strip())
                if next_tc and re.match(r'^\d+$', line):
                    i += 1
                    tc_match = next_tc

            if tc_match:
                start_sec = round(_srt_ts_to_sec(tc_match.group(1)), 2)
                end_sec = round(_srt_ts_to_sec(tc_match.group(2)), 2)
                if end_sec <= start_sec:
                    end_sec = round(start_sec + 1.0, 2)
                i += 1
                text_lines: List[str] = []
                while i < n and lines[i].strip() != "":
                    # Stop if next block starts without an empty line
                    if re.match(r'^\d+$', lines[i].strip()) and (i + 1 < n) and timecode_pattern.search(lines[i + 1].strip()):
                        break
                    if timecode_pattern.search(lines[i].strip()):
                        break
                    text_lines.append(lines[i].strip())
                    i += 1
                block_text = " ".join(text_lines).strip()
                parsed_blocks.append({
                    "start": start_sec,
                    "end": end_sec,
                    "content": block_text
                })
            else:
                i += 1

    # Case 1: Parsed standard SRT blocks
    if parsed_blocks:
        # 1a: Exact same count as existing segments -> 1-to-1 mapping preserving Chinese text
        if existing and len(parsed_blocks) == len(existing):
            updated_list: List[Dict[str, Any]] = []
            for idx, (old_seg, blk) in enumerate(zip(existing, parsed_blocks)):
                new_seg = dict(old_seg)
                new_seg["id"] = idx + 1
                new_seg["start"] = blk["start"]
                new_seg["end"] = blk["end"]
                old_val = (new_seg.get(target_field) or "").strip()
                new_val = blk["content"]
                new_seg[target_field] = new_val
                if target_field == "translation" and new_val != old_val:
                    new_seg.pop("tts_raw_hash", None)
                updated_list.append(new_seg)
            return _clear_stale_translation_flags(updated_list, target_field)

        # 1b: Different block count -> match each block to closest existing segment by timestamp overlap
        updated_list = []
        for idx, blk in enumerate(parsed_blocks):
            matched_old: Optional[Dict[str, Any]] = None
            best_dist = 999999.0
            for old_seg in existing:
                dist = abs(float(old_seg.get("start", 0.0)) - blk["start"])
                if dist < best_dist and dist <= 1.2:
                    best_dist = dist
                    matched_old = old_seg

            if matched_old:
                new_seg = dict(matched_old)
                new_seg["id"] = idx + 1
                new_seg["start"] = blk["start"]
                new_seg["end"] = blk["end"]
                old_val = (new_seg.get(target_field) or "").strip()
                new_seg[target_field] = blk["content"]
                if target_field == "translation" and blk["content"] != old_val:
                    new_seg.pop("tts_raw_hash", None)
            else:
                new_seg = {
                    "id": idx + 1,
                    "start": blk["start"],
                    "end": blk["end"],
                    "text": blk["content"] if target_field == "text" else "",
                    "translation": blk["content"] if target_field == "translation" else ""
                }
            updated_list.append(new_seg)
        return _clear_stale_translation_flags(updated_list, target_field)

    # Case 2: Plain lines or numbered lines ([1] ..., 1. ...) without timestamps
    plain_lines = [
        re.sub(r'^\s*(?:\[\d+\]|\(\d+\)|\d+[\.\):])\s*', '', ln).strip()
        for ln in raw.split("\n")
        if ln.strip()
    ]
    if existing and plain_lines:
        updated_list = []
        for idx, old_seg in enumerate(existing):
            new_seg = dict(old_seg)
            if idx < len(plain_lines):
                new_val = plain_lines[idx]
                old_val = (new_seg.get(target_field) or "").strip()
                new_seg[target_field] = new_val
                if target_field == "translation" and new_val != old_val:
                    new_seg.pop("tts_raw_hash", None)
            updated_list.append(new_seg)
        return _clear_stale_translation_flags(updated_list, target_field)

    return existing


def transcribe_and_translate_local(audio_path: str, source_lang_code: str = "zh") -> List[Dict[str, Any]]:
    """
    Transcribes audio using cached local Whisper model and translates in batches.
    """
    logger.info("Using cached local Whisper model for Speech-to-Text...")
    model, device = get_whisper_model()

    whisper_code = source_lang_code
    translator_code = source_lang_code
    if source_lang_code.lower() in ("zh-cn", "zh"):
        whisper_code = "zh"
        translator_code = "zh-CN"

    logger.info(f"[System] Language codes - Whisper: {whisper_code}, Translator: {translator_code}")
    logger.info(f"Transcribing audio file: {audio_path}")

    use_fp16 = (device == "cuda")
    result = model.transcribe(audio_path, language=whisper_code, fp16=use_fp16)

    raw_segments = result.get("segments", [])
    logger.info(f"Transcription finished. Transcribed {len(raw_segments)} segments.")

    valid_segments = [s for s in raw_segments if s.get("text", "").strip()]
    if not valid_segments:
        return []

    original_texts = [s["text"].strip() for s in valid_segments]
    durations = [max(0.2, float(s.get("end", 0.0)) - float(s.get("start", 0.0))) for s in valid_segments]

    if whisper_code == "zh":
        cleaned_originals, _ = preprocess_chinese_segments(original_texts)
    else:
        cleaned_originals = original_texts

    logger.info(f"Translating {len(valid_segments)} segments with dubbing naturalizer...")
    translated_texts = batch_translate_texts(
        cleaned_originals,
        source_code=translator_code,
        target_code="vi",
        durations=durations
    )

    processed_segments = []
    for seg, orig, trans in zip(valid_segments, cleaned_originals, translated_texts):
        if not orig.strip() or not trans.strip():
            continue
        processed_segments.append({
            "start": round(float(seg.get("start", 0.0)), 2),
            "end": round(float(seg.get("end", 0.0)), 2),
            "text": orig,
            "translation": trans
        })

    logger.info(f"Batch transcription and translation completed successfully ({len(processed_segments)} segments).")
    return processed_segments


def translate_video_audio(audio_path: str, source_lang: str = "Chinese") -> List[Dict[str, Any]]:
    """
    Main entry point for Whisper audio transcription & translation.
    """
    lang_map = {
        "Chinese": "zh",
        "English": "en",
        "Japanese": "ja",
        "Korean": "ko"
    }
    lang_code = lang_map.get(source_lang, "zh")
    return transcribe_and_translate_local(audio_path, lang_code)
