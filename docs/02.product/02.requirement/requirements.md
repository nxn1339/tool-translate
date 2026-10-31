# Requirements Template & Index

Owner: BA  
Status: Active / Master Index

## Mục đích
File này định nghĩa quy chuẩn mẫu cho tài liệu yêu cầu và chỉ mục các lát cắt tính năng (Vertical Slices) của hệ thống AI Video Dubber Studio:
- `docs/02.product/02.requirement/VS-001.md` (Core Media Pipeline: Bilibili download, Whisper STT, Google Translate, Edge-TTS, FFmpeg)
- `docs/02.product/02.requirement/VS-002.md` (Web Interface, Task Progress Polling & Video Download)
- `docs/02.product/02.requirement/VS-003.md` (Bilibili Cookie & Buvid3/4 Anti-412 Authentication)
- `docs/02.product/02.requirement/VS-004.md` (Voice Settings, CapCut Neural TTS & RVC Voice Conversion)
- `docs/02.product/02.requirement/VS-005.md` (Subtitle OCR, Masking Box, Sub Box & Multi-Step Studio Workspace)
- `docs/02.product/02.requirement/VS-006.md` (Video Logo & Watermark Overlay, Canvas Drag-Resize & FFmpeg Filter)


## Mẫu cấu trúc lát cắt (Slice Template)
```markdown
# VS-XXX Requirements - <Slice Name>

Owner: BA  
Status: Draft / Approved

## Scope
Mô tả phạm vi nghiệp vụ.

## Functional Requirements
| Req ID | Tiêu đề | Mô tả nghiệp vụ | Mức độ ưu tiên | Trạng thái |
|---|---|---|---|---|
| REQ-XXX | ... | ... | High/Medium/Low | Open/Implemented |

## Non-functional Requirements
- Hiệu năng, độ ổn định, tương thích.

## Open Questions
| ID | Câu hỏi | Người phụ trách | Trạng thái |
|---|---|---|---|
```
