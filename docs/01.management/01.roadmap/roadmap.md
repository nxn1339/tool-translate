# Project Roadmap - Lộ trình phát triển tool-translate

```text
[ Phase 1: MVP Core Pipeline ] (Done)
  |-- Tải video Bilibili (yt-dlp) + bypass HTTP 412
  |-- STT Whisper base + Google Translate
  |-- Lồng tiếng Edge-TTS + FFmpeg audio mixing
  |-- Web Dashboard đơn giản + Polling status
  |
[ Phase 2: Refactor & Stability ] (Current)
  |-- Chuẩn hóa bộ tài liệu docs theo tiêu chuẩn enterprise
  |-- Sửa lỗi lệch đường dẫn local ffmpeg binary (DEV-001)
  |-- Dọn dẹp mã nguồn và chuyển README.md sang UTF-8
  |-- Bổ sung cơ chế dọn dẹp thư mục tạm `app/temp` tự động
  |
[ Phase 3: Enhanced Features ] (Planned)
  |-- Hỗ trợ xem trước và chỉnh sửa bản dịch (Subtitle Editor) trước khi sinh voice
  |-- Đa dạng hóa nguồn video (YouTube, Douyin, TikTok)
  |-- Hỗ trợ tăng tốc GPU (CUDA) cho Whisper
  |-- Hỗ trợ xuất file phụ đề rời (.srt, .vtt)
```
