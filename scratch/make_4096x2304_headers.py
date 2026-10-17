import functools
import os
from PIL import ImageDraw, ImageFont
from graphic_utils import (
    GraphicConfig,
    create_gradient_background,
    add_ambient_glows,
    render_logo_badge,
    render_phone_screenshot
)

@functools.lru_cache(maxsize=32)
def get_font(font_name: str, size: int):
    try:
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()

def create_developer_header_graphic(config: GraphicConfig):
    width = config.width
    height = config.height

    # 1. Base Dark Navy Gradient Background (Fast 1D Scaling)
    img = create_gradient_background(
        width=width,
        height=height,
        top_color=(10, 25, 47, 255),
        bottom_color=(4, 11, 21, 255)
    )

    # 2. Ambient Glowing Atmosphere
    glows = [
        ((-300, -100, 1800, 2000), (100, 255, 218, 45)),
        ((2400, 300, 4400, 2300), (0, 229, 255, 35))
    ]
    img = add_ambient_glows(img, width, height, blur_radius=220, glows=glows)

    # 3. Left Brand Logo Badge
    img = render_logo_badge(
        img=img,
        logo_path=config.logo_path,
        x=280,
        y=350,
        size=580,
        badge_radius=90,
        badge_pad=48,
        border_width=8
    )

    # 4. Right: High-Res Perspective Phone Mockup
    img = render_phone_screenshot(
        img=img,
        screenshot_path=config.screenshot_path,
        chassis_x=2750,
        chassis_y=220,
        ph_w=1000,
        crop_h=1870,
        corner_radius=100,
        border_width=8
    )

    draw = ImageDraw.Draw(img)

    # 5. High-Resolution Typography
    font_brand = get_font("arialbd.ttf", 145)
    font_tag = get_font("arialbd.ttf", 100)
    font_sub = get_font("arial.ttf", 64)
    font_pill = get_font("courbd.ttf", 46)
    font_stat = get_font("arialbd.ttf", 52)

    # Studio Pill
    pill_x = 1050
    pill_y = 350
    pill_w = 1450
    pill_h = 100
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=50, fill=(15, 23, 42, 230), outline=(51, 65, 85, 220), width=3)
    draw.ellipse([pill_x + 45, pill_y + 35, pill_x + 75, pill_y + 65], fill=(100, 255, 218, 255))
    draw.text((pill_x + 105, pill_y + 22), "RIOMHOIDEAS SOFTWARE LAB", fill=(100, 255, 218, 255), font=font_pill)

    # Main Brand Name
    draw.text((1050, 490), config.app_name.upper(), fill=(255, 255, 255, 255), font=font_brand)

    # Tagline (Mint Gradient accent)
    draw.text((1050, 690), config.tagline, fill=(100, 255, 218, 255), font=font_tag)

    # Multi-line Subtitle
    draw.text((280, 1140), config.subtag, fill=(203, 213, 225, 255), font=font_sub, spacing=28)

    # Bottom Trust Badges
    start_x = 280
    stat_y = 1840
    for b in config.badges:
        text_bbox = draw.textbbox((0, 0), b, font=font_stat)
        bw = text_bbox[2] - text_bbox[0] + 80
        bh = 110
        draw.rounded_rectangle([start_x, stat_y, start_x + bw, stat_y + bh], radius=28, fill=(15, 23, 42, 220), outline=(51, 65, 85, 200), width=3)
        draw.text((start_x + 40, stat_y + 24), b, fill=(148, 163, 184, 255), font=font_stat)
        start_x += bw + 36

    # Save output in pristine high quality PNG
    img.convert("RGB").save(config.output_path, "PNG", quality=98)
    print(f"Generated 4K Play Store Header: {config.output_path} ({width}x{height})")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logo = os.path.join(base_dir, "assets", "img", "riomhoideas_logo.jpg")

    # 1. Official Google Play Developer Page Header (4096 x 2304)
    create_developer_header_graphic(GraphicConfig(
        logo_path=logo,
        screenshot_path=os.path.join(base_dir, "assets", "img", "hously_preview_1.png"),
        output_path=os.path.join(base_dir, "assets", "img", "google_play_header_4096x2304.png"),
        app_name="Ríomhoideas",
        tagline="Smarter admin. Zero bloat.",
        subtag="An independent Irish software studio crafting lightweight, secure, and mobile-first\nadministrative utilities for mobile professionals and residential committees.\nPrivate, local-first architecture with 100% data sovereignty.",
        width=4096,
        height=2304,
        badges=["100% Offline-First", "Zero Telemetry", "Local Scoped Database", "County Donegal, Ireland"]
    ))

    # 2. Pocket Office Pro 4K Header (4096 x 2304)
    create_developer_header_graphic(GraphicConfig(
        logo_path=logo,
        screenshot_path=os.path.join(base_dir, "assets", "img", "pocketoffice_preview_1.jpeg"),
        output_path=os.path.join(base_dir, "assets", "img", "google_play_header_pocketoffice_4096x2304.png"),
        app_name="Pocket Office Pro",
        tagline="Invoicing & Sign-Off in Seconds",
        subtag="Professional mobile invoicing, quote generation, and job tracking.\nCapture live client signatures on-site with zero evening paperwork.\nBuilt for mobile contractors, tradesmen, and service technicians.",
        width=4096,
        height=2304,
        badges=["100% Offline-First", "Zero Telemetry", "Local Scoped Database", "County Donegal, Ireland"]
    ))

    # 3. Hously Pro 4K Header (4096 x 2304)
    create_developer_header_graphic(GraphicConfig(
        logo_path=logo,
        screenshot_path=os.path.join(base_dir, "assets", "img", "hously_preview_1.png"),
        output_path=os.path.join(base_dir, "assets", "img", "google_play_header_hously_4096x2304.png"),
        app_name="Hously Pro",
        tagline="Clear Residential Oversight",
        subtag="Smart bank statement scanning, arrears reconciliation, and AGM-ready reports.\nUnified management platform for residential committees, OMCs, and factors.\nScoped local database ensuring complete financial privacy.",
        width=4096,
        height=2304,
        badges=["100% Offline-First", "Zero Telemetry", "Local Scoped Database", "County Donegal, Ireland"]
    ))
