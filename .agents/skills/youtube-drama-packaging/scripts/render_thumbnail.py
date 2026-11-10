import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


def generate_thumbnail(
    input_path: str,
    output_path: str,
    line1: str,
    line2: str,
    scale: float = 0.88,
    clean_watermarks: bool = True,
):
    img = Image.open(input_path).convert("RGB")
    orig_w, orig_h = img.size

    if clean_watermarks:
        img_np = np.array(img)
        mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
        # Standard watermark zones (top-left, top-right, bottom subtitle bar)
        mask[0 : int(orig_h * 0.12), 0 : int(orig_w * 0.33)] = 255
        mask[0 : int(orig_h * 0.18), int(orig_w * 0.88) : orig_w] = 255
        mask[int(orig_h * 0.73) : int(orig_h * 0.83), int(orig_w * 0.65) : int(orig_w * 0.84)] = 255
        mask[int(orig_h * 0.80) : orig_h, int(orig_w * 0.10) : int(orig_w * 0.92)] = 255

        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        clean_bgr = cv2.inpaint(img_bgr, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
        clean_img = Image.fromarray(cv2.cvtColor(clean_bgr, cv2.COLOR_BGR2RGBA))
    else:
        clean_img = img.convert("RGBA")

    target_w, target_h = 1920, 1080

    # Blurred dark cinematic background
    bg = clean_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    bg = ImageEnhance.Color(bg).enhance(1.2)

    # Balanced foreground
    fg_w = int(target_w * scale)
    fg_h = int(target_h * scale)
    fg = clean_img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    fg = ImageEnhance.Color(fg).enhance(1.25)
    fg = ImageEnhance.Contrast(fg).enhance(1.18)
    fg = ImageEnhance.Sharpness(fg).enhance(1.35)
    fg = ImageEnhance.Brightness(fg).enhance(1.04)

    mask_feather = Image.new("L", (fg_w, fg_h), 255)
    d_mf = ImageDraw.Draw(mask_feather)
    border = 40
    for i in range(border):
        alpha = int(255 * (i / border))
        d_mf.rectangle([i, i, fg_w - 1 - i, fg_h - 1 - i], outline=alpha)

    fg_x = (target_w - fg_w) // 2
    fg_y = (target_h - fg_h) // 2 - 20

    composite = bg.copy()
    composite.paste(fg, (fg_x, fg_y), mask_feather)

    # Bottom vignette gradient for text readability
    vignette = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for y in range(target_h - 450, target_h):
        alpha = int(210 * ((y - (target_h - 450)) / 450) ** 1.3)
        v_draw.line([(0, y), (target_w, y)], fill=(8, 4, 12, alpha))

    composite = Image.alpha_composite(composite, vignette)

    # Typography
    txt_canvas_w, txt_canvas_h = 1700, 500
    txt_img = Image.new("RGBA", (txt_canvas_w, txt_canvas_h), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(txt_img)

    font_path = r"C:\Windows\Fonts\ariblk.ttf"
    f1 = ImageFont.truetype(font_path, 88)
    f2 = ImageFont.truetype(font_path, 112)

    l1_w = f1.getlength(line1)
    l2_w = f2.getlength(line2)

    x1 = (txt_canvas_w - l1_w) // 2
    y1 = 30
    x2 = (txt_canvas_w - l2_w) // 2
    y2 = 145

    # Line 1: White + Black stroke
    t_draw.text((x1 + 6, y1 + 10), line1, font=f1, fill=(0, 0, 0, 220), stroke_width=14, stroke_fill=(0, 0, 0, 220))
    t_draw.text((x1, y1), line1, font=f1, fill=(255, 255, 255, 255), stroke_width=12, stroke_fill=(15, 10, 20, 255))
    t_draw.text((x1, y1), line1, font=f1, fill=(255, 255, 255, 255))

    # Line 2: Gold-Yellow + Red outer stroke + Black inner stroke
    t_draw.text((x2 + 8, y2 + 12), line2, font=f2, fill=(0, 0, 0, 240), stroke_width=18, stroke_fill=(0, 0, 0, 240))
    t_draw.text((x2, y2), line2, font=f2, fill=(255, 20, 40, 255), stroke_width=22, stroke_fill=(210, 15, 30, 220))
    t_draw.text((x2, y2), line2, font=f2, fill=(255, 230, 0, 255), stroke_width=13, stroke_fill=(10, 5, 10, 255))
    t_draw.text((x2, y2), line2, font=f2, fill=(255, 235, 20, 255))

    txt_rotated = txt_img.rotate(2.5, resample=Image.Resampling.BICUBIC, expand=True)
    txt_w, txt_h = txt_rotated.size
    paste_x = (target_w - txt_w) // 2
    paste_y = target_h - txt_h - 25

    composite.paste(txt_rotated, (paste_x, paste_y), txt_rotated)
    composite.convert("RGB").save(output_path, quality=96)
    print(f"Thumbnail saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render YouTube Drama Thumbnail")
    parser.add_argument("--input", required=True, help="Input screenshot path")
    parser.add_argument("--output", required=True, help="Output thumbnail path")
    parser.add_argument("--line1", required=True, help="Top line text (White)")
    parser.add_argument("--line2", required=True, help="Bottom line text (Yellow/Red)")
    parser.add_argument("--scale", type=float, default=0.88, help="Foreground scale factor")
    parser.add_argument("--no-clean", action="store_true", help="Disable automatic watermark inpainting")
    args = parser.parse_args()

    generate_thumbnail(
        input_path=args.input,
        output_path=args.output,
        line1=args.line1,
        line2=args.line2,
        scale=args.scale,
        clean_watermarks=not args.no_clean,
    )

