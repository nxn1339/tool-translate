# Thư mục chứa Models RVC (Voice Conversion)

Thả các file model giọng RVC của bạn vào thư mục này:
- File trọng số mô hình: `.pth` (ví dụ: `cogaithoatngon.pth`)
- File chỉ mục (tùy chọn, giúp giọng giống hơn): `.index` (ví dụ: `cogaithoatngon.index` hoặc `added_IVF256_Flat_FastTrack...index`)

Hệ thống sẽ tự động quét và hiển thị lên danh sách chọn giọng trên giao diện Studio.

### Model cơ sở (Base weights) cần thiết cho RVC:
- `hubert_base.pt`
- `rmvpe.pt`
Lưu tại `app/models/rvc/base/`

