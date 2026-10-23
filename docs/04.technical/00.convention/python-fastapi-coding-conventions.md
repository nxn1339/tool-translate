# Coding Conventions - Quy chuẩn mã nguồn Python & FastAPI

## 1. Tiêu chuẩn ngôn ngữ & Style Guide
- Tuân thủ PEP 8 cho toàn bộ mã nguồn Python.
- Định dạng encoding: UTF-8 không BOM cho toàn bộ file code và tài liệu.
- Type Hints: Sử dụng `typing` (`List`, `Dict`, `Optional`, `Any`) hoặc Python 3.10+ native typing cho chữ ký hàm.
- Docstrings: Viết docstring theo phong cách Google hoặc Sphinx cho mọi hàm public và module.

## 2. FastAPI & Bất đồng bộ (Async/Await)
- Các tác vụ I/O nặng (tải file mạng, chạy tiến trình bên ngoài FFmpeg/Whisper) phải dùng `BackgroundTasks` hoặc chạy trên thread pool riêng để không block Event Loop của Uvicorn.
- Xử lý lỗi: Luôn bắt ngoại lệ cụ thể, ghi log qua `logging.getLogger(__name__)` kèm `exc_info=True` khi gặp lỗi hệ thống.
- Endpoint trả về cấu trúc dữ liệu tường minh thông qua Pydantic `BaseModel`.

## 3. Xử lý đường dẫn & Hệ thống file (Cross-Platform)
- Tuyệt đối không hard-code đường dẫn dạng Linux `/tmp` hay Windows `C:\` cố định.
- Luôn sử dụng `os.path.join` hoặc `pathlib.Path` tương đối dựa trên `os.path.dirname(os.path.abspath(__file__))`.
- Đảm bảo kiểm tra sự tồn tại của thư mục trước khi ghi file bằng `os.makedirs(dir_path, exist_ok=True)`.
