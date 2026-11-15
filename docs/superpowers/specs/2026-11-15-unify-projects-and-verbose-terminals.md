# Đặc Tả Kỹ Thuật: Đồng Bộ Quản Lý Dự Án & Terminal Tiến Trình Chi Tiết Toàn Bộ 3 Phân Hệ

## 1. Bối Cảnh & Mục Tiêu
Hệ thống hiện tại có 3 phân hệ chính:
1. **Dịch Phim & Lồng Tiếng (Dubber Studio)**: Đã có thanh quản lý dự án và terminal, nhưng log tiến trình còn thô sơ, chưa phản ánh đầy đủ từng phân đoạn (OCR/Whisper, dịch AI, TTS từng câu, tiến trình render FFmpeg).
2. **Đọc Truyện TTS (Story TTS Studio)**: Chưa có cơ chế lưu/mở dự án (chỉ lưu tạm thời gian chạy); thanh tiến trình chỉ hiển thị spinner không có số %; hoàn toàn chưa có terminal xem log tiến trình.
3. **Video Ngắn Threads / FB (Social Video Studio)**: Chưa có lưu/mở dự án (dữ liệu bài viết, bình luận, voice bị mất khi refresh); thanh tiến trình chỉ có 4 mốc nhảy thô (20%, 50%, 75%, 100%); chưa có terminal console để xem quá trình cào dữ liệu, render thẻ ảnh, tạo voice và xuất video FFmpeg.

**Mục tiêu**:
- Chuẩn hóa kiến trúc **Project Management** đồng bộ cho cả 3 phân hệ (`dubber`, `story_tts`, `social_video`), lưu trữ tập trung tại `app/projects/{id}/project.json` với trường phân loại `type`.
- Đồng bộ thanh điều khiển dự án (Project Bar) trên giao diện của cả 3 phân hệ: Đổi tên dự án, Trạng thái tự động lưu, Mở dự án, Tạo dự án mới, Lưu thủ công.
- Tích hợp **Terminal Tiến Trình Studio** đồng bộ UI (Header có 3 dot màu, tag trạng thái, nút Sao chép, nút Xóa, nút Thu gọn/Mở rộng, Auto-scroll) cho cả 3 phân hệ.
- Bổ sung **Verbose Logging & % Tiến Độ Chi Tiết**:
  - Terminal hiển thị chi tiết từng câu thoại, từng bình luận, tham số âm thanh, thời lượng, và tiến trình render.
  - Thanh tiến trình hiển thị chính xác % thực tế kèm text giải thích trực quan.
- Nâng cấp **Home Hub Recent Projects**: Danh sách dự án gần đây trên Trang Chủ phân loại rõ ràng theo từng phân hệ (badge/icon riêng), cho phép bấm "Tiếp tục" để mở đúng phân hệ và khôi phục toàn bộ trạng thái làm việc.

---

## 2. Thiết Kế Kiến Trúc & Dữ Liệu

### 2.1. Cấu Trúc Metadata Dự Án (`project.json`)
Mọi dự án đều nằm trong `app/projects/{project_id}/project.json` với schema chuẩn:
```json
{
  "id": "uuid-string",
  "name": "Tên dự án do người dùng đặt hoặc sinh tự động",
  "type": "dubber | story_tts | social_video",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "status": "draft | processing | completed | failed",
  "data": { ... } // Dữ liệu chuyên biệt cho từng loại phân hệ
}
```

#### Dữ liệu chuyên biệt theo từng `type`:
1. **`type: "dubber"`**:
   - `video_url`, `mode`, `current_step`, `mask_box`, `sub_box`, `sub_styling`, `voice`, `bg_volume`, `tts_volume`, `logo_box`, `segments_count`, `has_raw_video`, `has_dubbed_video`.
