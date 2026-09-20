import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_feature_graphic(logo_path, screenshot_path, output_path, app_name, tagline, subtag):
    width = 1024
    height = 500

    # 1. Base Dark Navy Gradient Background
    img = Image.new("RGBA", (width, height), (10, 25, 47, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / float(height)
        r = int(10 * (1 - ratio) + 4 * ratio)
        g = int(25 * (1 - ratio) + 11 * ratio)
        b = int(47 * (1 - ratio) + 21 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Ambient Glowing Orbs
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    # Teal glow behind left logo area
    glow_draw.ellipse([(-100, -50), (450, 500)], fill=(100, 255, 218, 40))
    # Cyan glow on the right behind app preview
    glow_draw.ellipse([(650, 50), (1150, 550)], fill=(0, 229, 255, 30))
    
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=60))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # 3. Left Brand / Logo Box
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 140
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # Rounded badge behind logo
        logo_badge_x = 70
        logo_badge_y = 65
        badge_pad = 12
        badge_rect = [
            logo_badge_x - badge_pad,
            logo_badge_y - badge_pad,
            logo_badge_x + logo_size + badge_pad,
            logo_badge_y + logo_size + badge_pad
        ]
        
        # Glow for logo
        badge_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(badge_glow)
        bg_draw.rounded_rectangle(badge_rect, radius=24, fill=(100, 255, 218, 80))
        badge_glow = badge_glow.filter(ImageFilter.GaussianBlur(radius=15))
        img = Image.alpha_composite(img, badge_glow)
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle(badge_rect, radius=24, fill=(7, 17, 32, 240), outline=(100, 255, 218, 200), width=2)

        # Paste logo with rounded mask
        mask = Image.new("L", (logo_size, logo_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, logo_size, logo_size], radius=16, fill=255)
        img.paste(logo, (logo_badge_x, logo_badge_y), mask)

    # 4. Right: Perspective Phone Screenshot Frame
    if os.path.exists(screenshot_path):
        ss = Image.open(screenshot_path).convert("RGBA")
        # Target phone dimensions in banner
        ph_w = 260
        ph_h = 520
        ss_resized = ss.resize((ph_w, int(ph_w * (ss.height / ss.width))), Image.Resampling.LANCZOS)
        
        # Phone chassis canvas
        chassis_x = 700
        chassis_y = 50
        
        # Phone drop shadow
        phone_shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ps_draw = ImageDraw.Draw(phone_shadow)
        ps_draw.rounded_rectangle([chassis_x - 10, chassis_y - 5, chassis_x + ph_w + 10, chassis_y + 440], radius=32, fill=(0, 0, 0, 180))
        phone_shadow = phone_shadow.filter(ImageFilter.GaussianBlur(radius=20))
        img = Image.alpha_composite(img, phone_shadow)
        draw = ImageDraw.Draw(img)

        # Phone frame outline
        draw.rounded_rectangle([chassis_x - 6, chassis_y - 6, chassis_x + ph_w + 6, chassis_y + 430], radius=30, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=2)

        # Paste cropped screenshot
        crop_box = (0, 0, ph_w, 420)
        ss_cropped = ss_resized.crop(crop_box)
        ss_mask = Image.new("L", (ph_w, 420), 0)
        ss_mask_draw = ImageDraw.Draw(ss_mask)
        ss_mask_draw.rounded_rectangle([0, 0, ph_w, 420], radius=24, fill=255)
        img.paste(ss_cropped, (chassis_x, chassis_y), ss_mask)

    # 5. Typography via System Font
    try:
        font_brand = ImageFont.truetype("arialbd.ttf", 36)
        font_tag = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 16)
        font_pill = ImageFont.truetype("courbd.ttf", 12)
        font_stat = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font_brand = ImageFont.load_default()
        font_tag = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_pill = ImageFont.load_default()
        font_stat = ImageFont.load_default()

    # Studio Pill
    pill_x = 260
    pill_y = 65
    draw.rounded_rectangle([pill_x, pill_y, pill_x + 360, pill_y + 28], radius=14, fill=(15, 23, 42, 220), outline=(51, 65, 85, 200), width=1)
    draw.ellipse([pill_x + 12, pill_y + 10, pill_x + 20, pill_y + 18], fill=(100, 255, 218, 255))
    draw.text((pill_x + 28, pill_y + 6), "RIOMHOIDEAS SOFTWARE LAB", fill=(100, 255, 218, 255), font=font_pill)

    # App Title / Brand
    draw.text((260, 105), app_name.upper(), fill=(255, 255, 255, 255), font=font_brand)

    # Tagline
    draw.text((260, 160), tagline, fill=(100, 255, 218, 255), font=font_tag)

    # Subtagline
    draw.text((70, 260), subtag, fill=(203, 213, 225, 255), font=font_sub)

    # Stat / Trust Badges at bottom
    badges = [
        "100% Offline-First",
        "Zero Telemetry",
        "On-Device Database",
        "County Donegal, IE"
    ]
    
    start_x = 70
    stat_y = 410
    for b in badges:
        text_bbox = draw.textbbox((0, 0), b, font=font_stat)
        bw = text_bbox[2] - text_bbox[0] + 24
        draw.rounded_rectangle([start_x, stat_y, start_x + bw, stat_y + 32], radius=8, fill=(15, 23, 42, 200), outline=(51, 65, 85, 180), width=1)
        draw.text((start_x + 12, stat_y + 7), b, fill=(148, 163, 184, 255), font=font_stat)
        start_x += bw + 12

    # Save output
    img.convert("RGB").save(output_path, "PNG", quality=95)
    print(f"Generated: {output_path} ({width}x{height})")

if __name__ == "__main__":
    logo = "c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/riomhoideas_logo.jpg"
    
    # 1. Riomhoideas Studio Header
    create_feature_graphic(
        logo_path=logo,
        screenshot_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/hously_preview_1.png",
        output_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/google_play_feature_graphic_riomhoideas.png",
        app_name="Ríomhoideas",
        tagline="Smarter admin. Zero bloat.",
        subtag="Lightweight, secure, and mobile-first administrative utilities.\nBuilt for mobile service operators & residential estate committees."
    )

    # 2. Pocket Office Pro Feature Graphic
    create_feature_graphic(
        logo_path=logo,
        screenshot_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/pocketoffice_preview_1.jpeg",
        output_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/google_play_feature_graphic_pocketoffice.png",
        app_name="Pocket Office Pro",
        tagline="Invoicing & Sign-Off in Seconds",
        subtag="Draft quotes, calculate VAT, and deliver clean PDF invoices on-site.\nCapture live client signatures with zero evening paperwork."
    )

    # 3. Hously Pro Feature Graphic
    create_feature_graphic(
        logo_path=logo,
        screenshot_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/hously_preview_1.png",
        output_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/google_play_feature_graphic_hously.png",
        app_name="Hously Pro",
        tagline="Clear Residential Oversight",
        subtag="Smart financial statement scanning, reconciliation, and AGM-ready reports.\nUnified estate management for housing committees & OMCs."
    )
