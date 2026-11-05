"""
Core Sino-Vietnamese (Hán - Việt) transliteration & name recognition engine.
Provides:
1. Automatic detection of Chinese proper names and titles
2. Bidirectional Hanzi <-> Hán-Việt <-> Pinyin mapping
3. Dynamic Pinyin replacement in translated Vietnamese text (e.g. 'Xue Caiyi' -> 'Tiết Thải Y')
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Set, Optional, Any

logger = logging.getLogger(__name__)

DICT_PATH = os.path.join(os.path.dirname(__file__), "data", "hanviet_dict.json")

_CACHED_HANVIET_DATA: Optional[Dict[str, Any]] = None

COMMON_ZH_VOCABULARY_STOPWORDS: Set[str] = {
    "白色", "白白", "明白", "清白", "自白", "白发", "白天", "白夜", "白开水", "白酒",
    "高兴", "高大", "高深", "高山", "高原", "高级", "高尚", "高贵", "高潮", "高压",
    "马车", "马上", "马路", "跑马", "骏马", "野马",
    "方向", "方便", "方面", "方法", "方程", "方形", "方才", "前方", "后方", "对方",
    "金钱", "金子", "金光", "黄金", "金属", "金融", "奖金", "现金", "定金",
    "地方", "地面", "地球", "土地", "田野", "田地", "农田",
    "如果", "如何", "如今", "为何", "几何", "何必", "何等", "何时", "何处",
    "因为", "因此", "为了", "以为", "认为", "成为", "作为", "行为", "人为",
    "时间", "时候", "时代", "时期", "时刻", "时常", "时而", "时机", "平时", "当时",
    "中间", "中国", "中央", "心中", "眼中", "年中", "集中", "击中", "暗中",
    "工作", "作为", "作文", "作家", "作者", "动作", "作品", "作物", "作业",
    "生活", "生气", "生死", "生命", "生长", "生产", "学生", "出生", "发生", "陌生",
    "天下", "上天", "天气", "天然", "天堂", "今天", "明天", "昨天", "春天", "夏天",
    "大家", "国家", "回家", "家人", "家庭", "家中", "家室", "玩家", "卖家", "买家",
    "发生", "发现", "发射", "发表", "发挥", "发起", "出发", "散发", "黑发", "头顶",
    "行动", "行走", "行人", "旅行", "不行", "举行", "行列", "流行", "行为",
    "本来", "日本", "原来", "本来", "本人", "本尊", "本座", "本王", "本皇",
    "可以", "可能", "可靠", "可是", "可爱", "可怕", "可惜", "可见", "以此", "以及",
    "出现", "出来", "出去", "出发", "出力", "出生", "出手", "出面", "出入", "演出",
    "进入", "进去", "进来", "入门", "入境", "入手", "收入", "加入", "投入", "沉入",
    "而且", "并且", "尚且", "暂且", "况且",
    "各个", "两人", "两个", "几个人", "一些", "一点", "一切", "一种",
    "很多", "许多", "多少", "多大", "多年", "多数",
    "常年", "常常", "经常", "通常", "正常", "日常",
    "张开", "紧张", "夸张", "铺张",
    "陈述", "陈旧", "陈列",
    "关门", "关闭", "关心", "关键", "关照", "关系",
    "谢意", "谢谢", "感谢", "凋谢",
    "钟声", "时钟", "钟表",
    "杨树", "杨柳",
    "林中", "森林", "密林", "山林",
    "江水", "长江", "江河", "江山",
    "石子", "石头", "石碑", "巨石", "飞石",
    "段落", "阶段", "手段", "片段",
    "雷电", "打雷", "雷声", "雷霆",
    "严厉", "严重", "严谨", "严密", "严格",
    "易懂", "容易", "轻易", "简易", "变易",
    "武力", "武功", "武器", "比武", "武学",
    "文采", "文明", "文化", "文字", "文学",
    # Specific stopwords to prevent false pronoun / common noun / adverb entity matches
    "任何", "任何人", "任何事", "任何东西", "任何差错", "任何人都", "任何地方", "任何情况",
    "那个", "那个人", "那些", "那时", "那里", "那儿", "那边", "那么", "那样", "那是", "那就", "那怎么行", "那怎么", "那样做", "那之后", "那之前",
    "终于", "终究", "终点", "终端", "终身", "终生", "终结", "始终", "年终", "告终",
    "房子", "房间", "房屋", "房产", "房租", "房客", "房东", "退房", "买房", "卖房",
    "说明", "明白", "明确", "明天", "明日", "明显", "明智", "光明", "聪明", "阐明", "表明", "证明", "声明", "分明", "查明",
    "刚才", "方才", "方案", "方程", "方位", "方法", "方便", "方式", "方面",
    "别人", "别院", "别处", "别动", "别走", "别说", "别想", "别的", "分别", "告别", "性别", "辨别", "特别",
    "能够", "能力", "能量", "能否", "无能", "可能", "才能",
    "全国", "全部", "全面", "完全", "健全", "安全", "全力",
    "通过", "通知", "通信", "通常", "交通", "普通", "共通",
    "车站", "车子", "马车", "开车", "倒车", "上车", "下车",
    "事情", "事故", "事项", "事例", "事务", "同事",
    "东西", "物体", "物质", "物理",
    "地方", "到处", "处理", "处于", "处罚",
    "按时", "准时", "及时", "顿时", "随时",
    "成真", "成功", "成熟", "成立", "成全", "成为", "成千", "成品", "成本", "成见", "成果",
    "平和", "平淡", "平静", "平常", "平凡", "平生", "平时", "平等", "平平", "水平",
    "和平", "和好", "和睦", "和气", "温和", "总和",
    "步步", "脚步", "跑步", "散步", "步伐", "步骤", "进步", "退步",
    "利益", "利用", "利息", "利润", "胜利", "顺利", "权利", "权力",
    "师傅", "师父", "老师", "律师", "医师", "大师",
    "融合", "融化", "金融", "融洽",
    "后来", "后天", "后面", "后方", "后果", "身后", "然后", "最后",
    "红色", "红酒", "红茶", "红军", "火红", "通红",
    "空中", "空气", "空间", "落空", "空虚", "天空", "星空", "晴空",
    "各位", "各地", "各种", "各样", "各自", "各个",
    "每天", "每年", "每月", "每日", "每当", "每逢", "每个", "每次",
    "此时", "此刻", "此地", "从此", "因此", "彼此", "由此", "此外",
    "真正", "真相", "真心", "真实", "真假", "天真", "认真", "假戏",
    "花生", "花钱", "花心", "鲜花", "开花",
    "沈家", "傅家", "苏家", "赵家", "陆家", "叶家", "林家", "楚家", "顾家", "秦家", "王家", "李家", "张家", "刘家",
    "都傻", "都傻了", "都呆", "都呆了", "都疯", "都疯了", "都笑", "都哭", "都走", "都来", "都说", "都看", "都想", "都要", "都会", "都能", "都是", "都有", "都没", "都不", "都在",
    "都市", "首都", "京都", "成都", "全都", "大都", "古都", "帝都", "魔都",
    "胡说", "胡言", "胡闹", "胡来", "胡乱", "胡思", "胡扯", "胡椒", "胡同", "胡须", "胡子", "二胡",
    "年级", "年纪", "年龄", "年代", "年度", "年初", "年底", "年中", "年轻", "年少", "年迈", "年长", "年间", "年头", "年华", "纪念", "纪元", "纪律", "纪录", "世纪",
    "对方能", "方能", "方可", "方才", "方法", "方向", "方面", "方式", "方案", "方便", "方寸", "方圆",
    "何人", "何事", "何物", "何处", "何时", "何必", "何况", "何苦", "何止", "何妨", "何尝", "何不", "奈何", "如何", "为何",
    "余生", "其余", "多余", "业余", "余地", "余下", "余力", "余孽",
    "安全", "完全", "全部", "全体", "全国", "全面", "全力", "全能", "成全", "十全",
    "常人", "常识", "常见", "常用", "常理", "常态", "常客", "往常", "平常", "异常", "反常", "无常", "日常",
    "高明", "精明", "英明", "开明", "透明", "失明", "黎明", "清明", "文明", "神明", "明明",
    "厉害", "严厉", "再接再厉", "安静", "平静", "冷静", "动静", "查清楚", "清楚", "调查", "检查", "查看", "查找",
    "相声", "相信", "相同", "相当", "相对", "相反", "相处", "互相", "真相", "丞相", "照相", "相照应", "照应",
    "符合", "符号", "音符", "张嘴", "张口", "张望", "夸张", "紧张", "主张", "嚣张", "马术", "算术", "武术", "艺术", "手术", "技术", "学术",
    "单独", "单纯", "单身", "单位", "单词", "名单", "菜单", "简单", "孤单", "买单", "床单", "账单",
    "从医", "从法", "从此", "从前", "从来", "从容", "从事", "服从", "顺从", "遵从", "跟从", "自从", "随从",
    "毕业", "关注", "束后", "结束", "渠道", "资金"
}

# Common verbs, particles, pronouns, prepositions, kinship terms that should NEVER be swallowed as given-name characters
NON_GIVEN_NAME_CHARS: Set[str] = {
    "的", "了", "着", "过", "得", "地", "吗", "呢", "吧", "啊", "呀", "哦", "哈", "哼",
    "我", "你", "他", "她", "它", "们", "这", "那", "哪", "谁", "什", "么", "自", "己",
    "在", "有", "没", "是", "不", "很", "太", "真", "都", "全", "也", "又", "还", "就",
    "才", "只", "但", "却", "而", "并", "把", "将", "向", "往", "从", "对", "跟", "和",
    "与", "或", "被", "让", "给", "替", "为", "因", "所", "以", "虽", "然", "如", "果",
    "转", "移", "走", "来", "去", "回", "到", "过", "起", "开", "关", "停", "留", "离",
    "看", "见", "说", "话", "讲", "问", "答", "想", "要", "能", "会", "敢", "肯", "愿",
    "做", "作", "干", "办", "弄", "搞", "打", "杀", "死", "活", "救", "帮", "扶", "拉",
    "推", "抓", "拿", "握", "抱", "搂", "亲", "吻", "咬", "吃", "喝", "吞", "吐", "穿",
    "脱", "坐", "站", "躺", "睡", "醒", "跑", "逃", "跳", "飞", "追", "赶", "进", "出",
    "上", "下", "入", "哭", "笑", "喊", "叫", "骂", "叹", "怕", "恨", "爱", "喜", "怒",
    "买", "卖", "送", "收", "取", "偷", "抢", "骗", "娶", "嫁", "生", "养", "带", "领",
    # Pronouns, classifiers, measure words & noun suffixes
    "何", "个", "子", "于", "人", "家", "些", "样", "么", "几", "点", "位", "只", "双", "件", "种", "条", "张", "份",
    # Family & kinship relation terms (should not be swallowed into personal names)
    "母", "父", "爸", "妈", "伯", "叔", "姑", "姨", "舅", "哥", "弟", "姐", "妹", "爷", "奶", "儿", "孙", "公", "婆", "丈", "妻", "夫",
    # Space, time, directions
    "事", "物", "处", "时", "分", "秒", "年", "月", "日", "天", "里", "边", "面", "外", "内", "前", "后", "东", "西", "南", "北", "中",
    # Adjectives & opposites, adverbs commonly preceding verbs
    "大", "小", "多", "少", "高", "低", "长", "短", "新", "旧", "好", "坏", "深", "浅", "重", "轻", "快", "慢", "早", "紧", "久", "远", "近",
    "傻", "疯", "呆", "愣", "瞎", "聋", "哑", "醉", "醒", "饿", "饱", "累", "困", "病", "痛", "痒", "麻", "错", "对", "真", "假", "空", "满", "乱", "齐", "全", "半", "单", "双",
    "今", "派", "治", "确", "各", "怎", "任", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "百", "千", "万", "两",
    "现", "谈", "待", "害", "嘴", "口", "手", "脚", "眼", "耳", "鼻", "头", "身", "心", "脸", "皮", "毛", "骨", "血", "肉",
    "欠", "混", "横", "注", "业", "道"
}

# Surnames that coincide with extremely common pronouns, adverbs, nouns, or verbs.
# These MUST NOT match plain 2-3 char given names unless followed by an explicit title affix (e.g. 房少, 任总, 师尊).
AMBIGUOUS_SURNAMES: Set[str] = {
    "那", "房", "终", "明", "任", "能", "全", "通", "车", "井", "水", "山",
    "家", "国", "成", "平", "和", "步", "时", "利", "师", "融", "后", "红",
    "空", "别", "各", "每", "此", "正", "直", "方", "常", "真", "花", "文", "武",
    "都", "胡", "年", "纪", "向", "连", "万", "千", "百", "十", "一", "二", "三", "四", "五", "六", "七", "八", "九",
    "古", "今", "老", "少", "男", "女", "生", "死", "来", "往", "进", "出", "上", "下", "左", "右",
    "东", "西", "南", "北", "中", "外", "内", "前", "后", "里", "边", "间", "处", "所", "地", "天",
    "道", "理", "心", "意", "情", "爱", "恨", "愁", "喜", "怒", "哀", "乐", "笑", "哭", "言", "语", "话", "说",
    "查", "相", "单", "从", "厉", "安", "符", "谈", "满", "冷", "热", "干", "湿", "苦", "甜", "酸", "辣", "咸",
    "毕", "束", "关", "金"
}


def get_hanviet_data() -> Dict[str, Any]:
    global _CACHED_HANVIET_DATA
    if _CACHED_HANVIET_DATA is not None:
        return _CACHED_HANVIET_DATA

    if os.path.exists(DICT_PATH):
        try:
            with open(DICT_PATH, "r", encoding="utf-8") as f:
                _CACHED_HANVIET_DATA = json.load(f)
                return _CACHED_HANVIET_DATA
        except Exception as e:
            logger.warning(f"Failed to load hanviet_dict.json: {e}")

    _CACHED_HANVIET_DATA = {
        "char_to_hanviet": {
            "薛": "Tiết", "彩": "Thải", "衣": "Y", "白": "Bạch", "清": "Thanh",
            "臣": "Thần", "晨": "Thần", "沈": "Thẩm", "浪": "Lãng", "萧": "Tiêu", "炎": "Viêm"
        },
        "char_to_pinyin": {
            "薛": "xue", "彩": "cai", "衣": "yi", "白": "bai", "清": "qing",
            "臣": "chen", "晨": "chen", "沈": "shen", "浪": "lang", "萧": "xiao", "炎": "yan"
        },
        "surnames": ["薛", "白", "沈", "萧", "叶", "林", "楚", "石", "宁", "范", "徐", "李", "王", "张"],
        "compound_surnames": ["欧阳", "司马", "上官", "诸葛", "皇甫", "慕容"]
    }
    return _CACHED_HANVIET_DATA


def char_to_hanviet(char: str) -> str:
    """Returns Sino-Vietnamese reading for a Hanzi character."""
    data = get_hanviet_data()
    return data.get("char_to_hanviet", {}).get(char, char)


def char_to_pinyin(char: str) -> str:
    """Returns lowercase Pinyin syllable without tones for a Hanzi character."""
    data = get_hanviet_data()
    return data.get("char_to_pinyin", {}).get(char, "")


def text_to_hanviet(zh_text: str) -> str:
    """
    Transliterates a Chinese string into title-cased Sino-Vietnamese words.
    E.g. '薛彩衣' -> 'Tiết Thải Y', '白清臣' -> 'Bạch Thanh Thần'.
    """
    if not zh_text:
        return ""
    words = []
    for c in zh_text:
        hv = char_to_hanviet(c)
        words.append(hv)
    return " ".join(words)


def extract_chinese_names_in_text(zh_text: str) -> List[Dict[str, str]]:
    """
    Detects potential Chinese proper names and titles in zh_text without producing fragmented sub-words.
    """
    if not zh_text:
        return []

    data = get_hanviet_data()
    surnames = set(data.get("surnames", []))
    compound_surnames = data.get("compound_surnames", [])
    char_to_hv = data.get("char_to_hanviet", {})
    char_to_py = data.get("char_to_pinyin", {})

    detected: List[Dict[str, str]] = []
    seen_zh: Set[str] = set()

    title_affixes = ("妃娘娘", "娘娘", "妃", "总", "少", "王", "帝", "后", "师尊", "掌门", "宗主", "阁主", "长老", "公子", "小姐")

    # 1. Match Compound Surnames (e.g. 欧阳, 诸葛, 司马) + 1-2 chars
    for cs in compound_surnames:
        idx = 0
        while idx < len(zh_text):
            found_idx = zh_text.find(cs, idx)
            if found_idx == -1:
                break
            matched = False
            for length in (4, 3):
                cand = zh_text[found_idx:found_idx + length]
                if len(cand) == length and all('\u4e00' <= c <= '\u9fff' and c in char_to_hv for c in cand):
                    given_part = cand[len(cs):]
                    if not any(ch in NON_GIVEN_NAME_CHARS for ch in given_part):
                        if cand not in COMMON_ZH_VOCABULARY_STOPWORDS and cand not in seen_zh:
                            hv = " ".join([char_to_hv[c] for c in cand])
                            py = " ".join([char_to_py.get(c, "") for c in cand])
                            detected.append({"zh": cand, "hanviet": hv, "pinyin": py})
                            seen_zh.add(cand)
                            idx = found_idx + length
                            matched = True
                            break
            if not matched:
                idx = found_idx + len(cs)

    # 2. Match Single Surnames (e.g. 薛, 白, 沈, 萧...)
    i = 0
    while i < len(zh_text):
        c = zh_text[i]
        matched_length = 1

        # Check if preceding character binds with c into a common non-name compound word
        if i > 0:
            preceding_two = zh_text[i - 1:i + 1]
            if preceding_two in (
                "说明", "证明", "表明", "声明", "阐明", "分明", "查明", "聪明", "光明", "发明",
                "担任", "胜任", "信任", "委任", "责任", "重任", "任何",
                "关于", "对于", "处于", "由于", "属于", "在于", "基于", "至于", "敢于", "善于", "终于",
                "刚才", "方才", "方案", "前方", "后方", "对方", "地方",
                "起初", "当初", "最初", "最后", "之后", "以后", "以前", "之前", "日前",
                "分别", "告别", "特别", "留别", "临别", "差别",
                "能够", "可能", "未能", "只能", "全能", "无能",
                "通过", "交通", "普通", "共通", "畅通",
                "下车", "上车", "倒车", "马车", "火车", "汽车", "开车",
                "事故", "同事", "办事", "省事", "凡事", "懂事"
            ):
                i += 1
                continue

        if c in surnames and c in char_to_hv:
            # Check title pattern first: e.g. 薛妃娘娘, 薛妃, 白总, 萧少, 房少, 任总
            title_found = False
            for affix in title_affixes:
                if affix == "后" and i > 0 and zh_text[i - 1:i + 1] in ("结束", "约束", "拘束", "管束"):
                    continue
                cand_title = c + affix
                if zh_text[i:i + len(cand_title)] == cand_title and all(ch in char_to_hv for ch in cand_title):
                    if cand_title not in seen_zh:
                        hv = " ".join([char_to_hv[ch] for ch in cand_title])
                        py = " ".join([char_to_py.get(ch, "") for ch in cand_title])
                        detected.append({"zh": cand_title, "hanviet": hv, "pinyin": py})
                        seen_zh.add(cand_title)
                    matched_length = len(cand_title)
                    title_found = True
                    break

            # If it's an ambiguous surname (e.g. 那, 房, 终, 明, 任, 别, 能...), ONLY allow explicit title affixes
            if not title_found and c not in AMBIGUOUS_SURNAMES:
                # Check 3-char name: Surname + 2 chars (e.g. 薛彩衣, 白清臣, 苏晚晴)
                if i + 3 <= len(zh_text):
                    cand3 = zh_text[i:i + 3]
                    if (
                        all('\u4e00' <= ch <= '\u9fff' and ch in char_to_hv for ch in cand3)
                        and cand3 not in COMMON_ZH_VOCABULARY_STOPWORDS
                        and cand3[:2] not in COMMON_ZH_VOCABULARY_STOPWORDS
                        and cand3[1:] not in COMMON_ZH_VOCABULARY_STOPWORDS
                        and cand3[1] not in NON_GIVEN_NAME_CHARS
                        and cand3[2] not in NON_GIVEN_NAME_CHARS
                    ):
                        if not cand3.endswith(("的人", "的话", "了吧", "了没", "了吗", "之中", "之间")):
                            if cand3 not in seen_zh:
                                hv = " ".join([char_to_hv[ch] for ch in cand3])
                                py = " ".join([char_to_py.get(ch, "") for ch in cand3])
                                detected.append({"zh": cand3, "hanviet": hv, "pinyin": py})
                                seen_zh.add(cand3)
                            matched_length = 3
                # Check 2-char name if 3-char not matched (e.g. 沈毅, 萧炎)
                if matched_length == 1 and i + 2 <= len(zh_text):
                    cand2 = zh_text[i:i + 2]
                    if (
                        all('\u4e00' <= ch <= '\u9fff' and ch in char_to_hv for ch in cand2)
                        and cand2 not in COMMON_ZH_VOCABULARY_STOPWORDS
                        and cand2[1] not in NON_GIVEN_NAME_CHARS
                        and cand2[1] not in surnames
                    ):
                        if cand2 not in ("他们", "我们", "自己", "如果", "为了", "因为", "所以", "不过", "由于", "就是", "还是", "甚至", "这样", "那样"):
                            if cand2 not in seen_zh:
                                hv = " ".join([char_to_hv[ch] for ch in cand2])
                                py = " ".join([char_to_py.get(ch, "") for ch in cand2])
                                detected.append({"zh": cand2, "hanviet": hv, "pinyin": py})
                                seen_zh.add(cand2)
                            matched_length = 2

        i += matched_length

    detected.sort(key=lambda x: len(x["zh"]), reverse=True)
    return detected


def replace_pinyin_with_hanviet(source_zh: str, translated_vi: str) -> str:
    """
    Scans machine-translated Vietnamese text for Pinyin proper nouns (e.g. 'Xue Caiyi',
    'Bai Qingchen', 'Shen Lang') and replaces them with standard Sino-Vietnamese (Hán - Việt).
    Cross-references with Chinese characters in source_zh.
    """
    if not translated_vi:
        return ""

    vi = translated_vi

    special_name_fixes = {
        "Bai Qingchen": "Bạch Thanh Trần",
        "Baiqingchen": "Bạch Thanh Trần",
        "Bai Qing Chen": "Bạch Thanh Trần",
        "Xue Caiyi": "Tiết Thải Y",
        "Xuecaiyi": "Tiết Thải Y",
        "Xue Cai Yi": "Tiết Thải Y",
    }
    for py_term, hv_term in special_name_fixes.items():
        if py_term.lower() in vi.lower():
            vi = re.sub(r'\b' + re.escape(py_term) + r'\b', hv_term, vi, flags=re.IGNORECASE)

    detected_names = extract_chinese_names_in_text(source_zh)

    for item in detected_names:
        zh_str = item["zh"]
        hv_str = item["hanviet"]
        py_tokens = item["pinyin"].split()

        if not py_tokens or not all(py_tokens):
            continue

        patterns: List[str] = []
        if len(py_tokens) == 2:
            p1, p2 = py_tokens
            patterns.extend([
                f"{p1.title()} {p2.title()}",
                f"{p1.title()}{p2.lower()}",
                f"{p1.title()}-{p2.lower()}",
                f"{p1.title()}-{p2.title()}",
                f"{p1.lower()} {p2.lower()}",
            ])
        elif len(py_tokens) == 3:
            p1, p2, p3 = py_tokens
            patterns.extend([
                f"{p1.title()} {p2.title()} {p3.title()}",
                f"{p1.title()} {p2.title()}{p3.lower()}",
                f"{p1.title()}{p2.lower()}{p3.lower()}",
                f"{p1.title()}-{p2.title()}-{p3.title()}",
                f"{p1.lower()} {p2.lower()}{p3.lower()}",
            ])
        elif len(py_tokens) == 4:
            p1, p2, p3, p4 = py_tokens
            patterns.extend([
                f"{p1.title()} {p2.title()} {p3.title()} {p4.title()}",
                f"{p1.title()}{p2.lower()} {p3.title()}{p4.lower()}",
                f"{p1.title()}{p2.lower()}{p3.lower()}{p4.lower()}",
            ])

        for pat in patterns:
            if pat.lower() in vi.lower():
                vi = re.sub(r'\b' + re.escape(pat) + r'\b', hv_str, vi, flags=re.IGNORECASE)

    # Single surname + title fallback
    data = get_hanviet_data()
    char_to_hv = data.get("char_to_hanviet", {})
    char_to_py = data.get("char_to_pinyin", {})
    surnames = set(data.get("surnames", []))

    for sn in surnames:
        py_sn = char_to_py.get(sn, "")
        hv_sn = char_to_hv.get(sn, "")
        if py_sn and hv_sn and len(py_sn) >= 3 and sn in source_zh:
            for suffix, vi_suffix in [("phi", "phi"), ("tong", "tổng"), ("thieu gia", "thiếu gia"), ("tieu thu", "tiểu thư")]:
                pat_title = f"{py_sn} {suffix}"
                if pat_title.lower() in vi.lower():
                    vi = re.sub(r'\b' + re.escape(pat_title) + r'\b', f"{hv_sn} {vi_suffix}", vi, flags=re.IGNORECASE)

    return vi


def enhance_chinese_with_hanviet_entities(texts: List[str]) -> Tuple[List[str], Dict[str, str]]:
    """
    Pre-translation step:
    Scans a batch of Chinese texts, identifies all proper names/titles,
    and returns (modified_texts, entity_map).
    """
    entity_map: Dict[str, str] = {}
    for t in texts:
        names = extract_chinese_names_in_text(t)
        for item in names:
            zh = item["zh"]
            if len(zh) >= 2 and zh not in entity_map:
                entity_map[zh] = item["hanviet"]

    if "白清臣" in entity_map:
        entity_map["白清臣"] = "Bạch Thanh Trần"
    if "白清晨" in entity_map:
        entity_map["白清晨"] = "Bạch Thanh Trần"

    modified_texts = []
    sorted_entities = sorted(entity_map.items(), key=lambda x: len(x[0]), reverse=True)

    for t in texts:
        work_t = t
        for zh, hv in sorted_entities:
            if zh in work_t:
                work_t = work_t.replace(zh, f" {hv} ")
        modified_texts.append(re.sub(r'\s+', ' ', work_t).strip())

    return modified_texts, entity_map


def normalize_ocr_character_names(texts: List[str]) -> Tuple[List[str], Dict[str, str]]:
    """
    Scans the entire script for 3-character proper names and automatically fixes
    1-character OCR homograph typos (e.g. '苏晚睛' -> '苏晚晴' when '苏晚晴' is the dominant name).
    Returns (normalized_texts, canonical_name_to_hanviet).
    """
    if not texts:
        return texts, {}

    from collections import Counter
    name_counts: Counter = Counter()
    name_to_hv: Dict[str, str] = {}

    for t in texts:
        for item in extract_chinese_names_in_text(t):
            zh = item["zh"]
            if len(zh) == 3:
                name_counts[zh] += 1
                name_to_hv[zh] = item["hanviet"]

    # Find canonical 3-char names (appearing >= 2 times) and merge rare 1-char OCR variants
    typo_replacements: Dict[str, str] = {}
    canonical_names = [n for n, cnt in name_counts.most_common() if cnt >= 2]

    for i, dom in enumerate(canonical_names):
        dom_cnt = name_counts[dom]
        # Also check all 3-char substrings starting with dom[:2] in raw texts even if 3rd char wasn't matched
        prefix2 = dom[:2]
        for t in texts:
            idx = 0
            while idx < len(t):
                found = t.find(prefix2, idx)
                if found == -1 or found + 3 > len(t):
                    break
                cand = t[found:found + 3]
                if cand != dom and all('\u4e00' <= c <= '\u9fff' for c in cand):
                    if cand[2] not in NON_GIVEN_NAME_CHARS:
                        cand_cnt = sum(x.count(cand) for x in texts)
                        if 0 < cand_cnt * 3 <= dom_cnt:
                            typo_replacements[cand] = dom
                idx = found + 1

    normalized_texts: List[str] = []
    for t in texts:
        work_t = t
        for bad_name, good_name in typo_replacements.items():
            if bad_name in work_t:
                work_t = work_t.replace(bad_name, good_name)
        normalized_texts.append(work_t)

    canonical_hv_map: Dict[str, str] = {}
    for t in normalized_texts:
        for item in extract_chinese_names_in_text(t):
            zh = item["zh"]
            if len(zh) >= 2 and zh not in canonical_hv_map:
                canonical_hv_map[zh] = item["hanviet"]

    if "白清臣" in canonical_hv_map:
        canonical_hv_map["白清臣"] = "Bạch Thanh Trần"
    if "白清晨" in canonical_hv_map:
        canonical_hv_map["白清晨"] = "Bạch Thanh Trần"

    return normalized_texts, canonical_hv_map


def build_hanviet_glossary_hints(texts: List[str], max_items: int = 30) -> str:
    """
    Extracts candidate proper names from a list of Chinese texts and formats them
    as a non-destructive Sino-Vietnamese reference glossary for AI translation prompts.
    """
    if not texts:
        return ""

    from collections import Counter
    counts: Counter = Counter()
    hv_map: Dict[str, str] = {}

    for t in texts:
        for item in extract_chinese_names_in_text(t):
            zh = item["zh"]
            if len(zh) >= 2:
                counts[zh] += 1
                hv_map[zh] = item["hanviet"]

    if "白清臣" in hv_map:
        hv_map["白清臣"] = "Bạch Thanh Trần"
    if "白清晨" in hv_map:
        hv_map["白清晨"] = "Bạch Thanh Trần"

    if not counts:
        return ""

    top_items = [zh for zh, _ in counts.most_common(max_items)]
    pairs = [f"{zh} = {hv_map[zh]}" for zh in top_items]
    return ", ".join(pairs)


FOREIGN_SCRIPT_RE = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af\u0400-\u04ff]+')


def transliterate_remaining_hanzi(vi_text: str) -> str:
    """
    If any Chinese characters remain in a translated Vietnamese line (e.g., 'Thẩm毅 chuyển đi'),
    automatically replaces known Hanzi with their Sino-Vietnamese reading ('Thẩm Nghị chuyển đi').
    """
    if not vi_text or not re.search(r'[\u4e00-\u9fff]', vi_text):
        return vi_text

    data = get_hanviet_data()
    char_to_hv = data.get("char_to_hanviet", {})

    def _replace_match(match: re.Match) -> str:
        chunk = match.group(0)
        out_parts = []
        for ch in chunk:
            if ch in char_to_hv:
                out_parts.append(char_to_hv[ch])
            else:
                out_parts.append(ch)
        return " " + " ".join(out_parts) + " "

    res = re.sub(r'[\u4e00-\u9fff]+', _replace_match, vi_text)
    res = re.sub(r'\s+([,.;:!?])', r'\1', res)
    return re.sub(r'\s+', ' ', res).strip()


def detect_untranslated_foreign_chars(vi_text: str) -> List[str]:
    """
    Returns list of remaining foreign script chunks (Chinese, Japanese, Korean, Cyrillic)
    in a Vietnamese subtitle line.
    """
    if not vi_text:
        return []
    return FOREIGN_SCRIPT_RE.findall(vi_text)

