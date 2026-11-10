---
name: youtube-drama-packaging
description: >-
  Use when reading subtitle or script files (.srt, .txt) to generate high-CTR
  YouTube/TikTok titles, thumbnail concepts, Flow AI image generation prompts,
  thumbnail text overlays, and SEO-optimized video descriptions for the
  Hạt Tiêu Vietsub channel.
---

# YouTube Drama & Movie Packaging (Hạt Tiêu Vietsub)

Skill này chuẩn hóa toàn bộ quy trình đóng gói một video từ file kịch bản/phụ đề (`.srt`, `.txt`) thành bộ nguyên liệu đăng kênh hoàn chỉnh: **Tiêu đề CTR cao ➔ Concept & Prompt Thumbnail cho Flow AI ➔ Text Thumbnail ➔ Mô tả chuẩn SEO YouTube & Thẻ Tags**.

---

## Khi nào sử dụng Skill này

- Khi người dùng cung cấp đường dẫn file `.srt` / `.txt` hoặc nội dung kịch bản và yêu cầu đặt tiêu đề, làm thumbnail, tạo prompt Flow AI, hoặc viết mô tả video.
- Khi cần tối ưu lại tiêu đề/mô tả video cũ đang có CTR hoặc lượng tìm kiếm thấp.

---

## Quy trình 4 Bước Bắt Buộc

### Bước 1: Đọc & Giải phẫu Kịch bản (Script Anatomy)
Đọc file `.srt` hoặc kịch bản để trích xuất 4 dữ liệu cốt lõi trước khi viết:
1. **Thể loại & Phong cách hình ảnh (Genre & Visual Style):** Xác định rõ phim thuộc nhóm nào (Ngôn tình hào môn, Song trùng sinh, Hệ thống, Cổ trang, Kinh dị, Hoạt hình 3D CGI Donghua hay Phim ngắn người đóng).
2. **Mồi câu mở đầu (Opening Hook - 3 phút đầu):** Sự kiện sốc nhất ngay đầu phim (hạ thuốc, ép cưới, nhảy biển, trùng sinh, vung 30 tỷ...).
3. **Nhân thiết & Xung đột chính (Core Trope):** Nam chính kiểu gì (tổng tài điên tình, chiếm hữu yandere, trà xanh tâm cơ giả yếu đuối)? Nữ chính kiểu gì (giả ngốc, giả mất trí nhớ, hám tiền tỉnh táo)?
4. **Cú lật kèo cuối phim (Climax Twist) & Mốc thời gian (Timestamps):** Ghi nhận các mốc thời gian gay cấn theo file `.srt`. **Lưu ý sống còn:** Chỉ dùng cú twist để nhá hàng gây tò mò, **tuyệt đối không spoil toẹt kết cục** trong phần mô tả.

---

### Bước 2: Đặt Tiêu đề (Title Matrix - Tối ưu CTR)

Áp dụng công thức:
> **`[Thân phận / Trope mạnh] + [Hành động / Con số kịch tính] + [Cú lật kèo / Hệ quả] | Hạt Tiêu Vietsub`**

Luôn đề xuất **3 nhóm tiêu đề** (mỗi nhóm 3 phương án):
1. **Nhóm 1 - Giật gân / Chiếm hữu / Kịch tính (Khuyên dùng cho YouTube dài):** Đánh mạnh vào xung đột sinh tử, con số (30 tỷ, 100 triệu...), sự điên cuồng hoặc bí mật bị che giấu.
2. **Nhóm 2 - Hài hước / Trà xanh lật mặt / Ngọt sủng:** Khai thác sự đối lập giữa vẻ ngoài và tâm cơ bên trong của nhân vật.
3. **Nhóm 3 - Ngắn gọn giật tít (< 60 ký tự cho Shorts / TikTok / Reels):** Đi thẳng vào tình huống trớ trêu nhất.

---

### Bước 3: Thiết kế Thumbnail & Prompt cho Flow AI

