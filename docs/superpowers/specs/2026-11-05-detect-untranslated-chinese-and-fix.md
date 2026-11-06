# Specification: Phát hiện & Đánh dấu Câu sót Tiếng Trung và Tinh chỉnh Hán-Việt

- **Date:** 2026-11-05
- **Status:** Draft / Chờ người dùng duyệt sửa code
- **Model:** Gemini 3.8 Flash (Medium)

---

## 1. Bối Cảnh & Nguyên Nhân Gốc Rễ (Root Cause)

Người dùng phản ánh:
> *"tình trạng dịch sot vẫn còn text tiếng trung như Thẩm毅 chuyển đi cần thêm 1 cái đánh giấu nếu còn tiếng trung hay text không phải tiếng việt"*

### 1.1. Nguyên nhân sinh ra câu lỗi như "Thẩm毅 chuyển đi"
1. **Thiếu từ trong từ điển Hán - Việt (`hanviet_dict.json`):**
   - Ký tự `毅` (Nghị) chưa có trong `hanviet_dict.json`.
2. **Thuật toán nhận diện tên riêng tham lam & sinh chuỗi lai tạp (`app/hanviet.py`):**
   - Họ `沈` (Thẩm) nằm trong danh sách `surnames`.
   - Khi quét câu gốc có chữ như `沈毅转走`, thuật toán quét tham lam 3 ký tự `cand3 = "沈毅转"`.
   - Hàm `char_to_hv.get(ch, ch)`: Với `沈` trả về `Thẩm`, với `转` trả về `Chuyển`, nhưng với `毅` do thiếu trong từ điển nên trả về chính nó `毅`.
   - Kết quả: `沈毅转` bị thay thành chuỗi lai tạp `"Thẩm 毅 Chuyển "`.
   - Thuật toán tham lam nuốt luôn cả động từ `转` (chuyển) vào cụm tên.
   - Khi đưa chuỗi lai tạp này vào bộ dịch (Google Translate / Groq / Gemini), máy dịch giữ nguyên tên riêng lai tạp và chỉ dịch từ `走` thành `đi`, dẫn tới kết quả phụ đề bị biến dạng thành: `"Thẩm毅 chuyển đi"`.
3. **Thiếu hậu xử lý Hán - Việt fallback khi câu dịch còn chữ Hán:**
   - Sau khi dịch máy, nếu câu dịch vẫn sót chữ Hán thì hệ thống không thực hiện quét chuyển âm Hán - Việt nốt các chữ Hán đó.

### 1.2. Vấn đề cảnh báo trên giao diện & Quy trình dịch lại
1. **Chưa có cờ đánh dấu câu sót chữ Hán:**
   - Hiện tại hệ thống chỉ kiểm tra `translation_error` hoặc trường `translation` rỗng.
   - Câu `"Thẩm毅 chuyển đi"` có nội dung nên hệ thống đánh giá là dịch thành công, không cảnh báo người dùng.
2. **Không có công cụ tìm nhanh:**
   - Khi video có hàng trăm câu thoại, người dùng không thể biết câu nào bị sót chữ Hán nếu không soi thủ công từng dòng.
3. **Nút "Dịch lại câu lỗi" (`failed_only=True`) bỏ qua các câu này:**
   - Do không coi câu chứa chữ Hán là câu lỗi nên không thể chọn dịch lại tự động.

---

## 2. Thiết Kế Kỹ Thuật Chi Tiết

### 2.1. Cập nhật Backend & Tinh chỉnh Hán - Việt
1. **Bổ sung từ điển Hán - Việt (`app/data/hanviet_dict.json` & `app/hanviet_builder.py`):**
   - Bổ sung ký tự `毅:Nghị:yi` và các ký tự tên/từ vựng phổ biến thường gặp.
2. **Chặn sinh chuỗi lai tạp trong `app/hanviet.py`:**
   - Trong `extract_chinese_names_in_text`:
     - Nếu bất kỳ ký tự nào trong cụm ứng viên (cand2, cand3) KHÔNG có trong từ điển Hán - Việt (`ch not in char_to_hv`), TUYỆT ĐỐI KHÔNG nhận diện làm entity để tránh thay thế nửa vời chữ Hán vào câu tiếng Việt.
     - Chặn các động từ/trợ từ phổ biến đi kèm sau tên như: `转` (chuyển), `移` (di), `走` (đi), `来` (đến), `去` (đi), `跑` (chạy), `看` (nhìn), `说` (nói), `死` (chết)... không cho lọt vào `cand3`.
3. **Hậu xử lý fallback Hán - Việt trong `refine_vietnamese_dub_line` (`app/translator.py`):**
   - Kiểm tra nếu chuỗi tiếng Việt sau dịch vẫn còn ký tự chữ Hán `[\u4e00-\u9fff]`:
     - Tự động thay thế ký tự chữ Hán đó bằng âm Hán Việt tương ứng (nếu có trong từ điển).
4. **Mở rộng định nghĩa lỗi dịch trong `app/main.py`:**
   - Khi dịch với `failed_only=True`: Coi các câu có chứa ký tự `[\u4e00-\u9fff]` trong bản dịch là câu lỗi cần dịch lại.

### 2.2. Giao diện Người dùng (Frontend UI - `app/static/`)
1. **Đánh dấu trực quan trên từng hàng của Bảng Phụ Đề (`renderSegmentsTable` trong `app/static/app.js`):**
   - Kiểm tra regex chữ Hán: `const hasChinese = /[\u4e00-\u9fff]/.test(seg.translation || '');`
   - Nếu `hasChinese`:
     - Gắn badge cảnh báo nổi bật:
       `<span class="badge-chinese-warn" title="Bản dịch còn chứa ký tự tiếng Trung chưa dịch hết: ${chars}"><i class="fa-solid fa-language"></i> Sót chữ Hán: ${chars}</span>`
     - Thêm viền đỏ cam nổi bật cho ô input bản dịch (`border: 1px solid #f97316; background: rgba(249, 115, 22, 0.08)`).
     - Hàng `tr` được gắn class hoặc màu nền cảnh báo để dễ nhận biết khi cuộn bảng.
2. **Nút Lọc nhanh & Đếm số câu sót chữ Hán trên Header (`app/static/index.html`):**
   - Thêm nút lọc `btn-filter-chinese`:
     `<button type="button" id="btn-filter-chinese" class="secondary-btn btn-sm d-none" style="border-color: #f97316; color: #fb923c; background: rgba(249, 115, 22, 0.15); font-weight: 700;" title="Nhấn để chỉ xem các câu còn sót tiếng Trung hoặc xem lại tất cả"><i class="fa-solid fa-filter"></i> Sót tiếng Trung (<span id="count-chinese-warn">0</span>)</button>`
   - Bấm vào nút này sẽ bật/tắt (toggle) chế độ chỉ hiển thị những câu còn sót chữ Hán để người dùng sửa nhanh tức thì.
3. **Tích hợp vào nút "Dịch lại câu lỗi":**
   - Số lượng đếm câu lỗi dịch `failedTransCount` bao gồm cả câu chưa dịch và câu còn sót chữ Hán.
   - Nút `btn-retry-failed-translate` hỗ trợ dịch lại toàn bộ các câu này 1-click.

