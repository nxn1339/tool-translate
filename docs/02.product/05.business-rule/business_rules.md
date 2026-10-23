# Business Rules - Quy tắc nghiệp vụ

| Quy tắc ID | Tên quy tắc | Nội dung chi tiết | Slice |
|---|---|---|---|
| `BR-001` | Bắt buộc URL hợp lệ | URL đầu vào phải là link Bilibili hợp lệ (bilibili.com/video/BV... hoặc b23.tv) | `VS-001` |
| `BR-002` | Dự phòng âm thanh im lặng | Nếu một phân đoạn TTS bị lỗi mạng sau 3 lần retry, sinh đoạn audio im lặng tương ứng để không làm lệch timestamp của toàn bộ video | `VS-004` |
| `BR-003` | Tự sinh định danh Anti-Bot | Khi request không kèm cookie, tự động sinh chuỗi `buvid3` và `buvid4` ngẫu nhiên để vượt rào HTTP 412 của Bilibili CDN | `VS-003` |
| `BR-004` | Giới hạn âm lượng phối trộn | Âm lượng nhạc nền gốc (`bg_volume`) mặc định là 0.15 (15%), âm lượng giọng đọc TTS (`tts_volume`) mặc định là 1.0 (100%) để tiếng thoại rõ nét | `VS-004` |
