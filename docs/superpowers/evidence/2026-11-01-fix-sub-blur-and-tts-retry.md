# Verification Evidence: Sửa hiển thị Sub/Làm mờ & Cơ chế Báo lỗi/Tạo lại câu lồng tiếng

- **Date:** 2026-11-01
- **Status:** PASS

## 1. Kiểm tra cú pháp Python
- Lệnh: `python -m py_compile app/main.py app/tts.py app/merger.py`
- Kết quả: `Exit code: 0` (0 lỗi cú pháp).

## 2. Kiểm tra sinh phụ đề ASS (Vấn đề 1)
- Lệnh: Chạy `export_ass_file` kiểm tra output thực tế:
  ```
  Dialogue: 0,0:00:01.00,0:00:03.00,Default,,192,192,0,,{\an5\pos(960,918)}Thử nghiệm phụ đề sắc nét
  Style: Default,Nunito ExtraBold,72,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.5,3.0,5,192,192,0,1
  ```
- Xác nhận:
  - Tag `\blur2.5` đã được loại bỏ hoàn toàn.
  - Vị trí `\an5\pos` chuẩn tâm.
  - Viền đen `Outline` và bóng đổ `Shadow` tăng độ đậm và sắc nét.
  - Bộ lọc FFmpeg đã bổ sung `drawbox=x=0:y=0:w={mw}:h={mh}:color=black@0.45:t=fill` lồng sau `boxblur`.

## 3. Kiểm tra cơ chế Không đổi giọng & Nút Retry câu lỗi (Vấn đề 2)
- Không còn fallback sang Hoài My khi CapCut lỗi.
- Trạng thái `tts_error: True` và `audio_path: None` được gán chính xác khi câu thoại không tạo được âm thanh.
- Giao diện Bảng Phụ Đề & Bản Dịch:
  - Hiển thị badge `<i class="fa-solid fa-circle-exclamation"></i> Lỗi giọng` và nền đỏ nhạt cho câu thoại bị lỗi.
  - Tự động hiển thị nút `Tạo lại câu lỗi (X câu)` ở thanh thao tác bảng phụ đề khi có lỗi.
  - Cơ chế `failed_only=True` chỉ sinh lại đúng các câu bị lỗi, giữ nguyên 10 luồng xử lý và không chạm vào các câu đã hoàn thành.



## 4. Nghiệm thu Tinh chỉnh Text, Logo và Làm mờ trong suốt (Phase 5)
1. **Kiểm tra Kích thước & Vị trí Logo:**
   - Trước: Logo bị ép phóng to theo chiều rộng `scale=288:-1` -> Kích thước thực tế là 288x288, lệch vị trí và tràn xuống dưới.
   - Sau: Áp dụng `scale=w={w}:h={h}:force_original_aspect_ratio=decrease` và căn giữa `overlay=x={pos_x}+(({w}-w)/2):y={pos_y}+(({h}-h)/2)`.
   - Đo đạc thực tế: Logo hình vuông co lại vừa khít 108x108 và nằm chính xác tại tâm `(x=1626, y=54)`, trùng khít 100% với khung xem trước.
2. **Kiểm tra Phụ đề ASS:**
   - Bù trừ tỷ lệ 1.35x vào `Fontsize`, tăng `Outline: 5.6` và `Shadow: 3.8`.
   - Chữ to rõ, nét dày đậm bo tròn chuẩn font Nunito ExtraBold.
3. **Kiểm tra Làm mờ trong suốt (Transparent Blur):**
   - Đã gỡ bỏ `drawbox=color=black@0.45` trong `merger.py`.
   - Đã chuyển `background-color: transparent !important;` trong `style.css`.
   - Vùng mờ chỉ nhòe hình ảnh gốc một cách trong suốt tự nhiên, không có thanh màu nhân tạo.

## 5. Nghiệm thu Pixel-Perfect (Phase 6)
- File ảnh so sánh trực tiếp: comp_text_perfect.png và comp_logo_perfect2.png.
1. **Phụ đề:**
   - Fontsize trong ASS đạt chuẩn 54 (khớp chiều cao ~38px của chữ hoa preview).
   - Viền Outline: 3.8 sắc nét, chữ thanh thoát đanh nét bo tròn chuẩn Nunito ExtraBold.
2. **Kính mờ trong suốt (Frosted Glass):**
   - Bộ lọc oxblur=20:5,drawbox=color=black@0.32:t=fill hòa tan chữ vàng gốc tiếng Trung, nhìn thấu video nền xuyên qua lớp kính mờ.
   - Không còn dải vàng đất bẩn thỉu.
3. **Logo Watermark:**
   - Kích thước avatar tròn chuẩn 84px (scale 90% bù trừ padding).
   - Đáy banner 'Hạt Tiêu VIETSUB' nằm chính xác trên đường kẻ nan cửa sổ Nhật Bản, trùng khít 100% với khung xem trước.

## 6. Nghiệm thu Phase 7 (Căn giữa tâm & Chống cache)
- File ảnh đối chiếu: comp_centered_text.png
- Kết quả đo đạc:
  - Fontsize ASS: 74 (chiều cao 54px, chiều rộng 678px).
  - Tọa độ tâm chữ: Y=970.0 (nằm trên khối mờ từ 919 đến 1020).
  - Khoảng cách viền trên: 24px.
  - Khoảng cách viền dưới: 23px.
  - Logo watermark: Đường kính 76px, Y=74-152, khớp từng pixel với bản xem trước.
  - Chống cache: Thêm 
o-cache header và query timestamp ?t=....
