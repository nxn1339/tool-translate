# Master Test Plan - Kế hoạch kiểm thử tổng thể

## 1. Mục tiêu kiểm thử
Đảm bảo độ tin cậy của toàn bộ pipeline dịch và lồng tiếng video từ lúc nhập URL cho tới khi xuất file hoàn thiện, kiểm soát các ngoại lệ mạng và lỗi thư viện bên thứ ba.

## 2. Phạm vi kiểm thử (Scope)
- **Kiểm thử tích hợp (Integration):**
  - Kết nối yt-dlp và tải video từ Bilibili.
  - Tích hợp Whisper STT và deep-translator.
  - Tích hợp Edge-TTS sinh âm thanh.
  - Ghép kênh âm thanh và hình ảnh bằng FFmpeg.
- **Kiểm thử giao diện (UI/E2E):**
  - Form validation (URL trống, URL không hợp lệ).
  - Quá trình polling và cập nhật thanh tiến độ.
  - Tải file thành phẩm về máy người dùng.
- **Kiểm thử môi trường & phụ thuộc (Environment):**
  - Kiểm tra phát hiện binary FFmpeg trong thư mục `ffmpeg/` và PATH hệ thống.

## 3. Chiến lược kiểm thử lỗi (Edge Cases)
1. Video không có tiếng thoại: Whisper trả về 0 segments -> Báo lỗi rõ ràng cho người dùng.
2. Bilibili yêu cầu xác thực / HTTP 412 -> Tự động sinh buvid hoặc thông báo nhập SESSDATA.
3. Ký tự đặc biệt trong lời thoại -> Đảm bảo hàm sanitize loại bỏ emoji, invisible unicode trước khi gửi sang TTS.
