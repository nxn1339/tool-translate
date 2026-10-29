# Docs - Source of Truth

Thư mục này là nguồn tài liệu chính (Source of Truth) cho dự án **tool-translate** (Hệ thống tự động dịch & lồng tiếng video Bilibili bằng AI). BA, Design, Dev, Test và PM cùng cập nhật theo một cấu trúc thống nhất.

## Mục tiêu

- Quản lý yêu cầu, thiết kế kiến trúc, API, xử lý âm thanh/video, kiểm thử, task và release trong cùng một nơi.
- Duy trì tính truy vết (traceability) từ requirement -> UI Screen -> API Endpoint -> Worker Pipeline -> Test Case.
- Chuẩn hóa quy trình làm việc theo vai trò và hỗ trợ tự động hóa thông qua hệ thống AI Skills tại `.agents/skills/`.

## Vai trò và khu vực phụ trách

| Vai trò | Thư mục chính | Nội dung |
|---|---|---|
| PM | `01.management/` | Roadmap, schedule, WBS, task, meeting, feedback, decision log |
| BA | `02.product/` | Vision, requirement, user role, user story, business rule, acceptance criteria |
| Design | `03.design/` | Design system, user flow, wireframe, screen layout, UI asset |
| Dev | `04.technical/` | Architecture, Web app, API contracts, local storage, security/anti-bot, refactor |
| Test | `05.testing/` | Test plan, test case, bug report, regression checklist, UAT |
| All | `06.traceability/` | Mapping giữa requirement, screen, API, worker và test case |
| Release | `07.release/` | Runbook vận hành, checklist triển khai, release notes |
| Superpowers | `superpowers/` | Kế hoạch thực thi (plans), đặc tả kỹ thuật (specs), bằng chứng kiểm thử (evidence) |

## Vertical Slices (VS) Convention

Dự án phân chia các cụm tính năng độc lập theo chiều dọc (Vertical Slices):
- `VS-001`: Core Media Pipeline (Tải video Bilibili, bóc tách audio, nhận dạng giọng nói bằng Whisper, dịch bằng deep-translator, tổng hợp TTS bằng Edge-TTS và ghép video/audio bằng FFmpeg).
- `VS-002`: Web Interface & Task Monitoring (FastAPI Web App, giao diện dashboard điều khiển, polling tiến độ real-time, preview và tải video hoàn thiện).
- `VS-003`: Bilibili Cookie & Authentication (Quản lý SESSDATA, buvid3/buvid4 chống chặn HTTP 412, cấu hình cookie nâng cao).
- `VS-004`: Voice Settings & Audio Customization (Tùy chỉnh giọng đọc TikTok/Hoài My/Nam Minh, tốc độ rate, cao độ pitch, cân bằng âm lượng nhạc nền vs lồng tiếng).
- `VS-005`: Subtitle OCR, Masking & Multi-Tab Workspace (Phân tách giao diện 2 Tab Video Có Sub / Không Sub, 2 khung tương tác kéo-thả che sub cũ và định vị sub mới, tích hợp RapidOCR và FFmpeg Hardsub/SRT).
- `VS-006`: CapCut Subtitle Studio & Modular Settings (Module hóa Cài đặt hệ thống thành 3 thẻ con; Tab chuyên biệt Kiểu Phụ Đề phong cách CapCut với 6 presets hot TikTok/Shorts, color picker, stroke, box background, font, live monitor và đồng bộ bounding box trực quan).


## ID Convention

| Loại | Mẫu ID | Ví dụ |
|---|---|---|
| Requirement | `REQ-XXX` | `REQ-001` |
| User story | `US-XXX` | `US-001` |
| Screen | `APP-XXX` | `APP-001` |
| Function / Action | `FUNC-XXX` | `FUNC-001` |
| API Endpoint | `API-XXX` | `API-001` |
| Test case | `TC-XXX` | `TC-001` |
| Task (Management) | `TASK-XXX` | `TASK-001` |
| Dev Task (Code) | `DEV-XXX` | `DEV-001` |
| Decision | `DEC-XXX` | `DEC-001` |

## Hệ thống Skill tự động hóa (.agents/skills)

Repo tích hợp các kỹ năng tiêu chuẩn tại `.agents/skills/`:
- `output-docs-standard`: Quy chuẩn đặt tên file, UTF-8 tiếng Việt và kiến trúc Multi-Phase.
- `ba-workflow`: Quy trình chuyển yêu cầu thành tài liệu nghiệp vụ.
- `dev-workflow`: Quy trình thiết kế kỹ thuật, API và bẻ khóa implementation task.
- `design-workflow`: Quy trình thiết kế giao diện UI/UX.
- `test-workflow`: Quy trình lập test plan, test case và ma trận kiểm thử.
- `pm-task-assignment`: Quản lý danh sách task, WBS và phân bổ nguồn lực.
- `docs-consistency-review`: Quét kiểm toán toàn bộ tính nhất quán của tài liệu và mã nguồn.
