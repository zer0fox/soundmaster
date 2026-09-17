import math
import os
from PIL import Image, ImageDraw, ImageFilter


def create_soundmaster_icon(output_ico_path="soundmaster.ico", output_png_path="soundmaster.png"):
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    pad = 56
    r = 210

    # 1. Base Squircle Mask
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=r, fill=255)

    # 2. Gradient Background
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)
    for y in range(pad, size - pad):
        factor = (y - pad) / (size - 2 * pad)
        # Deep dark cyber blue to charcoal gradient
        cr = int(14 * (1 - factor) + 8 * factor)
        cg = int(22 * (1 - factor) + 12 * factor)
        cb = int(38 * (1 - factor) + 20 * factor)
        bg_draw.line([(pad, y), (size - pad, y)], fill=(cr, cg, cb, 255))

    bg.putalpha(mask)
    img.alpha_composite(bg)

    # 3. Outer Neon Accent Border
    border = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=r,
        outline=(0, 210, 255, 180),
        width=10
    )
    # Subtle inner gloss line
    border_draw.rounded_rectangle(
        [pad + 10, pad + 10, size - pad - 10, size - pad - 10],
        radius=r - 8,
        outline=(255, 255, 255, 25),
        width=4
    )
    img.alpha_composite(border)

    center_y = 490

    # 4. Sound Waves Layer (Active "ON" state)
    wave_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    wave_draw = ImageDraw.Draw(wave_layer)

    def draw_sound_wave(center_pt, radius, start_angle, end_angle, width, color):
        bbox = [center_pt[0] - radius, center_pt[1] - radius, center_pt[0] + radius, center_pt[1] + radius]
        wave_draw.arc(bbox, start=start_angle, end=end_angle, fill=color, width=width)

    # Sound Waves (Cyan neon glow)
    draw_sound_wave((420, center_y), radius=190, start_angle=-38, end_angle=38, width=32, color=(0, 240, 255, 255))
    draw_sound_wave((420, center_y), radius=290, start_angle=-40, end_angle=40, width=34, color=(0, 215, 255, 240))
    draw_sound_wave((420, center_y), radius=390, start_angle=-42, end_angle=42, width=36, color=(0, 180, 255, 220))

    # Glow layer for waves
    wave_glow = wave_layer.filter(ImageFilter.GaussianBlur(radius=22))
    img.alpha_composite(wave_glow)
    img.alpha_composite(wave_layer)

    # 5. Speaker Body Layer
    spk_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    spk_draw = ImageDraw.Draw(spk_layer)

    # Speaker box
    bx1, by1, bx2, by2 = 180, 360, 310, 620
    spk_draw.rounded_rectangle([bx1, by1, bx2, by2], radius=24, fill=(230, 240, 250, 255))

    # Speaker cone flare
    cone_pts = [
        (300, 385),
        (500, 230),
        (500, 750),
        (300, 595)
    ]
    spk_draw.polygon(cone_pts, fill=(245, 250, 255, 255))

    # Lower bevel shading on cone for 3D metallic feel
    cone_shade = [
        (300, 595),
        (500, 750),
        (500, 530),
        (300, 500)
    ]
    spk_draw.polygon(cone_shade, fill=(175, 195, 215, 200))

    # Speaker rim / front cap
    spk_draw.rounded_rectangle([480, 230, 516, 750], radius=18, fill=(255, 255, 255, 255))

    # 6. Glowing Power Symbol on Speaker Box (Classic ⏻ ON/OFF symbol)
    p_cx = 245
    p_cy = center_y
    p_rad = 45
    p_bbox = [p_cx - p_rad, p_cy - p_rad, p_cx + p_rad, p_cy + p_rad]
    
    # Circle with opening at the top (-60 to 240 degrees)
    spk_draw.arc(p_bbox, start=300, end=240, fill=(0, 160, 255, 255), width=12)
    # Vertical line at the top
    spk_draw.line([(p_cx, p_cy - p_rad - 6), (p_cx, p_cy - 4)], fill=(0, 160, 255, 255), width=12)

    # 7. Modern "ON / OFF" Switch Control Bar at the bottom
    # Positioned nicely in the bottom center
    bar_x = 320
    bar_y = 800
    bar_w = 384
    bar_h = 94
    bar_r = 47

    # Switch background track
    spk_draw.rounded_rectangle(
        [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
        radius=bar_r,
        fill=(12, 20, 32, 240),
        outline=(0, 200, 255, 160),
        width=5
    )

    # OFF Side (Left) - Dim Red/Coral Mute Indicator
    off_cx = bar_x + 60
    off_cy = bar_y + bar_h // 2
    spk_draw.ellipse([off_cx - 20, off_cy - 20, off_cx + 20, off_cy + 20], outline=(255, 75, 90, 200), width=6)
    # Slash line across the OFF ring to clearly indicate mute/off
    spk_draw.line([(off_cx - 15, off_cy + 15), (off_cx + 15, off_cy - 15)], fill=(255, 75, 90, 200), width=5)

    # Center divider text/symbol
    spk_draw.line([(bar_x + bar_w // 2 - 10, bar_y + 25), (bar_x + bar_w // 2 - 10, bar_y + bar_h - 25)], fill=(255, 255, 255, 40), width=3)

    # ON Side (Right) - Glowing Neon Cyan Active Slider Knob
    knob_cx = bar_x + bar_w - 55
    knob_cy = bar_y + bar_h // 2
    knob_rad = 36
    
    # Glowing knob
    spk_draw.ellipse(
        [knob_cx - knob_rad, knob_cy - knob_rad, knob_cx + knob_rad, knob_cy + knob_rad],
        fill=(0, 245, 255, 255)
    )
    # Power vertical bar inside ON knob
    spk_draw.line([(knob_cx, knob_cy - 16), (knob_cx, knob_cy + 16)], fill=(10, 25, 40, 255), width=8)

    img.alpha_composite(spk_layer)

    # Save PNG and ICO
    png_img = img.resize((512, 512), Image.Resampling.LANCZOS)
    png_img.save(output_png_path, "PNG")

    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(output_ico_path, format="ICO", sizes=icon_sizes)
    print(f"Generated {output_ico_path} and {output_png_path} successfully!")


if __name__ == "__main__":
    create_soundmaster_icon()
