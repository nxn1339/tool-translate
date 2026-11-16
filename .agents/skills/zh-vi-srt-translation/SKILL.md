---
name: zh-vi-srt-translation
description: >-
  Use when translating Chinese subtitle files (.srt) or scripts into natural,
  expressive Vietnamese subtitles while strictly preserving 100% of the original
  timeline, block numbering, and layout.
---

# Kỹ năng Dịch thuật Phụ đề Kịch bản Trung - Việt (.SRT)

Skill này quy chuẩn hóa quy trình tiếp nhận file phụ đề `.srt` hoặc kịch bản tiếng Trung, phân tích bối cảnh câu chuyện, quan hệ nhân vật và chuyển ngữ sang tiếng Việt tự nhiên, giàu cảm xúc, chuẩn nhịp điệu phim ảnh/lồng tiếng.

---

## Khi nào sử dụng Skill này

- Khi người dùng gửi file `.srt`, đường dẫn file phụ đề, hoặc một đoạn script tiếng Trung và yêu cầu dịch sang tiếng Việt.
- Khi cần dịch kịch bản phim ngắn, tiểu phẩm, phim truyền hình, drama mạng từ tiếng Trung sang tiếng Việt giữ nguyên timeline.

---

## Nguyên tắc Cốt lõi Bắt buộc (Core Invariants)

1. **Bảo toàn 100% Timeline & Bố cục:**
   - Tuyệt đối không thêm, xóa, gộp, tách dòng hoặc thay đổi thứ tự các khối timeline.
   - Số thứ tự (Index) và mốc thời gian (`00:00:00,000 --> 00:00:00,000`) phải giữ nguyên từng ký tự và khoảng trắng.
   - Tổng số khối phụ đề ở bản dịch tiếng Việt phải bằng chính xác 100% số khối của bản gốc tiếng Trung.

2. **Chỉ dịch nội dung thoại:**
   - Chỉ chuyển ngữ phần văn bản tiếng Trung sang tiếng Việt.
   - Giữ nguyên các ký hiệu định dạng đặc biệt, dấu câu gốc hoặc cấu trúc dòng bên trong khối nếu có.

3. **Văn phong Tự nhiên & Thoát ý:**
   - Dịch theo văn phong giao tiếp đời thường của người Việt, đậm chất ngôn ngữ kịch bản / phim ảnh.
   - Tránh dịch thô theo kiểu "word-by-word", máy dịch (Google Translate thô) hay lạm dụng âm Hán Việt cứng nhắc.
   - Ưu tiên dịch thoát ý, giữ trọn vẹn ngữ khí, sự châm biếm, cay đắng, ngọt ngào hay bi kịch của câu chuyện.

4. **Chuẩn hóa Xưng hô & Đại từ Nhân xưng:**
   - Phân tích mối quan hệ nhân vật trước khi dịch (vợ chồng, người yêu cũ, mẹ - con, bạn thân, cấp trên - cấp dưới, đối thủ...).
   - Lựa chọn đại từ nhân xưng phù hợp với thân phận và sự biến chuyển tâm lý trong từng cảnh:
     - Giữa người yêu cũ vừa hận vừa yêu: *anh - tôi*, *em - tôi*, chuyển thành *anh - em* khi trải lòng hoặc dỗ dành.
     - Bạn bè thân thiết: *cậu - tớ*, *mày - tao* (đanh đá, chân thật).
     - Bố mẹ - con cái: *mẹ - con*, *ba - con*.
     - Giữ sự nhất quán xuyên suốt toàn bộ câu chuyện.

5. **Tối ưu Độ dài theo Thời lượng Timeline (Sub/Dub Rhythm):**
   - Rút gọn khéo léo những câu chữ Hán quá dài so với thời lượng hiển thị (ví dụ 1.0 - 1.5 giây), đảm bảo người xem đọc kịp và diễn viên lồng tiếng nói vừa nhịp.
   - Câu rút gọn phải đủ ý, đắt giá, tuyệt đối không dịch cụt ngủn hoặc làm mất chi tiết quan trọng.

