"""
Comprehensive Sino-Vietnamese (Hán - Việt) dictionary builder & dataset.
Maps Hanzi -> (Vietnamese Hán-Việt reading, Pinyin) for automatic transliteration
of Chinese names, titles, and proper nouns in video subtitling/dubbing.
"""
import os
import json

DATA_ENTRIES = [
    # Top Chinese Surnames & Character names
    "薛:Tiết:xue", "彩:Thải:cai", "衣:Y:yi", "白:Bạch:bai", "清:Thanh:qing", "臣:Thần:chen", "晨:Thần:chen",
    "沈:Thẩm:shen", "浪:Lãng:lang", "萧:Tiêu:xiao", "炎:Viêm:yan", "薰:Huân:xun", "儿:Nhi:er", "鳞:Lân:lin",
    "叶:Diệp:ye", "辰:Thần:chen", "凡:Phàm:fan", "林:Lâm:lin", "风:Phong:feng", "动:Động:dong", "石:Thạch:shi",
    "昊:Hạo:hao", "楚:Sở:chu", "韩:Hàn:han", "立:Lập:li", "陈:Trần:chen", "江:Giang:jiang", "尘:Trần:chen",
    "秦:Tần:qin", "牧:Mục:mu", "顾:Cố:gu", "长:Trường:chang", "歌:Ca:ge", "王:Vương:wang", "苏:Tô:su",
    "铭:Minh:ming", "纯:Thuần:chun", "许:Hứa:xu", "七:Thất:qi", "安:An:an", "宁:Ninh:ning", "缺:Khuyết:que",
    "范:Phạm:fan", "闲:Nhàn:xian", "徐:Từ:xu", "凤:Phượng:feng", "年:Niên:nian", "李:Lý:li", "夜:Dạ:ye",
    "杨:Dương:yang", "开:Khai:kai", "罗:La:luo", "唐:Đường:tang", "三:Tam:san", "舞:Vũ:wu", "纳:Nạp:na",
    "兰:Lan:lan", "嫣:Yên:yan", "然:Nhiên:ran", "云:Vân:yun", "韵:Vận:yun", "雪:Tuyết:xue", "婉:Uyển:wan",
    "柳:Liễu:liu", "如:Như:ru", "烟:Yên:yan", "幼:Ấu:you", "容:Dung:rong", "鱼:Ngư:yu", "姜:Khương:jiang",
    "泥:Nê:ni", "南:Nam:nan", "宫:Cung:gong", "仆:Phó:pu", "射:Xạ:she", "寒:Hàn:han", "姬:Cơ:ji",
    "黄:Hoàng:huang", "菲:Phi:fei", "张:Trương:zhang", "刘:Lưu:liu", "赵:Triệu:zhao", "周:Chu:zhou",
    "吴:Ngô:wu", "孙:Tôn:sun", "胡:Hồ:hu", "朱:Chu:zhu", "高:Cao:gao", "何:Hà:he", "郭:Quách:guo",
    "马:Mã:ma", "梁:Lương:liang", "宋:Tống:song", "郑:Trịnh:zheng", "谢:Tạ:xie", "冯:Phùng:feng",
    "于:Vu:yu", "董:Đổng:dong", "程:Trình:cheng", "曹:Tào:cao", "袁:Viên:yuan", "邓:Đặng:deng",
    "傅:Phó:fu", "曾:Tăng:zeng", "彭:Bành:peng", "吕:Lữ:lv", "卢:Lư:lu", "蒋:Tưởng:jiang",
    "蔡:Thái:cai", "贾:Giả:jia", "丁:Đinh:ding", "魏:Ngụy:wei", "阎:Diêm:yan", "余:Dư:yu",
    "潘:Phan:pan", "杜:Đỗ:du", "戴:Đới:dai", "夏:Hạ:xia", "钟:Chung:zhong", "汪:Uông:wang",
    "田:Điền:tian", "任:Nhậm:ren", "方:Phương:fang", "姚:Diêu:yao", "谭:Đàm:tan", "廖:Liêu:liao",
    "邹:Trâu:zou", "熊:Hùng:xiong", "金:Kim:jin", "陆:Lục:lu", "郝:Hách:hao", "孔:Khổng:kong",
    "崔:Thôi:cui", "康:Khang:kang", "毛:Mao:mao", "邱:Khâu:qiu", "史:Sử:shi", "侯:Hầu:hou",
    "邵:Thiệu:shao", "孟:Mạnh:meng", "龙:Long:long", "万:Vạn:wan", "段:Đoàn:duan", "雷:Lôi:lei",
    "钱:Tiền:qian", "汤:Thang:tang", "尹:Doãn:yin", "黎:Lê:li", "易:Dịch:yi", "常:Thường:chang",
    "武:Vũ:wu", "乔:Kiều:qiao", "贺:Hạ:he", "赖:Lại:lai", "龚:Cung:gong", "文:Văn:wen",
    "严:Nghiêm:yan", "施:Thi:shi", "陶:Đào:tao", "洪:Hồng:hong", "翟:Trạch:zhai", "颜:Nhan:yan",
    "倪:Nghê:ni", "牛:Ngưu:niu", "温:Ôn:wen", "俞:Du:yu", "章:Chương:zhang", "鲁:Lỗ:lu",
    "葛:Cát:ge", "伍:Ngũ:wu", "韦:Vi:wei", "申:Thân:shen", "尤:Ưu:you", "毕:Tất:bi",
    "聂:Nhiếp:nie", "焦:Tiêu:jiao", "向:Hướng:xiang", "邢:Hình:xing", "路:Lộ:lu", "岳:Nhạc:yue",
    "齐:Tề:qi", "梅:Mai:mei", "莫:Mạc:mo", "庄:Trang:zhuang", "辛:Tân:xin", "管:Quản:guan",
    "祝:Chúc:zhu", "左:Tả:zuo", "谷:Cốc:gu", "时:Thời:shi", "舒:Thư:shu", "耿:Cảnh:geng",
    "关:Quan:guan", "苗:Miêu:miao", "凌:Lăng:ling", "费:Phí:fei", "纪:Kỷ:ji", "靳:Cận:jin",
    "盛:Thịnh:sheng", "童:Đồng:tong", "欧:Âu:ou", "甄:Chân:zhen", "项:Hạng:xiang", "曲:Khúc:qu",
    "成:Thành:cheng", "游:Du:you", "阳:Dương:yang", "裴:Bùi:pei", "席:Tịch:xi", "卫:Vệ:wei",
    "查:Tra:zha", "屈:Khuất:qu", "鲍:Bào:bao", "霍:Hoắc:huo", "翁:Ông:weng", "隋:Tùy:sui",
    "甘:Cam:gan", "景:Cảnh:jing", "薄:Bạc:bo", "单:Đan:shan", "包:Bao:bao", "司:Tư:si",
    "柴:Sài:chai", "瞿:Cù:qu", "阮:Nguyễn:ruan", "桂:Quế:gui", "闵:Mẫn:min",

    # Compound Surnames
    "欧阳:Âu Dương:ouyang", "司马:Tư Mã:sima", "上官:Thượng Quan:shangguan", "诸葛:Gia Cát:zhuge",
    "皇甫:Hoàng Phủ:huangfu", "尉迟:Uất Trì:yuchi", "公孙:Công Tôn:gongsun", "慕容:Mộ Dung:murong",
    "独孤:Độc Cô:dugu", "澹台:Đạm Đài:dantai", "轩辕:Hiên Viên:xuanyuan", "令狐:Lệnh Hồ:linghu",
    "东方:Đông Phương:dongfang", "西门:Tây Môn:ximen", "赫连:Hách Liên:helian", "钟离:Chung Ly:zhongli",
    "长孙:Trường Tôn:zhangsun", "夏侯:Hạ Hầu:xiahou",

    # Titles & Nobility
    "帝:Đế:di", "皇:Hoàng:huang", "妃:Phi:fei", "后:Hậu:hou", "娘:Nương:niang", "王:Vương:wang",
    "宗:Tông:zong", "门:Môn:men", "派:Phái:pai", "阁:Các:ge", "殿:Điện:dian", "府:Phủ:fu",
    "主:Chủ:zhu", "尊:Tôn:zun", "老:Lão:lao", "圣:Thánh:sheng", "神:Thần:shen", "仙:Tiên:xian",
    "魔:Ma:mo", "妖:Yêu:yao", "道:Đạo:dao", "佛:Phật:fo", "君:Quân:jun", "公:Công:gong",
    "侯:Hầu:hou", "伯:Bá:bo", "子:Tử:zi", "男:Nam:nan", "女:Nữ:nv", "郎:Lang:lang",
    "妾:Thiếp:qie", "奴:Nô:nu", "婢:Tỳ:bi", "仆:Phó:pu", "将:Tướng:jiang", "帅:Soái:shuai",
    "相:Tướng:xiang", "使:Sứ:shi", "使者:Sứ Giả:shizhe", "长老:Trưởng Lão:zhanglao",
    "掌门:Chưởng Môn:zhangmen", "宗主:Tông Chủ:zongzhu", "门主:Môn Chủ:menzhu", "阁主:Các Chủ:gezhu",
    "师尊:Sư Tôn:shizun", "师父:Sư Phụ:shifu", "师傅:Sư Phụ:shifu", "师兄:Sư Huynh:shixiong",
    "师弟:Sư Đệ:shidi", "师姐:Sư Tỷ:shijie", "师妹:Sư Muội:shimei", "徒儿:Đồ Nhi:tuer",
    "徒弟:Đồ Đệ:tudi", "殿下:Điện Hạ:dianxia", "陛下:Bệ Hạ:bixia", "皇上:Hoàng Thượng:huangshang",
    "娘娘:Nương Nương:niangniang", "太后:Thái Hậu:taihou", "太妃:Thái Phi:taifei", "贵妃:Quý Phi:guifei",
    "皇妃:Hoàng Phi:huangfei", "王妃:Vương Phi:wangfei", "太子:Thái Tử:taizi", "皇子:Hoàng Tử:huangzi",
    "公主:Công Chúa:gongzhu", "郡主:Quận Chúa:junzhu", "世子:Thế Tử:shizi", "公子:Công Tử:gongzi",
    "少爷:Thiếu Gia:shaoye", "小姐:Tiểu Thư:xiaojie", "夫人:Phu Nhân:furen", "总:Tổng:zong",
    "总裁:Tổng Tài:zongcai", "大帝:Đại Đế:dadi", "神王:Thần Vương:shenwang", "至尊:Chí Tôn:zhizun",
    "霸主:Bá Chủ:bazhu", "巨擘:Cự Phách:jubo", "天尊:Thiên Tôn:tianzun", "道尊:Đạo Tôn:daozun",
    "仙王:Tiên Vương:xianwang", "真仙:Chân Tiên:zhenxian", "金仙:Kim Tiên:jinxian", "玄仙:Huyền Tiên:xuanxian",

    # Characters in current project & missing items
    "一:Nhất:yi", "二:Nhị:er", "三:Tam:san", "四:Tứ:si", "五:Ngũ:wu", "六:Lục:liu", "七:Thất:qi",
    "八:Bát:ba", "九:Cửu:jiu", "十:Thập:shi", "百:Bách:bai", "千:Thiên:qian", "万:Vạn:wan", "亿:Ức:yi",
    "下:Hạ:xia", "上:Thượng:shang", "且:Thả:qie", "两:Lưỡng:liang", "个:Cá:ge", "也:Dã:ye",
    "事:Sự:shi", "亮:Lượng:liang", "人:Nhân:ren", "似:Tự:si", "住:Trú:zhu", "其:Kỳ:qi",
    "几:Kỷ:ji", "却:Khước:que", "厉:Lệ:li", "台:Đài:tai", "吞:Thôn:tun", "咱:Tạp:zan",
    "啊:A:a", "器:Khí:qi", "外:Ngoại:wai", "头:Đầu:tou", "家:Gia:jia", "就:Tựu:jiu",
    "差:Sai:cha", "彼:Bỉ:bi", "怎:Chẩm:zen", "愣:Lăng:leng", "愿:Nguyện:yuan", "暴:Bạo:bao",
    "未:Vị:wei", "机:Cơ:ji", "条:Điều:tiao", "样:Dạng:yang", "环:Hoàn:huan", "的:Đích:de",
    "系:Hệ:xi", "而:Nhi:er", "能:Năng:neng", "良:Lương:liang", "跟:Cân:gen", "还:Hoàn:hai",
    "面:Diện:mian", "以:Dĩ:yi", "会:Hội:hui", "害:Hại:hai", "根:Căn:gen", "止:Chỉ:zhi",
    "漂:Phiêu:piao", "简:Giản:jian", "晨:Thần:chen", "晨:Thần:chen", "晨:Thần:chen",
    "剑:Kiếm:jian", "刀:Đao:dao", "枪:Thương:qiang", "戟:Kích:ji", "弓:Cung:gong", "箭:Tiễn:jian",
    "丹:Đan:dan", "药:Dược:yao", "鼎:Đỉnh:ding", "炉:Lô:lu", "符:Phù:fu", "宝:Bảo:bao",
    "塔:Tháp:ta", "印:Ấn:yin", "幡:Phan:fan", "珠:Châu:zhu", "镜:Kính:jing", "扇:Phiến:shan",
    "镯:Trạc:zhuo", "簪:Trâm:zan", "佩:Bội:pei", "戒:Giới:jie", "国:Quốc:guo", "兵:Binh:bing",
    "卒:Tốt:zu", "卿:Khanh:qing", "岛:Đảo:dao", "帮:Bang:bang", "儒:Nho:ru", "鬼:Quỷ:gui",

    # Romance, dialogue, emotions, body parts
    "你:Bạn:ni", "我:Tôi:wo", "他:Anh:ta", "她:Cô:ta", "它:Nó:ta", "们:Các:men",
    "这:Này:zhe", "那:Na:na", "哪:Nào:na", "谁:Ai:shei", "什:Gì:shen", "么:Sao:me",
    "不:Bất:bu", "是:Thị:shi", "在:Tại:zai", "有:Hữu:you", "没:Một:mei", "好:Hảo:hao",
    "看:Khán:kan", "说:Thuyết:shuo", "想:Tưởng:xiang", "要:Yếu:yao", "给:Cấp:gei",
    "被:Bị:bei", "让:Nhượng:rang", "去:Khứ:qu", "来:Lai:lai", "回:Hồi:hui",
    "做:Tố:zuo", "作:Tác:zuo", "得:Đắc:de", "着:Trứ:zhe", "了:Liễu:le",
    "过:Quá:guo", "到:Đáo:dao", "起:Khởi:qi", "开:Khai:kai", "停:Đình:ting",
    "关:Quan:guan", "死:Tử:si", "活:Hoạt:huo", "生:Sinh:sheng", "命:Mệnh:ming",
    "吻:Vấn:wen", "亲:Thân:qin", "抱:Bão:bao", "搂:Lâu:lou", "抚:Phủ:fu",
    "摸:Mạc:mo", "咬:Ngáp:yao", "尝:Thường:chang", "品:Phẩm:pin", "甜:Điềm:tian",
    "蜜:Mật:mi", "香:Hương:xiang", "软:Nhuyễn:ruan", "酥:Tô:su", "麻:Ma:ma",
    "骨:Cốt:gu", "融:Dung:rong", "化:Hóa:hua", "掉:Điệu:diao", "唇:Thuần:chun",
    "嘴:Chủy:zui", "颈:Cảnh:jing", "脖:Bột:bo", "耳:Nhĩ:er", "畔:Bạn:pan",
    "声:Thanh:sheng", "音:Âm:yin", "低:Đê:di", "轻:Khinh:qing", "娇:Kiều:jiao",
    "羞:Tu:xiu", "涩:Sáp:se", "盖:Cái:gai", "媚:Mị:mei", "柔:Nhu:rou",
    "热:Nhiệt:re", "冷:Lãnh:leng", "温:Ôn:wen", "凉:Lương:liang", "痛:Thống:tong",
    "疼:Đông:teng", "爱:Ái:ai", "恨:Hận:hen", "怜:Liên:lian", "惜:Tích:xi",
    "舍:Xả:she", "留:Lưu:liu", "走:Tẩu:zou", "离:Ly:li", "伴:Bạn:ban",
    "随:Tùy:sui", "陪:Bồi:pei", "等:Đẳng:deng", "待:Đãi:dai", "休:Hưu:xiu",
    "歇:Hiết:xie", "息:Tức:xi", "气:Khí:qi", "呼:Hô:hu", "吸:Hấp:xi",
    "喷:Phún:pen", "洒:Sái:sa", "紧:Khẩn:jin", "松:Tùng:song", "放:Phóng:fang",
    "握:Ác:wo", "抓:Trảo:zhua", "拉:Lạp:la", "扯:Xả:che", "推:Thôi:tui",
    "压:Áp:ya", "顶:Đỉnh:ding", "入:Nhập:ru", "出:Xuất:chu", "进:Tiến:jin",
    "封:Phong:feng", "闭:Bế:bi", "锁:Tỏa:suo", "解:Giải:jie", "脱:Thoát:tuo",
    "穿:Xuyên:chuan", "除:Trừ:chu", "双:Song:shuang", "臂:Tí:bi",
    "手:Thủ:shou", "足:Túc:zu", "腰:Yêu:yao", "肢:Chi:zhi", "胸:Hung:xiong",
    "怀:Hoài:huai", "身:Thân:shen", "躯:Khu:qu", "体:Thể:ti", "美:Mỹ:mei",
    "丽:Lệ:li", "艳:Diễm:yan", "绝:Tuyệt:jue", "极:Cực:ji",
    "真:Chân:zhen", "正:Chính:zheng", "确:Xác:que", "实:Thực:shi", "现:Hiện:xian",
    "从:Tòng:cong", "前:Tiền:qian", "将:Tương:jiang", "当:Đương:dang", "初:Sơ:chu",
    "终:Chung:zhong", "完:Hoàn:wan", "全:Toàn:quan", "都:Đô:dou",
    "尽:Tẫn:jin", "无:Vô:wu", "非:Phi:fei", "只:Chỉ:zhi",
    "独:Độc:du", "孤:Cô:gu", "对:Đối:dui", "群:Quần:qun", "众:Chúng:zhong",
    "诸:Chư:zhu", "各:Các:ge", "每:Mỗi:mei", "同:Đồng:tong", "异:Dị:yi",
    "合:Hợp:he", "分:Phân:fen", "散:Tán:san", "聚:Tụ:ju", "集:Tập:ji",
    "见:Kiến:jian", "识:Thức:shi", "知:Tri:zhi", "晓:Hiểu:xiao", "明:Minh:ming",
    "暗:Ám:an", "黑:Hắc:hei", "日:Nhật:ri", "月:Nguyệt:yue", "星:Tinh:xing",
    "光:Quang:guang", "辉:Huy:hui", "芒:Mang:mang", "耀:Diệu:yao", "照:Chiếu:zhao",
    "映:Ánh:ying", "发:Phát:fa", "显:Hiển:xian", "露:Lộ:lu", "藏:Tàng:cang",
    "隐:Ẩn:yin", "逃:Đào:tao", "避:Tị:bi", "闪:Thiểm:shan",
    "胜:Thắng:sheng", "败:Bại:bai", "赢:Doanh:ying", "输:Thâu:shu", "战:Chiến:zhan",
    "斗:Đấu:dou", "击:Kích:ji", "杀:Sát:sha", "灭:Diệt:mie", "亡:Vong:wang",
    "伤:Thương:shang", "损:Tổn:sun", "残:Tàn:can", "废:Phế:fei", "救:Cứu:jiu",
    "治:Trị:zhi", "医:Y:yi", "愈:Dũ:yu", "复:Phục:fu", "醒:Tỉnh:xing", "梦:Mộng:meng",
    "虚:Hư:xu", "空:Không:kong", "灵:Linh:ling", "魄:Phách:po", "魂:Hồn:hun",
    "意:Ý:yi", "志:Chí:zhi", "心:Tâm:xin", "思:Tư:si", "情:Tình:qing", "感:Cảm:gan",
    "念:Niệm:nian", "忆:Ức:yi", "忘:Vong:wang", "记:Ký:ji", "言:Ngôn:yan",
    "语:Ngữ:yu", "话:Thoại:hua", "谈:Đàm:tan", "论:Luận:lun", "问:Vấn:wen", "答:Đáp:da",
    "应:Ứng:ying", "定:Định:ding", "威:Uy:wei", "静:Tĩnh:jing", "默:Mặc:mo",
    "平:Bình:ping", "快:Khoái:kuai", "乐:Lạc:le", "喜:Hỷ:xi", "欢:Hoan:huan",
    "悦:Duyệt:yue", "欣:Hân:xin", "妙:Diệu:miao", "奇:Kỳ:qi", "变:Biến:bian",
    "转:Chuyển:zhuan", "移:Di:yi", "行:Hành:xing", "立:Lập:li", "坐:Tọa:zuo",
    "卧:Ngọa:wo", "躺:Thảng:tang", "睡:Thụy:shui", "床:Sàng:chuang", "房:Phòng:fang",
    "屋:Ốc:wu", "室:Thất:shi", "楼:Lâu:lou", "城:Thành:cheng", "市:Thị:shi",
    "山:Sơn:shan", "水:Thủy:shui", "川:Xuyên:chuan", "河:Hà:he", "湖:Hồ:hu", "海:Hải:hai",
    "峰:Phong:feng", "林:Lâm:lin", "木:Mộc:mu", "树:Thụ:shu", "花:Hoa:hua", "草:Thảo:cao",
    "竹:Trúc:zhu", "玉:Ngọc:yu", "金:Kim:jin", "银:Ngân:yin", "铜:Đồng:tong", "铁:Thiết:tie",
    "重:Trọng:zhong", "深:Sâu:shen", "广:Quảng:guang", "长:Trường:chang", "短:Đoản:duan",
    "远:Viễn:yuan", "近:Cận:jin", "久:Cửu:jiu", "速:Tốc:su", "慢:Mạn:man", "早:Tảo:zao",
    "春:Xuân:chun", "秋:Thu:qiu", "冬:Đông:dong", "寒:Hàn:han", "雨:Vũ:yu",
    "冰:Băng:bing", "火:Hỏa:huo", "土:Thổ:tu", "沙:Sa:sha", "天:Thiên:tian", "地:Địa:di",
    "红:Hồng:hong", "蓝:Lam:lan", "紫:Tử:zi", "绿:Lục:lv", "净:Tịnh:jing",
    "浩:Hạo:hao", "雄:Hùng:xiong", "英:Anh:ying", "俊:Tuấn:jun", "秀:Tú:xiu",
    "华:Hoa:hua", "荣:Vinh:rong", "登:Đăng:deng", "飞:Phi:fei", "落:Lạc:luo",
    "流:Lưu:liu", "涨:Trướng:zhang", "退:Thoái:tui", "安:An:an", "福:Phúc:fu",
    "吉:Cát:ji", "凶:Hung:xiong", "善:Thiện:shan", "直:Trực:zhi", "度:Độ:du",
    "量:Lượng:liang", "持:Trì:chi", "提:Đề:ti", "引:Dẫn:yin", "点:Điểm:dian",
    "教:Giáo:jiao", "收:Thu:shou", "取:Thủ:qu", "阵:Trận:zhen", "图:Đồ:tu",
    "书:Thư:shu", "字:Tự:zi", "词:Từ:ci", "诗:Thi:shi", "琴:Cầm:qin", "棋:Kỳ:qi",
    "画:Họa:hua", "影:Ảnh:ying", "法:Pháp:fa", "术:Thuật:shu", "工:Công:gong",
    "修:Tu:xiu", "练:Luyện:lian", "境:Cảnh:jing", "界:Giới:jie", "域:Vực:yu",
    "古:Cổ:gu", "今:Kim:jin", "世:Thế:shi", "代:Đại:dai", "运:Vận:yun",
    "路:Lộ:lu", "步:Bộ:bu", "求:Cầu:qiu", "本:Bản:ben", "源:Nguồn:yuan",

    # Common Given Name Characters (Male & Female)
    "毅:Nghị:yi", "睿:Duệ:rui", "轩:Hiên:xuan", "宇:Vũ:yu", "博:Bác:bo",
    "泽:Trạch:ze", "豪:Hào:hao", "杰:Kiệt:jie", "伟:Vĩ:wei", "强:Cường:qiang",
    "磊:Lỗi:lei", "军:Quân:jun", "洋:Dương:yang", "勇:Dũng:yong", "娜:Na:na",
    "敏:Mẫn:min", "娟:Quyên:juan", "芳:Phương:fang", "刚:Cương:gang", "超:Siêu:chao",
    "鹏:Bằng:peng", "斌:Bân:bin", "涛:Đào:tao", "波:Ba:bo", "凯:Khải:kai",
    "健:Kiện:jian", "鑫:Hâm:xin", "锋:Phong:feng", "翔:Tường:xiang", "瑞:Thụy:rui",
    "瑶:Dao:yao", "琪:Kỳ:qi", "琳:Lâm:lin", "婷:Đình:ting", "怡:Di:yi",
    "涵:Hàm:han", "彤:Đồng:tong", "馨:Hinh:xin", "媛:Viện:yuan", "薇:Vi:wei",
    "倩:Thiến:qian", "璐:Lộ:lu", "璇:Tuyền:xuan", "珊:San:shan", "颖:Dĩnh:ying",
    "洁:Khiết:jie", "玲:Linh:ling", "霞:Hà:xia", "萍:Bình:ping", "燕:Yến:yan",
    "哲:Triết:zhe", "瀚:Hãn:han", "墨:Mặc:mo", "渊:Uyên:yuan", "冥:Minh:ming",
    "澈:Triệt:che", "傲:Ngạo:ao", "狂:Cuồng:kuang", "霸:Bá:ba", "邪:Tà:xie",
    "玄:Huyền:xuan", "苍:Thương:cang", "穹:Khung:qiong", "乾:Càn:qian", "坤:Khôn:kun",
    "宸:Thần:chen", "煜:Dục:yu", "瑾:Cẩn:jin", "瑜:Du:yu", "曦:Hi:xi",
    "澜:Lan:lan", "汐:Tịch:xi", "洛:Lạc:luo", "笙:Sanh:sheng", "陌:Mạch:mo",
    "殇:Thương:shang", "烬:Tẫn:jin", "峥:Tranh:zheng", "嵘:Vinh:rong", "霆:Đình:ting",
    "钧:Quân:jun", "霖:Lâm:lin", "烨:Diệp:ye", "熠:Dập:yi", "曜:Diệu:yao",
    "昂:Ngẩng:ang", "昆:Côn:kun", "仑:Luân:lun", "岱:Đại:dai", "岳:Nhạc:yue",
    "屿:Dữ:yu", "洲:Châu:zhou", "川:Xuyên:chuan", "棠:Đường:tang", "薇:Vi:wei",
    "母:Mẫu:mu", "父:Phụ:fu", "爷:Gia:ye", "奶:Nãi:nai"
]