#### 3.1. Nguyên tắc Bố cục & Text Thumbnail
- **Tỷ lệ:** `16:9` (1920x1080) cho YouTube, `9:16` cho Shorts/TikTok.
- **Góc máy (Framing):** Luôn ưu tiên `medium bust shot` (bán thân trên, thu nhỏ chủ thể vừa phải, có khoảng thở hai bên và phía dưới) để **cân đối khung hình và có chỗ đặt chữ**, tránh `extreme close-up` phóng mặt quá to choán hết ảnh.
- **Text Thumbnail:**
  - Độ dài: Tối đa **2 dòng (4 – 6 từ)**, viết IN HOA 100%.
  - Màu sắc chuẩn CTR:
    - **Dòng 1:** Trắng sáng (`#FFFFFF`) viền đen dày (`10-12px`).
    - **Dòng 2 (Từ khóa đắt nhất):** Vàng chanh ánh kim (`#FFE600`) hoặc Đỏ tươi (`#FF1E27`), viền kép (hào quang đỏ + viền đen dày `14px`), đổ bóng 3D sâu, nghiêng nhẹ `2.5°`.
  - Vị trí: Đặt ở **trung tâm cạnh dưới** hoặc **góc dưới bên trái**. Tuyệt đối tránh góc dưới bên phải (bị đè bởi đồng hồ thời lượng YouTube).

#### 3.2. Cấu trúc Prompt tiếng Anh chuẩn cho Flow AI
Luôn xuất kèm **Prompt chính** và **Negative Prompt** theo khuôn mẫu sau:

```text
A breathtaking cinematic YouTube thumbnail, 16:9 aspect ratio, 8k resolution, [CHỌN STYLE: Chinese 3D CGI donghua style, Unreal Engine 5 render HOẶC Photorealistic Chinese modern mini-drama movie still].

Framing & Composition: Balanced medium bust shot with comfortable breathing room, perfectly centered, zoomed-out slightly for balanced proportions. [Mô tả chi tiết vị trí, trang phục, hành động tương tác giữa nam chính và nữ chính, nhấn mạnh sự đối lập cảm xúc: một bên chiếm hữu/nguy hiểm/tâm cơ vs một bên hoảng hốt/ngây thơ/bối rối].

Beauty & Lighting Effects: Flawless ethereal skin glow, soft cinematic bloom, [hiệu ứng phụ: floating red rose petals / dark feathers / subtle bokeh], dramatic crimson and deep violet rim lighting against a moody dark background, high contrast, ultra-detailed textures, 32k UHD, masterpiece quality, clean image with no watermark or video player overlay.

Text Overlay: Clean, aesthetic 3D typography at the lower third: "[DÒNG 1]" in bold white metallic with heavy black contour, and "[DÒNG 2]" in vibrant glowing gold-yellow (#FFE600) with dual red-and-black outline, deep 3D drop shadow, professional poster design --ar 16:9 --style raw
```

**Negative Prompt bắt buộc:**
```text
subtitles, watermark, logo, channel avatar, banner, username, Chinese characters, messy text, blurry, low resolution, bad anatomy, deformed fingers, extra limbs, oversaturated cartoon, cropped head
```

#### 3.3. Script Tự động Xử lý & Xuất Thumbnail (Khi người dùng cung cấp ảnh chụp màn hình)
Nếu người dùng gửi kèm ảnh chụp từ video và muốn xuất ngay ảnh Thumbnail hoàn chỉnh (xóa watermark, thu nhỏ cân đối 88%, làm nét và gắn chữ 3D), chạy ngay script có sẵn trong skill:

```powershell
python ".agents/skills/youtube-drama-packaging/scripts/render_thumbnail.py" `
  --input "duong/dan/anh_goc.jpg" `
  --output "duong/dan/thumbnail_output.png" `
  --line1 "KIẾP NÀY" `
  --line2 "ĐỪNG HÒNG CHẠY!"
```
- Script [`render_thumbnail.py`](./scripts/render_thumbnail.py) tự động tẩy phụ đề/logo góc bằng OpenCV Inpainting, mở rộng nền mờ chuẩn 1920x1080, tăng tương phản/độ nét và vẽ chữ nổi 3D viền kép.

---

### Bước 4: Viết Mô tả Chuẩn SEO YouTube (Chuẩn kênh Hạt Tiêu Vietsub)

#### Các lỗi chí mạng CẤM mắc phải khi viết mô tả:
1. **CẤM dùng văn phong ghi chú nội bộ** (kiểu `(nữ giả vờ mất trí để ăn 30 tỷ rồi chuồn...)`) ở phần mở đầu. Phải viết bằng văn phong kể chuyện lôi cuốn.
2. **CẤM spoil cú twist cuối phim** (ai cũng trùng sinh, kết cục ra sao). Chỉ nêu tình huống mở đầu và đặt câu hỏi bỏ lửng (Open Loop).
3. **CẤM đặt phần văn bản SEO xuống dưới đáy** (sau phần bản quyền/lưu ý). Thuật toán YouTube quét trọng số SEO mạnh nhất ở **200 ký tự đầu tiên** và **nửa trên** của mô tả.
4. **CẤM lệch thể loại ở câu kêu gọi Đăng ký (CTA):** Phim ngôn tình/hào môn thì tuyệt đối không được để câu *"đăng ký để xem video kinh dị mới nhất"*. Phải tự động khớp đúng thể loại phim hiện tại.

