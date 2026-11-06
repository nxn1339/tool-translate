# Implementation Plan: Khắc Phục Nhận Diện Thực Thể Hán - Việt Sai Lệch & Chuẩn Hóa Kịch Bản Dịch

- **Date:** 2026-11-05
- **Status:** In Progress
- **Spec Reference:** `docs/superpowers/specs/2026-11-05-fix-hanviet-false-entities-and-script.md`
- **Model:** Gemini 3.8 Flash

---

## Các Bước Triển Khai

### Phase 1: Chuẩn Hóa Từ Điển Hán - Việt
- [ ] `app/hanviet_builder.py`:
  - Đổi `那:Đó:na` thành `那:Na:na`.
  - Bổ sung `母:Mẫu:mu`, `父:Phụ:fu`, `爷:Gia:ye`, `奶:Nãi:nai`.
  - Chạy `hanviet_builder.py` để sinh lại `app/data/hanviet_dict.json`.

### Phase 2: Nâng Cấp Thuật Toán Nhận Diện Tên Riêng trong `app/hanviet.py`
- [ ] Mở rộng `NON_GIVEN_NAME_CHARS` chặn các ký tự không bao giờ là tên đệm/tên chính:
  - Bổ sung hư từ, lượng từ, đại từ, họ hàng: `何`, `个`, `子`, `于`, `人`, `家`, `母`, `父`, `爸`, `妈`, `伯`, `叔`, `姑`, `姨`, `舅`, `哥`, `弟`, `姐`, `妹`, `爷`, `奶`, `事`, `物`, `处`, `点`, `时`, `分`, `秒`, `年`, `月`, `日`, `天`, `里`, `边`, `面`, `外`, `内`, `前`, `后`, `些`, `样`, `么`.
- [ ] Mở rộng `COMMON_ZH_VOCABULARY_STOPWORDS`:
  - Thêm hàng loạt từ vựng thông dụng dễ bị bắt nhầm họ:
    `任何`, `任何人`, `任何事`, `任何东西`, `任何差错`, `终究`, `终于`, `终点`, `终端`, `终身`, `终生`, `房子`, `房间`, `房屋`, `房产`, `房租`, `房东`, `说明`, `明白`, `明确`, `明天`, `明日`, `明显`, `明智`, `那个`, `那个人`, `那些`, `那时`, `那里`, `那儿`, `那边`, `那么`, `那样`, `那是`, `那就`, `那怎么行`.
- [ ] Tách danh sách họ thành:
  - `COMMON_SURNAMES` (Các họ phổ thông: Thẩm, Tiết, Tiêu, Bạch, Lâm, Sở, Diệp, Triệu, Phó, Tô, v.v.).
  - `AMBIGUOUS_SURNAMES` (Các chữ trùng từ vựng đời thường: `那`, `房`, `终`, `明`, `任`, `能`, `全`, `通`, `车`, `井`, `水`, `山`, `家`, `国`, `成`, `平`, `和`, `步`, `时`, `利`, `师`, `融`, `后`, `红`, `空`, `别`, `各`, `每`).
  - Quy tắc: Các chữ thuộc `AMBIGUOUS_SURNAMES` chỉ được match khi có danh xưng đi kèm (`title_affixes`) hoặc đi sau tiền tố danh xưng.
- [ ] Trong `extract_chinese_names_in_text`:
  - Thêm kiểm tra tiền tố từ vựng: Nếu chữ cái đứng trước `i` cùng với `c` tạo thành từ ghép thông dụng (như `说明`, `证明`, `表明`, `声明`, `关于`, `对于`, `刚才`...), bỏ qua không coi `c` là họ.
  - Cấm tên 3 chữ mà ký tự thứ 2 lại là một họ lớn (`cand3[1] in surnames`).

### Phase 3: Bổ Sung Hậu Xử Lý & Chuẩn Hóa Phụ Đề trong `app/translator.py`
- [ ] Trong `refine_vietnamese_dub_line`:
  - Thêm bộ quy tắc chuẩn hóa các cụm từ bị dịch lệch:
    - `"Đó Cá"` $\rightarrow$ `"Ờ thì"` / `"Cái đó"`
    - `"Đó Chẩm, được rồi"` $\rightarrow$ `"Thế sao được"`
    - `"Phòng Tử"` $\rightarrow$ `"Căn nhà"`
    - `"Nhậm Hà Nhân"` $\rightarrow$ `"bất kỳ ai"`
    - `"Nhậm Hà"` $\rightarrow$ `"bất kỳ ai"` / `"bất kỳ"`
    - `"Chung Vu"` $\rightarrow$ `"cuối cùng"` / `"rốt cuộc"`
    - `"Minh Thẩm Gia"` $\rightarrow$ `"nhà họ Thẩm"`
    - `"Thẩm Bá mẹ"` $\rightarrow$ `"Bác gái Thẩm"`
    - `"sân chim"` $\rightarrow$ `"trường đua ngựa"` (nếu câu gốc chứa `逐风` / `马场`)
    - `"vé Quốc Cơ"` $\rightarrow$ `"vé máy bay về nước"`
    - `"Bốn, ba, hai, một"` $\rightarrow$ `"Ba, hai, một"` (khi câu gốc là `三二一`)

### Phase 4: Sửa Chữa Trực Tiếp File Dự Án `segments.json` & Kiểm Chứng
- [ ] Viết script quét và sửa toàn bộ các lỗi đã phát hiện trong file `app/projects/3553adb1-1c86-411e-8db3-4fbd345ad464/segments.json`.
- [ ] Kiểm thử tự động trên bộ test mẫu (unit test cho `hanviet.py`).
- [ ] Biên dịch kiểm tra cú pháp Python toàn bộ dự án (`py_compile`).
- [ ] Lập báo cáo nghiệm thu `docs/superpowers/evidence/2026-11-05-fix-hanviet-false-entities-and-script.md`.

