# Kế Hoạch: Khắc Phục Lỗi Đồng Bộ File Preview Âm Thanh Lồng Tiếng (TTS) Bị Cắt Cụt

## 1. Vấn Đề
- Khi sinh TTS cho toàn bộ video (đặc biệt các video dài trên 1000 câu), frontend poll status và kết thúc sớm khi `progress === 100`.
- Tại thời điểm 100% câu lẻ hoàn tất, backend bắt đầu chạy FFmpeg (`mix_timeline_audio_fast`) để tổng hợp các câu lẻ vào timeline (mất ~15s).
- Do frontend thấy `progress === 100` trước khi status chuyển thành `tts_ready`, frontend fetch ngay file `preview_dubbed.mp3` cũ (hoặc file chưa mix xong), dẫn đến việc file preview chỉ dài 25 giây thay vì 53 phút, gây lặp âm thanh và ngắt tiếng giữa chừng.

## 2. Giải Pháp Triển Khai
1. **Frontend (`app/static/app.js`)**:
   - Sửa điều kiện kết thúc polling ở dòng 6104 từ `if (statusData.status === "tts_ready" || progress === 100)` thành `if (statusData.status === "tts_ready")`.
   - Đảm bảo chỉ khi backend đã mix xong hoàn toàn và ghi đè file `preview_dubbed.mp3` thì mới cho phép tải và phát audio.

2. **Backend (`app/main.py`)**:
   - Trong `_progress_cb`: Giữ mức tiến độ tối đa 95% trong lúc đang sinh các câu thoại lẻ.
   - Khi hoàn tất 100% câu thoại lẻ (`done >= total`), cập nhật tiến độ 96% cùng thông điệp: `"Đang tổng hợp toàn bộ âm thanh lồng tiếng vào timeline..."`.
   - Chỉ khi `generate_preview_audio_track` thực sự hoàn tất thì mới gán `progress = 100` và `status = "tts_ready"`.

3. **Kiểm Thử & Nghiệm Thu**:
   - Biên dịch kiểm tra syntax code.
   - Kiểm tra file `preview_dubbed.mp3` của project thực tế (`7fb1daf7-5909-4245-81df-532d79cbd335`) để đảm bảo thời lượng đầy đủ 53.4 phút và dung lượng ~51.3 MB.

