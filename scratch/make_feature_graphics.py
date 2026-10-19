import os
from PIL import ImageDraw
from graphic_utils import (
    GraphicConfig,
    create_gradient_background,
    add_ambient_glows,
    render_logo_badge,
    render_phone_screenshot,
    load_font,
    render_studio_pill,
    render_trust_badges
)

def create_feature_graphic(config: GraphicConfig):
    width = config.width
    height = config.height

    # 1. Base Dark Navy Gradient Background (Fast 1D Scaling)
    img = create_gradient_background(
        width=width,
        height=height,
        top_color=(10, 25, 47, 255),
        bottom_color=(4, 11, 21, 255)
    )

    # 2. Ambient Glowing Orbs
    glows = [
        ((-100, -50, 450, 500), (100, 255, 218, 40)),
        ((650, 50, 1150, 550), (0, 229, 255, 30))
    ]
    img = add_ambient_glows(img, width, height, blur_radius=60, glows=glows)

    # 3. Left Brand / Logo Box
    img = render_logo_badge(
        img=img,
        logo_path=config.logo_path,
        x=70,
        y=65,
        size=140,
        badge_radius=24,
        badge_pad=12,
        border_width=2
    )

    # 4. Right: Perspective Phone Screenshot Frame
    img = render_phone_screenshot(
        img=img,
        screenshot_path=config.screenshot_path,
        chassis_x=700,
        chassis_y=50,
        ph_w=260,
        crop_h=420,
        corner_radius=24,
        border_width=2
    )

    draw = ImageDraw.Draw(img)

    # 5. Typography via System Font
    font_brand = load_font("arialbd.ttf", 36)
    font_tag = load_font("arialbd.ttf", 26)
    font_sub = load_font("arial.ttf", 16)
    font_pill = load_font("courbd.ttf", 12)
    font_stat = load_font("arialbd.ttf", 13)

    # Studio Pill
    render_studio_pill(
        draw=draw,
        pill_x=260,
        pill_y=65,
        pill_w=360,
        pill_h=28,
        radius=14,
        font=font_pill,
        dot_offset_x=12,
        dot_size=8,
        text_offset_x=28,
        text_offset_y=6,
        border_width=1
    )

    # App Title / Brand
    draw.text((260, 105), config.app_name.upper(), fill=(255, 255, 255, 255), font=font_brand)

    # Tagline
    draw.text((260, 160), config.tagline, fill=(100, 255, 218, 255), font=font_tag)

    # Subtagline
    draw.text((70, 260), config.subtag, fill=(203, 213, 225, 255), font=font_sub)

    # Stat / Trust Badges at bottom
    render_trust_badges(
        draw=draw,
        badges=config.badges,
        start_x=70,
        stat_y=410,
        font=font_stat,
        pad_x=12,
        pad_y=7,
        height=32,
        radius=8,
        gap=12,
        border_width=1
    )

    # Save output
    img.convert("RGB").save(config.output_path, "PNG", quality=95)
    print(f"Generated: {config.output_path} ({width}x{height})")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logo = os.path.join(base_dir, "assets", "img", "riomhoideas_logo.jpg")

    # 1. Riomhoideas Studio Header
    create_feature_graphic(GraphicConfig(
        logo_path=logo,
        screenshot_path=os.path.join(base_dir, "assets", "img", "hously_preview_1.png"),
        output_path=os.path.join(base_dir, "assets", "img", "google_play_feature_graphic_riomhoideas.png"),
        app_name="Ríomhoideas",
        tagline="Smarter admin. Zero bloat.",
        subtag="Lightweight, secure, and mobile-first administrative utilities.\nBuilt for mobile service operators & residential estate committees.",
        badges=["100% Offline-First", "Zero Telemetry", "On-Device Database", "County Donegal, IE"]
    ))

    # 2. Pocket Office Pro Feature Graphic
    create_feature_graphic(GraphicConfig(
        logo_path=logo,
        screenshot_path=os.path.join(base_dir, "assets", "img", "pocketoffice_preview_1.jpeg"),
        output_path=os.path.join(base_dir, "assets", "img", "google_play_feature_graphic_pocketoffice.png"),
        app_name="Pocket Office Pro",
        tagline="Invoicing & Sign-Off in Seconds",
        subtag="Draft quotes, calculate VAT, and deliver clean PDF invoices on-site.\nCapture live client signatures with zero evening paperwork.",
        badges=["100% Offline-First", "Zero Telemetry", "On-Device Database", "County Donegal, IE"]
    ))

    # 3. Hously Pro Feature Graphic
    create_feature_graphic(GraphicConfig(
        logo_path=logo,
        screenshot_path=os.path.join(base_dir, "assets", "img", "hously_preview_1.png"),
        output_path=os.path.join(base_dir, "assets", "img", "google_play_feature_graphic_hously.png"),
        app_name="Hously Pro",
        tagline="Clear Residential Oversight",
        subtag="Smart financial statement scanning, reconciliation, and AGM-ready reports.\nUnified estate management for housing committees & OMCs.",
        badges=["100% Offline-First", "Zero Telemetry", "On-Device Database", "County Donegal, IE"]
    ))
