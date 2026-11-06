# Implementation Plan: Sửa hiển thị Sub/Làm mờ & Cơ chế Báo lỗi/Tạo lại câu lồng tiếng

- **Date:** 2026-11-01
- **Status:** Đã hoàn thành triển khai

---

## Các Bước Triển Khai

### Phase 1: Xử lý Vấn đề 1 (Sub sắc nét & Dải che mờ chuẩn xem trước)
- [x] `app/merger.py`:
  - Xóa bỏ `\blur2.5` trong `pos_tag` của `export_ass_file`.
  - Cập nhật độ dày viền chữ `outline_width` và bóng đổ `shadow_val` trong ASS để chữ nổi bật, sắc sảo như CSS xem trước.
  - Thêm `drawbox=x=0:y=0:w={mw}:h={mh}:color=black@0.45:t=fill` vào chuỗi filter `boxblur` để tạo lớp phủ tối mờ giống hệt `background-color: rgba(0, 0, 0, 0.45)`.

### Phase 2: Xử lý Vấn đề 2 (Giữ 10 luồng, Chặn đổi giọng, Báo lỗi & Retry)
- [x] `app/tts.py`:
  - Trong `generate_single_tts`: Xóa bỏ việc tự động fallback sang `female_hoaimy`. Nếu CapCut thất bại sau 3 lần retry thì trả về `False`.
  - Trong `_process_single_segment`: Gắn cờ `seg["tts_error"] = True`, `seg["audio_path"] = None` khi tạo thất bại. Không cache hash thành công.
  - Thêm tham số `failed_only: bool = False` cho `generate_tts_for_segments` để hỗ trợ chạy riêng cho các câu bị lỗi.
- [x] `app/main.py`:
  - Cập nhật model `ProjectGenerateTTSRequest` và endpoint `POST /api/project/{project_id}/generate-tts` nhận thêm `failed_only: bool = False`.

### Phase 3: Giao diện người dùng (Bảng Phụ Đề & Bản Dịch)
- [x] `app/static/index.html`:
  - Thêm nút `btn-retry-failed-tts` vào `editor-header-actions` của Bảng Phụ Đề & Bản Dịch (ẩn mặc định, chỉ hiện khi có câu lỗi).
- [x] `app/static/app.js`:
  - Trong `renderSegmentsTable`: Hiển thị icon/badge cảnh báo đỏ tại cột Thao tác hoặc Bản dịch cho các câu `seg.tts_error` hoặc chưa có file audio.
  - Sau khi chạy xong tạo giọng đọc: Quét số câu bị lỗi. Nếu > 0, hiển thị nút `Tạo lại câu lỗi (X câu)` trên header của Bảng Phụ Đề.
  - Gắn sự kiện click cho nút `btn-retry-failed-tts`: Gửi request tạo lại đúng các câu bị lỗi với `failed_only: true`.

### Phase 4: Kiểm thử & Nghiệm thu
- [x] Chạy kiểm tra cú pháp Python (`python -m py_compile`).
- [x] Kiểm tra tạo thử ASS và verify không còn tag `\blur2.5`.
- [x] Kiểm tra cơ chế retry câu lỗi hoạt động độc lập và chính xác.



### Phase 5: Tinh chỉnh Text, Logo và Làm mờ trong suốt (Phản hồi thực tế)
- [x] Sửa cỡ chữ & độ nét phụ đề ASS: Bù trừ tỷ lệ `1.35x` để Fontsize trong ASS khớp chiều cao thực tế của CSS preview (`Fontsize: 73` thay vì 54). Tăng `Outline` và `Shadow` đanh nét chuẩn Nunito ExtraBold.
- [x] Sửa kích thước & vị trí Logo: Chuyển sang `scale=w={w}:h={h}:force_original_aspect_ratio=decrease` và căn giữa tâm `overlay=x={pos_x}+(({w}-w)/2):y={pos_y}+(({h}-h)/2)`, khớp chuẩn `object-fit: contain` của preview (108x108 thay vì 288x288).
- [x] Làm mờ trong suốt: Bỏ lệnh `drawbox` màu đen trong FFmpeg (`merger.py`) và đổi `background-color` thành `transparent` trong CSS (`style.css`), đảm bảo vùng mờ hoàn toàn trong suốt tự nhiên không chèn dải màu.

### Phase 6: Tinh chỉnh khớp Pixel-Perfect (Fontsize 54, Kính mờ trong suốt, Căn Y Logo)
- [x] Sửa cỡ chữ & viền ASS: Đưa Fontsize về chuẩn 54 (bỏ bù 1.35x), Outline: 3.8, Shadow: 2.2. Khớp 100% tỷ lệ preview browser.
- [x] Sửa làm mờ kính trong suốt: oxblur=20:5,drawbox=color=black@0.32:t=fill trung hòa triệt để màu vàng của phụ đề gốc tiếng Trung mà vẫn trong suốt nhìn thấu video nền. Cập nhật style.css đồng bộ 
gba(0,0,0,0.32) và ackdrop-filter: blur(14px).
- [x] Sửa logo watermark: Thu hẹp tỷ lệ scale 90% (it_w=259, fit_h=97) bù trừ padding container CSS, căn giữa Y và cộng offset +4px hạ đáy banner xanh của logo khớp đường lưới cửa Nhật Bản như bản xem trước.

### Phase 7: Hoàn thiện Triệt để Khớp Pixel & Căn giữa Tâm Hình học
- [x] Cỡ chữ ASS: Fontsize 74 (chiều cao chữ hoa đạt chuẩn 54px khớp 100% bản xem trước), Outline 3.4px, Shadow 2.2px.
- [x] Căn giữa tâm: Bù trừ tọa độ Y nâng lên 4px (cy = 966 thay vì 970), cân đối tuyệt đối khoảng cách viền trên 24px và viền dưới 23px.
- [x] Logo watermark: Scale 77% (it_h = target_lh * 0.77), căn giữa lề Y +8px, đạt chuẩn đường kính 76px.
- [x] Chống cache trình duyệt: Header 
o-cache, no-store, must-revalidate trong /api/project/{id}/video-dubbed và query timestamp ?t= trong pp.js.
