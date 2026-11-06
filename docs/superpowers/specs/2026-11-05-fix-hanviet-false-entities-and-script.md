# Specification: Khắc Phục Nhận Diện Thực Thể Hán - Việt Sai Lệch & Chuẩn Hóa Kịch Bản Dịch

- **Date:** 2026-11-05
- **Status:** Approved / Đang triển khai
- **Model:** Gemini 3.8 Flash
- **Reference Project:** `3553adb1-1c86-411e-8db3-4fbd345ad464`

---

## 1. Bối Cảnh & Vấn Đề Gốc Rễ (Root Cause Analysis)

Sau khi dịch toàn bộ 1.602 phân đoạn của kịch bản phim ngắn hào môn Thẩm Gia, bản dịch tiếng Việt xuất hiện nhiều lỗi nghiêm trọng phá vỡ ngữ cảnh kịch bản:

1. **Lỗi ngụy tạo tên riêng do thuật toán tham lam trong `app/hanviet.py`:**
   - Danh sách họ (`surnames`) lấy toàn bộ Bách Gia Tính (~407 họ), bao gồm cả các chữ vốn là đại từ, liên từ, danh từ hoặc động từ rất phổ biến như `任` (nhậm), `终` (chung), `那` (na), `房` (phòng), `明` (minh), `别` (biệt), `能` (năng)...
   - Khi quét câu thoại:
     - `任何人` (bất kỳ ai) $\rightarrow$ nhận diện thành tên riêng `Nhậm Hà Nhân`.
     - `任何` $\rightarrow$ nhận diện thành `Nhậm Hà`.
     - `终于` (cuối cùng) $\rightarrow$ nhận diện thành `Chung Vu`.
     - `那个` (cái đó / ờ thì...) $\rightarrow$ nhận diện thành `Đó Cá` (do `hanviet_dict.json` ánh xạ `那` -> `Đó`, `个` -> `Cá`).
     - `房子这么大` (nhà to thế này) $\rightarrow$ nhận diện thành `Phòng Tử rộng thế này`.
     - `说明沈家...` (cho thấy nhà họ Thẩm) $\rightarrow$ nhận diện cắt khúc chữ `明` ghép với `沈家` thành tên người `Minh Thẩm Gia`.
     - `沈伯母` (Thẩm bá mẫu / Bác gái Thẩm) $\rightarrow$ bị cắt cụt thành `Thẩm Bá` và để sót chữ `母` khiến dịch thành `Thẩm Bá mẹ, đừng khách sáo`.
2. **Tiền xử lý tiêm chuỗi Hán - Việt thô vào Prompt LLM (`enhance_chinese_with_hanviet_entities`):**
   - Trước khi gửi câu thoại sang Groq / Gemini, hệ thống tự ý thế các từ tiếng Trung bằng các tên giả cầy ở trên vào `translator_zh_list`.
   - LLM khi nhận được câu đã bị chèn chuỗi dị hợm ("Đó Cá 我什么都不要", "我不会让 Nhậm Hà Nhân 把 Thẩm Nghị 赶出去") sẽ tin rằng đây là nhân vật trong phim và dịch bám theo tên đó.
3. **Từ điển `hanviet_dict.json` bị lỗi ánh xạ:**
   - Chữ `那` bị gán là `Đó` (nghĩa dịch) thay vì âm Hán - Việt chuẩn là `Na`.
   - Thiếu các ký tự xưng hô gia tộc (`母`, `父`, `爷`, `奶`...) dẫn tới tách cụm tên - chức danh bị dị tật.
4. **Lỗi ASR & Lệch nhịp Dubbing:**
   - Whisper nhận nhầm `马场` (mã trường / bãi ngựa) thành `鸟场` (điểu trường) $\rightarrow$ dịch thành `sân chim`.
   - Một số câu ngắn (0.2s - 0.5s) bị dịch quá dài khiến tốc độ phát TTS bị ép kịch trần 1.35x.

---

## 2. Mục Tiêu & Yêu Cầu Thiết Kế

1. **Khắc phục triệt để `app/hanviet.py`:**
   - Mở rộng `NON_GIVEN_NAME_CHARS`: Bổ sung các hư từ, lượng từ, hậu tố danh từ, đại từ, giới từ, danh từ chỉ thời gian/nơi chốn, từ xưng hô họ hàng (`何`, `个`, `子`, `于`, `人`, `家`, `母`, `父`, `爸`, `妈`, `伯`, `叔`, `姑`, `姨`, `舅`, `哥`, `弟`, `姐`, `妹`, `爷`, `奶`, `事`, `物`, `处`, `点`, `时`, `分`, `秒`, `年`, `月`, `日`, `天`, `里`, `边`, `面`, `外`, `内`, `前`, `后`, `些`, `样`, `么`).
   - Mở rộng `COMMON_ZH_VOCABULARY_STOPWORDS`: Thêm toàn bộ các từ đa âm tiết thông dụng dễ bị bắt nhầm họ (`任何`, `任何人`, `终究`, `终于`, `房子`, `房间`, `说明`, `明白`, `明确`, `那个`, `那些`, `那样`, `那里`, `那儿`, `那边`, `那么`, `那是`, `那就`, `那怎么行`...).
   - Chặn nhận diện tên riêng khi ký tự bắt đầu nằm trong từ ghép phía trước (ví dụ `明` trong `说明`, `证明`, `表明`...).
   - Phân loại họ: Các chữ họ trùng từ vựng thông dụng (`那`, `房`, `终`, `明`, `任`, `能`, `全`, `通`, `车`, `井`, `水`, `山`, `家`, `国`, `成`, `平`, `和`, `步`, `时`, `利`, `师`, `融`, `后`, `红`, `空`, `别`) chỉ được match khi đi kèm danh xưng rõ ràng (`总`, `少`, `先生`, `女士`, `小姐`, `夫人`, `伯`, `叔`...) hoặc là tên 3 chữ có cấu trúc danh từ riêng hợp lệ.
2. **Cập nhật từ điển `app/hanviet_builder.py` & `hanviet_dict.json`:**
   - Đổi `那:Đó:na` thành `那:Na:na`.
   - Bổ sung `母:Mẫu:mu`, `父:Phụ:fu`, `爷:Gia:ye`, `奶:Nãi:nai`.
3. **Cải tiến `refine_vietnamese_dub_line` (`app/translator.py`):**
   - Thêm bộ lọc dọn dẹp các cụm từ dị tật nếu vô tình còn sót (`Đó Cá`, `Đó Chẩm`, `Phòng Tử`, `Nhậm Hà Nhân`, `Chung Vu`, `Minh Thẩm Gia`, `Thẩm Bá mẹ`, `sân chim`, `vé Quốc Cơ`).
   - Cân chỉnh độ dài các câu ngắn đếm nhịp (`三二一` $\rightarrow$ `Ba, hai, một`, không sinh thừa chữ `Bốn`).
4. **Chuẩn hóa & Sửa chữa dữ liệu dự án hiện tại:**
   - Chạy script chuẩn hóa tự động quét và sửa toàn bộ các câu dính lỗi trong `app/projects/3553adb1-1c86-411e-8db3-4fbd345ad464/segments.json`.

