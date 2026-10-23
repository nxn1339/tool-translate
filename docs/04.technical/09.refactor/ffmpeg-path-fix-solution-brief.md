# Solution Brief: Khắc phục lệch đường dẫn FFmpeg Binary

## 1. Vấn đề phát hiện (Problem Statement)
- Trong `run.py` (dòng 21) và `app/downloader.py` (dòng 22), logic tìm kiếm binary FFmpeg kiểm tra thư mục `bin/ffmpeg.exe`:
  ```python
  bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
  ```
- Tuy nhiên, trong cấu trúc thực tế của repository, file thực thi `ffmpeg.exe` (101MB) lại được lưu trữ tại thư mục `ffmpeg/ffmpeg.exe`.
- Hậu quả: Khi chạy trên máy chưa cài FFmpeg vào biến môi trường PATH hệ thống, ứng dụng không nhận diện được file `ffmpeg.exe` có sẵn, dẫn đến việc `run.py` kích hoạt tải lại gói 35MB từ GitHub hoặc gây lỗi pipeline ghép video.

## 2. Giải pháp đề xuất (Proposed Solution)
Cập nhật hàm `get_ffmpeg_path()` trong `app/downloader.py` và hàm `setup_ffmpeg()` trong `run.py` để bổ sung kiểm tra thư mục `ffmpeg/`:
1. Kiểm tra PATH hệ thống (`shutil.which("ffmpeg")`).
2. Kiểm tra thư mục `ffmpeg/ffmpeg.exe` tại root dự án.
3. Kiểm tra thư mục `bin/ffmpeg.exe` tại root dự án.
4. Kiểm tra đường dẫn WinGet Link (`%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe`).

## 3. Kế hoạch triển khai
- Task ID: `DEV-001`
- File chỉnh sửa: `app/downloader.py`, `run.py`.
- Tiêu chí nghiệm thu (DoD): Chạy `python run.py` trên môi trường không có PATH hệ thống vẫn nhận diện được `ffmpeg/ffmpeg.exe` thành công.