#### Mẫu Mô tả Chuẩn SEO (Copy-Paste Ready):

```text
[TIÊU ĐỀ CHÍNH ĐÃ CHỌN] | Hạt Tiêu Vietsub

[ĐOẠN HOOK 2 DÒNG ĐẦU - CHUẨN SEO 160 KÝ TỰ ĐẦU]:
[1-2 câu tóm tắt tình huống gay cấn nhất đầu phim có chứa từ khóa chính: Trùng sinh / Tổng tài chiếm hữu / Hào môn / Phim ngắn trọn bộ... Kích thích người xem bấm đọc tiếp].

🎬 Tóm tắt nội dung phim:
[Đoạn 1 - Khởi đầu & Xung đột]: Kể lại bối cảnh nhân vật chính (tên nhân vật: ví dụ Bùi Dư Sênh - Tống Dực Từ), nguyên nhân dẫn đến màn ép cưới / giả mất trí nhớ / giao kèo 30 tỷ. Cài cắm từ khóa tự nhiên.
[Đoạn 2 - Diễn biến & Cao trào]: Miêu tả những màn đấu trí "vỏ quýt dày có móng tay nhọn", khổ nhục kế của nam chính, sự xuất hiện của hệ thống hoặc kẻ thứ ba cản đường.
[Đoạn 3 - Câu hỏi bỏ lửng (Open Loop)]: Liệu màn kịch hoàn hảo này sẽ kéo dài được bao lâu trước khi bí mật thật sự bị lật tẩy? Xem ngay trọn bộ để không bỏ lỡ cái kết cực sốc!

⏱️ Các phân đoạn gay cấn trong phim (Timestamps):
00:00 - [Mốc 1: Biến cố mở màn / Sống lại trước giờ G]
[mm:ss] - [Mốc 2: Màn kịch giả mất trí nhớ & Bản hợp đồng 30 tỷ]
[mm:ss] - [Mốc 3: Nam chính tung khổ nhục kế "trà xanh" giữ vợ]
[mm:ss] - [Mốc 4: Đá văng Hệ thống, xử đẹp kẻ ngáng đường]
[mm:ss] - [Mốc 5: Bí mật bị lật tẩy trên du thuyền & Cái kết]
*(Lấy mốc thời gian thực tế từ file .srt)*

💬 Bạn ấn tượng nhất với màn "diễn sâu" nào của nam chính trong phim? Hãy để lại bình luận bên dưới nhé!

📅 Phim mới cập nhật MỖI NGÀY – Đừng bỏ lỡ!
👉 Đăng ký kênh ngay để theo dõi những bộ [THỂ LOẠI PHIM: phim ngôn tình tổng tài / hoạt hình 3D / trùng sinh báo thù] hấp dẫn nhất!

--------------------------------------------------

⚠️ Lưu ý: Nội dung trong video mang tính chất giải trí, hư cấu hoặc được biên tập lại từ nhiều nguồn, không nhằm khẳng định sự kiện có thật. Người xem vui lòng cân nhắc khi theo dõi.

--------------------------------------------------

📩 Liên hệ bản quyền / Copyright issues:
Email: hattieuvietsub2504@gmail.com

© Tất cả nội dung đều được chỉnh sửa và biên tập bởi Hạt Tiêu Vietsub
❌ Vui lòng không reup video dưới mọi hình thức

--------------------------------------------------

#[tenkenh] #[theloai1] #[theloai2] #[theloai3] #[tennhanvat] #hattieuvietsub #phimngantrungquoc #trungsinh #tongtai #haomon #cuoitruocyeusau #phimhay #vietsub
```

#### Khối Thẻ Tags (Dành cho ô Tags trong YouTube Studio - Tối đa 500 ký tự):
Luôn xuất kèm một block code chứa danh sách từ khóa cách nhau bằng dấu phẩy để người dùng copy dán thẳng vào ô **Thẻ (Tags)** của YouTube Studio:
```text
hạt tiêu vietsub, hat tieu vietsub, phim ngắn trung quốc, phim ngôn tình tổng tài, trùng sinh hào môn, cưới trước yêu sau, nam chính chiếm hữu, [tên nhân vật nam], [tên nhân vật nữ], phim hoạt hình 3d trung quốc, ngôn tình trùng sinh trọn bộ, review phim hay, phim tổng tài bá đạo, thiên kim giả trùng sinh
```
