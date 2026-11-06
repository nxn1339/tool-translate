# Specification: Sửa hiển thị Sub/Làm mờ và Cơ chế Báo lỗi/Tạo lại câu lồng tiếng

- **Date:** 2026-11-01
- **Status:** Draft / Chờ duyệt

---

## 1. Bối Cảnh & Vấn Đề
1. **Vấn đề 1 (Sub & Blur):**
   - Phụ đề video sau khi xuất ra (hardsub qua FFmpeg) bị mờ căm, viền đen nhòe nhoẹt, chữ trông mảnh và nhỏ hơn hẳn bản xem trước.
   - Dải làm mờ nền (mask blur) trong video xuất ra chỉ là `boxblur` thuần túy, thiếu lớp nền đen trong suốt 45% (`background-color: rgba(0,0,0,0.45)`) dẫn tới khi nền là áo sáng màu thì dải mờ bị biến thành màu trắng xám đục, làm chữ trắng bị chìm.
2. **Vấn đề 2 (Lồng tiếng 2 giọng & Xử lý lỗi):**
   - Khi chọn giọng CapCut (ví dụ Cô gái hoạt ngôn), hệ thống gọi API với 10 luồng song song (`Semaphore(10)`). Khi gặp câu bị timeout / rate limit, code âm thầm tự đổi sang Edge-TTS Hoài My làm lẫn 2 giọng trong 1 video.
   - Yêu cầu: Giữ nguyên 10 luồng, KHÔNG tự ý đổi giọng sang Hoài My. Nếu câu nào lỗi thì đánh dấu chưa tạo được, hiển thị rõ tại Bảng Phụ Đề & Bản Dịch, và cung cấp nút bấm để chỉ tạo lại các câu bị lỗi.

---

## 2. Thiết Kế Kỹ Thuật

### 2.1. Xử lý Vấn đề 1: Đồng bộ Sub & Dải Che Mờ
- **File:** `app/merger.py`
  - Bỏ triệt để tag `\blur2.5` trong `pos_tag` của hàm `export_ass_file`.
  - Căn chỉnh `Outline` và `Shadow` trong file ASS để tương xứng với CSS `-webkit-text-stroke: 3px` và drop-shadow đậm.
  - Cập nhật filter graph che mờ:
    ```
    [v_crop]crop=w={mw}:h={mh}:x={mx}:y={my},boxblur=15:5,drawbox=x=0:y=0:w={mw}:h={mh}:color=black@0.45:t=fill[v_blur];
    [v_main][v_blur]overlay=x={mx}:y={my}[v_masked];
    ```
    Tái hiện chính xác 100% hiệu ứng kính mờ tối màu của CSS `backdrop-filter: blur(14px)` + `rgba(0,0,0,0.45)`.

### 2.2. Xử lý Vấn đề 2: Giữ 10 luồng, Ghi nhận lỗi & Nút Tạo lại câu lỗi
- **File:** `app/tts.py`
  - Trong `generate_single_tts`: Khi CapCut TTS thất bại sau các lần retry, **KHÔNG fallback sang Edge-TTS Hoài My**. Trả về trạng thái thất bại.
  - Trong `_process_single_segment`: Nếu thất bại, đánh dấu `seg["tts_error"] = True`, `seg["audio_path"] = None`, không lưu hash thành công vào `seg["tts_raw_hash"]`.
  - Hỗ trợ tham số `failed_only: bool = False` trong `generate_tts_for_segments`: Khi bật, chỉ lọc và chạy TTS cho các câu `seg["translation"] and (not seg.get("audio_path") or seg.get("tts_error"))`.
- **File:** `app/main.py`
  - Thêm cờ `failed_only: Optional[bool] = False` vào endpoint `POST /api/project/{project_id}/generate-tts`.
- **File:** `app/static/index.html` & `app/static/app.js`
  - Tại thanh công cụ `editor-header-actions` của **Bảng Phụ Đề & Bản Dịch**: Thêm nút `btn-retry-failed-tts` ("Tạo lại câu lỗi (X)") chỉ xuất hiện khi có câu lỗi.
  - Trong bảng câu thoại (`subtitle-table-body`): Thêm nhãn cảnh báo đỏ `<span class="badge-tts-error"><i class="fa-solid fa-circle-exclamation"></i> Lỗi giọng</span>` tại các dòng chưa tạo được âm thanh.
  - Khi bấm nút "Tạo lại câu lỗi", chỉ gửi yêu cầu chạy lại cho đúng các câu chưa hoàn thành, giữ nguyên 10 luồng và cập nhật ngay vào bảng.

