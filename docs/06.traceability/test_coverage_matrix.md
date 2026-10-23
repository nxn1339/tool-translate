# Test Coverage Matrix

| Test Case ID | Tiêu đề kiểm thử | Slice | Req ID liên kết | Mức độ ưu tiên | Loại kiểm thử | Trạng thái hiện tại |
|---|---|---|---|---|---|---|
| `TC-001` | Kiểm tra tải video và audio từ Bilibili URL hợp lệ | `VS-001` | `REQ-001` | High | Integration | Passed |
| `TC-002` | Kiểm tra sinh buvid3/buvid4 khi không có cookie | `VS-003` | `REQ-002` | High | Unit | Passed |
| `TC-003` | Kiểm tra Whisper nhận diện giọng nói và xuất timestamp | `VS-001` | `REQ-003` | High | Unit | Passed |
| `TC-004` | Kiểm tra Google Translate dịch câu thoại tiếng Trung | `VS-001` | `REQ-004` | High | Integration | Passed |
| `TC-005` | Kiểm tra Edge-TTS sinh file mp3 đúng giọng cấu hình | `VS-004` | `REQ-005` | High | Integration | Passed |
| `TC-006` | Kiểm tra FFmpeg ghép audio TTS vào video gốc | `VS-001` | `REQ-006` | High | Integration | Passed |
| `TC-007` | Kiểm tra submit form trên UI gửi đúng payload | `VS-002` | `REQ-007` | Medium | E2E | Passed |
| `TC-008` | Kiểm tra thanh tiến độ cập nhật đúng theo task state | `VS-002` | `REQ-008` | Medium | E2E | Passed |
| `TC-009` | Kiểm tra link tải file mp4 trả về đúng video | `VS-002` | `REQ-009` | High | E2E | Passed |
| `TC-010` | Kiểm tra nhận diện binary `ffmpeg/ffmpeg.exe` local | `VS-001` | `REQ-010` | Critical | Unit / System | Failed (Cần fix refactor) |
