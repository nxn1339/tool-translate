# Operation Runbook - Hướng dẫn vận hành và khởi chạy

## 1. Yêu cầu môi trường
- Hệ điều hành: Windows 10/11 64-bit.
- Python: Phiên bản 3.9 - 3.11 (đã thêm vào PATH).
- FFmpeg: Đã tích hợp sẵn trong thư mục `ffmpeg/` của repo.

## 2. Cách khởi động ứng dụng
1. Mở terminal tại thư mục gốc của dự án.
2. Chạy lệnh:
   ```cmd
   run.bat
   ```
   hoặc:
   ```powershell
   python run.py
   ```
3. Script sẽ tự động:
   - Kiểm tra FFmpeg binary.
   - Kiểm tra và cài đặt các thư viện trong `requirements.txt`.
   - Tìm cổng mạng khả dụng (mặc định 8080).
   - Tự động mở trình duyệt web tại `http://localhost:8080`.

## 3. Xử lý sự cố thường gặp
- **Lỗi HTTP 412 (Precondition Failed):** Đăng nhập vào trang web Bilibili trên trình duyệt, lấy giá trị cookie `SESSDATA` dán vào ô "Bilibili Cookie" trên giao diện.
- **Lỗi Whisper không tải được model:** Kiểm tra kết nối mạng Internet ở lần chạy đầu tiên để Whisper tải model `base` (~140MB) từ HuggingFace/OpenAI CDN.