2. **`type: "story_tts"`**:
   - `story_text`: Nội dung kịch bản hiện tại.
   - `channel_name`: Tên kênh (vd: "Hạt Tiêu Vietsub").
   - `intro_style`: Phong cách mở đầu (`storytelling`, `dramatic`, `review`, `short`, `custom`).
   - `intro_text`: Lời dẫn mở đầu.
   - `source_type`: `text` hoặc `youtube`.
   - `youtube_url`: Link video YouTube nếu lấy phụ đề từ YT.
   - `voice`: Mã giọng đọc TikTok được chọn.
   - `pause_ms`: Khoảng lặng giữa các câu (ms).
   - `stats`: `{ char_count, word_count, duration_sec, sentences_count }`.
   - `audio_url`, `srt_url`: Đường dẫn tải file nếu đã xuất bản.
3. **`type: "social_video"`**:
   - `url`: Link bài viết gốc Threads / Facebook.
   - `platform`: `threads` hoặc `facebook`.
   - `author`: `{ name, handle, avatar, is_verified }`.
   - `post_content`: Nội dung câu chuyện bài viết.
   - `post_likes`, `post_replies`, `time_ago`.
   - `post_voice`: Giọng đọc bài viết.
   - `comments`: Danh sách bình luận `[{ id, author, content, likes, time_ago, voice }]`.
   - `background_video`: Tên file footage nền.
   - `dark_mode`: boolean.
   - `video_url`: Đường dẫn tải video nếu đã xuất bản.

---

### 2.2. Kiến Trúc Terminal & Log Stream Đồng Bộ
Mỗi tác vụ dài đều hỗ trợ stream logs và progress polling theo format chuẩn:
- Mọi log ghi nhận đều định dạng: `[HH:MM:SS] [LEVEL] Message` (với LEVEL: `INFO`, `WARN`, `ERROR`, `SUCCESS`).
- Log được lưu trong bộ nhớ và đồng thời ghi vào `app/projects/{id}/project_logs.json`.
- Cấu trúc phản hồi polling:
  ```json
  {
    "status": "processing | completed | failed",
    "progress": 45,
    "message": "Đang sinh giọng đọc AI câu 15/30...",
    "logs": [
      "[12:30:00] [INFO] Bắt đầu phân tích văn bản kịch bản...",
      "[12:30:02] [INFO] Đã tách thành 30 câu thoại ngắn phù hợp nhịp đọc.",
      "[12:30:03] [INFO] [Câu 1/30] Giọng 'Cô Gái Hoạt Ngôn' -> Đang gọi CapCut TTS API...",
      "[12:30:04] [SUCCESS] [Câu 1/30] Hoàn tất đoạn âm thanh 2.4s (57.6 KB)."
    ]
  }
  ```

---

## 3. Chi Tiết Nâng Cấp Từng Phân Hệ

### 3.1. Phân Hệ Đọc Truyện TTS (`#story-tts-view`)
1. **Project Control Bar**:
   - Tích hợp thanh quản lý dự án trên cùng:
     - Biểu tượng mic hồng + Tên dự án (click để sửa đổi)
     - Badge "Studio Đọc Truyện" + Trạng thái lưu (Tự động lưu / Chưa lưu)
     - Nút "Mở Dự Án" (kèm popup danh sách dự án đọc truyện đã lưu)
     - Nút "Dự Án Mới" (tạo dự án trống mới)
     - Nút "Lưu Ngay"