def build_hanviet_dictionary():
    char_to_hv = {}
    char_to_py = {}
    surnames = set()
    compound_surnames = set()

    for item in DATA_ENTRIES:
        parts = item.strip().split(":")
        if len(parts) != 3:
            continue
        zh, hv, py = parts
        char_to_hv[zh] = hv
        char_to_py[zh] = py.lower()

    # Known single-char Chinese surnames
    raw_surnames = (
        "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
        "戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐"
        "费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄"
        "和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁"
        "杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍"
        "虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚"
        "程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓"
        "牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙"
        "叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴郁胥能苍双"
        "闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍郤璩桑桂濮牛寿通边扈燕冀郏浦尚农"
        "温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘"
        "匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空"
        "曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公"
    )
    for s in raw_surnames:
        surnames.add(s)

    compound_list = [
        "欧阳", "司马", "上官", "诸葛", "皇甫", "尉迟", "公孙", "慕容",
        "独孤", "澹台", "轩辕", "令狐", "东方", "西门", "赫连", "钟离",
        "长孙", "夏侯", "诸葛", "宇文"
    ]
    for cs in compound_list:
        compound_surnames.add(cs)

    output = {
        "char_to_hanviet": char_to_hv,
        "char_to_pinyin": char_to_py,
        "surnames": sorted(list(surnames)),
        "compound_surnames": sorted(list(compound_surnames)),
    }

    out_file = os.path.join(os.path.dirname(__file__), "data", "hanviet_dict.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Han-Viet dictionary generated successfully at {out_file} with {len(char_to_hv)} characters.")
    return output

if __name__ == "__main__":
    build_hanviet_dictionary()