6. **Trung thực với Cốt truyện & Cảm xúc:**
   - Không tự ý thêm thắt các tình tiết hư cấu ngoài nguyên tác.
   - Thấu hiểu và truyền tải đúng tâm trạng nhân vật (tức giận, bất lực, đau xót, mỉa mai, nuông chiều).

7. **Quy chuẩn Lưu trữ & Đầu ra (Output & File Storage Standard):**
   - Chỉ xuất nội dung bản dịch tiếng Việt định dạng `.srt` chuẩn, không kèm bất kỳ giải thích, nhận xét, ghi chú dịch thuật hay lời bình thừa thãi.
   - **Thư mục lưu trữ bắt buộc:** Sau khi dịch xong, bắt buộc lưu file kết quả vào thư mục `file_dich/` (đường dẫn: `c:\project\tool-translate\file_dich\`).
   - **Quy tắc đặt tên file theo ngày:** Tên file phải chứa ngày thực hiện dịch theo định dạng `YYYY-MM-DD.srt` (ví dụ: `2026-11-16.srt`). Nếu có tên file gốc hoặc dịch nhiều tập/file trong cùng một ngày, đặt theo định dạng `YYYY-MM-DD_<tên_file_gốc>.srt` để tránh ghi đè.
   - Bản dịch lưu file phải đảm bảo mã hóa UTF-8.

---

## Quy trình Thực hiện Chuẩn 4 Bước

### Bước 1: Tiếp nhận & Phân tích Kịch bản (Script Context Analysis)
- Đọc lướt qua toàn bộ file để nắm bắt:
  - **Tuyến nhân vật:** Tên gọi, giới tính, quan hệ xã hội, xung đột cốt lõi.
  - **Bối cảnh:** Hào môn, thanh xuân vườn trường, đô thị hiện đại, công sở...
  - **Dòng cảm xúc:** Nhịp điệu tình cảm (từ xa cách, căm hận sang rung động, giải tỏa hiểu lầm).

### Bước 2: Xử lý Lỗi OCR Tiếng Trung (Nếu có)
- Bản subtitle tiếng Trung trích xuất từ video thường có lỗi OCR:
  - Chữ bị đứt đoạn, mất nét, hoặc nhầm chữ đồng âm (ví dụ: `入费豪门` ➔ `入赘豪门`, `彼止` ➔ `彼此`).
  - Dấu ấn bản quyền/watermark của công cụ tạo sub (như `AI牛成`, `成`, `2023...`).
  - Cần căn cứ ngữ cảnh câu trước và câu sau để dịch đúng nghĩa thực của câu thoại thay vì dịch mù quáng theo chữ sai.

### Bước 3: Dịch thuật & Căn chỉnh Khối Subtitle
- Dịch từng khối timeline, đối chiếu liên tục với ngữ cảnh câu liền trước và liền sau.
- Kiểm tra tính mạch lạc của hội thoại giữa các nhân vật.

### Bước 4: Kiểm tra Số lượng & Lưu File vào `file_dich`
- Kiểm tra số lượng block: `count(vietnamese_blocks) == count(chinese_blocks)`.
- Đảm bảo định dạng chuẩn `.srt`:
  ```text
  1
  00:00:01,000 --> 00:00:01,500
  Cô thua rồi nhé!

  2
  00:00:01,500 --> 00:00:02,500
  Mau gọi điện cho người yêu cũ đi,
  ```
- **Lưu file kết quả:**
  - Ghi file vào thư mục `c:\project\tool-translate\file_dich\`.
  - Đặt tên file theo ngày hôm đó: `file_dich/YYYY-MM-DD.srt` hoặc `file_dich/YYYY-MM-DD_<tên_file_gốc>.srt`.