2. **Terminal Console & Progress %**:
   - Đặt ngay bên dưới khối Tạo Audio / Kết quả (hoặc full-width chân trang).
   - Thanh tiến trình có text phần trăm rõ ràng (`0%` -> `100%`) cùng số câu hoàn thành / tổng số câu.
   - Background worker không đồng bộ cho tác vụ synthesize thay vì block request. Endpoint mới hoặc nâng cấp: `POST /api/story-tts/synthesize` trả về ngay `task_id` (hoặc `project_id`), frontend poll trạng thái `/api/story-tts/status/{id}` nhận % và log theo thời gian thực.
   - Verbose logs:
     - Trích xuất YouTube: Chi tiết phân tích URL, tìm stream timedtext tiếng Việt, số dòng đọc được.
     - Phân tích câu: Kích thước từng chunk câu, ngắt dấu câu, ước tính thời lượng.
     - TTS từng câu: Thông tin voice ID, thời gian phản hồi, dung lượng file wav, fallback silence nếu gặp lỗi.
     - Ghép FFmpeg: Ghép danh sách wav + silence snippet, mã hóa MP3 bitrate 192k.
     - Tạo file phụ đề SRT: Ghi nhận từng cue timestamp.

### 3.2. Phân Hệ Video Ngắn Threads / FB (`#social-video-view`)
1. **Project Control Bar**:
   - Tích hợp thanh quản lý dự án tương tự:
     - Tên dự án (mặc định lấy theo tác giả + tóm tắt bài viết)
     - Nút Mở / Tạo Mới / Lưu Ngay
     - Phục hồi toàn bộ form nhập liệu, danh sách comments, voice phân vai, footage nền khi tải lại dự án.
2. **Terminal Console & Progress %**:
   - Thêm Terminal Console tại Bước 4 (Kết quả & Tiến trình) và có thể toggle xem bất cứ lúc nào.
   - Chia nhỏ bước xử lý và hiển thị % mượt mà:
     - Scraping: 5% - 15% (kèm log phân tích DOM, trích xuất text, avatar, bình luận).
     - Render Thẻ Ảnh: 15% - 40% (kèm log render ảnh thẻ chính, từng thẻ comment 1..N với Playwright/Canvas).
     - Tạo Voice TTS: 40% - 70% (kèm log chi tiết từng câu của tác giả và từng bình luận với voice tương ứng).
     - Ghép Timeline & Audio: 70% - 80% (tính toán time markers cho từng visual card).
     - Render Video FFmpeg: 80% - 100% (chạy FFmpeg 9:16 trên nền video với log frame/time).

### 3.3. Phân Hệ Dịch Phim & Lồng Tiếng (`#dubber-view`)
- Tăng độ chi tiết log (Verbose) của Terminal hiện có:
  - Tải video: Ghi rõ nguồn (Bilibili/Douyin/YouTube), kích thước file, định dạng.
  - Tách Audio: Tần số mẫu (16kHz mono cho Whisper).
  - OCR / Whisper: Ghi nhận từng phân đoạn thời gian đang xử lý, số câu trích xuất được.
  - Dịch AI: Ghi rõ model đang dịch (Gemini/Groq), từng batch câu dịch, thời gian xử lý.
  - Tạo TTS: Ghi rõ từng câu đang sinh giọng đọc, thời lượng wav, tiến độ % TTS.
  - Render Video: Đọc và parse output progress của FFmpeg để in frame và thời gian xử lý.

### 3.4. Giao Diện Trang Chủ (Home Hub)
- Nâng cấp `home-recent-projects-list`:
  - Thêm bộ lọc tab danh mục: **Tất Cả** | **🎬 Dịch Phim** | **🎙️ Đọc Truyện** | **🧵 Video Threads**.
  - Hiển thị badge loại dự án rõ nét với màu sắc nhận diện:
    - 🎬 Dịch Phim: Xanh tím (Indigo)
    - 🎙️ Đọc Truyện: Hồng tím (Pink/Purple)
    - 🧵 Video Threads: Xanh dương (Blue/Cyan)
  - Khi click vào dự án, tự động chuyển view tương ứng và khôi phục toàn bộ trạng thái.

---

## 4. Kế Hoạch Kiểm Thử
1. Unit tests & API tests cho project save/load cả 3 loại.
2. Kiểm thử background task và streaming status/logs cho Story TTS và Social Video.
3. Kiểm thử khôi phục trạng thái giao diện khi mở dự án từ Home Hub.

