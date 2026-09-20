import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_developer_header_graphic(logo_path, screenshot_path, output_path, app_name, tagline, subtag):
    width = 4096
    height = 2304

    # 1. Base Gradient Canvas (16:9 4K)
    img = Image.new("RGBA", (width, height), (10, 25, 47, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / float(height)
        r = int(10 * (1 - ratio) + 4 * ratio)
        g = int(25 * (1 - ratio) + 11 * ratio)
        b = int(47 * (1 - ratio) + 21 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Ambient Glowing Atmosphere
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    # Large mint glow behind logo on left
    glow_draw.ellipse([(-300, -100), (1800, 2000)], fill=(100, 255, 218, 45))
    # Cyan glow behind phone on right
    glow_draw.ellipse([(2400, 300), (4400, 2300)], fill=(0, 229, 255, 35))
    
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=220))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # 3. Left Brand Logo Badge
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 580
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        logo_badge_x = 280
        logo_badge_y = 350
        badge_pad = 48
        badge_rect = [
            logo_badge_x - badge_pad,
            logo_badge_y - badge_pad,
            logo_badge_x + logo_size + badge_pad,
            logo_badge_y + logo_size + badge_pad
        ]
        
        # Soft outer glow
        badge_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(badge_glow)
        bg_draw.rounded_rectangle(badge_rect, radius=90, fill=(100, 255, 218, 90))
        badge_glow = badge_glow.filter(ImageFilter.GaussianBlur(radius=60))
        img = Image.alpha_composite(img, badge_glow)
        draw = ImageDraw.Draw(img)

        # Crisp badge frame
        draw.rounded_rectangle(badge_rect, radius=90, fill=(7, 17, 32, 240), outline=(100, 255, 218, 220), width=8)

        # Paste logo with rounded mask
        mask = Image.new("L", (logo_size, logo_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, logo_size, logo_size], radius=60, fill=255)
        img.paste(logo, (logo_badge_x, logo_badge_y), mask)

    # 4. Right: High-Res Perspective Phone Mockup
    if os.path.exists(screenshot_path):
        ss = Image.open(screenshot_path).convert("RGBA")
        ph_w = 1000
        ph_h = 1950
        ss_resized = ss.resize((ph_w, int(ph_w * (ss.height / ss.width))), Image.Resampling.LANCZOS)
        
        chassis_x = 2750
        chassis_y = 220
        
        # Phone chassis shadow
        phone_shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ps_draw = ImageDraw.Draw(phone_shadow)
        ps_draw.rounded_rectangle([chassis_x - 30, chassis_y - 20, chassis_x + ph_w + 30, chassis_y + 1920], radius=130, fill=(0, 0, 0, 200))
        phone_shadow = phone_shadow.filter(ImageFilter.GaussianBlur(radius=80))
        img = Image.alpha_composite(img, phone_shadow)
        draw = ImageDraw.Draw(img)

        # Phone chassis frame
        draw.rounded_rectangle([chassis_x - 20, chassis_y - 20, chassis_x + ph_w + 20, chassis_y + 1900], radius=120, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=8)

        # Screen crop & insert
        crop_box = (0, 0, ph_w, 1870)
        ss_cropped = ss_resized.crop(crop_box)
        ss_mask = Image.new("L", (ph_w, 1870), 0)
        ss_mask_draw = ImageDraw.Draw(ss_mask)
        ss_mask_draw.rounded_rectangle([0, 0, ph_w, 1870], radius=100, fill=255)
        img.paste(ss_cropped, (chassis_x, chassis_y), ss_mask)

    # 5. High-Resolution Typography
    try:
        font_brand = ImageFont.truetype("arialbd.ttf", 145)
        font_tag = ImageFont.truetype("arialbd.ttf", 100)
        font_sub = ImageFont.truetype("arial.ttf", 64)
        font_pill = ImageFont.truetype("courbd.ttf", 46)
        font_stat = ImageFont.truetype("arialbd.ttf", 52)
    except Exception:
        font_brand = ImageFont.load_default()
        font_tag = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_pill = ImageFont.load_default()
        font_stat = ImageFont.load_default()

    # Studio Pill
    pill_x = 1050
    pill_y = 350
    pill_w = 1450
    pill_h = 100
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=50, fill=(15, 23, 42, 230), outline=(51, 65, 85, 220), width=3)
    draw.ellipse([pill_x + 45, pill_y + 35, pill_x + 75, pill_y + 65], fill=(100, 255, 218, 255))
    draw.text((pill_x + 105, pill_y + 22), "RIOMHOIDEAS SOFTWARE LAB", fill=(100, 255, 218, 255), font=font_pill)

    # Main Brand Name
    draw.text((1050, 490), app_name.upper(), fill=(255, 255, 255, 255), font=font_brand)

    # Tagline (Mint Gradient accent)
    draw.text((1050, 690), tagline, fill=(100, 255, 218, 255), font=font_tag)

    # Multi-line Subtitle
    draw.text((280, 1140), subtag, fill=(203, 213, 225, 255), font=font_sub, spacing=28)

    # Bottom Trust Badges
    badges = [
        "100% Offline-First",
        "Zero Telemetry",
        "Local Scoped Database",
        "County Donegal, Ireland"
    ]
    
    start_x = 280
    stat_y = 1840
    for b in badges:
        text_bbox = draw.textbbox((0, 0), b, font=font_stat)
        bw = text_bbox[2] - text_bbox[0] + 80
        bh = 110
        draw.rounded_rectangle([start_x, stat_y, start_x + bw, stat_y + bh], radius=28, fill=(15, 23, 42, 220), outline=(51, 65, 85, 200), width=3)
        draw.text((start_x + 40, stat_y + 24), b, fill=(148, 163, 184, 255), font=font_stat)
        start_x += bw + 36

    # Save output in pristine high quality PNG
    img.convert("RGB").save(output_path, "PNG", quality=98)
    print(f"Generated 4K Play Store Header: {output_path} ({width}x{height})")

if __name__ == "__main__":
    logo = "c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/riomhoideas_logo.jpg"

    # 1. Official Google Play Developer Page Header (4096 x 2304)
    create_developer_header_graphic(
        logo_path=logo,
        screenshot_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/hously_preview_1.png",
        output_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/google_play_header_4096x2304.png",
        app_name="Ríomhoideas",
        tagline="Smarter admin. Zero bloat.",
        subtag="An independent Irish software studio crafting lightweight, secure, and mobile-first\nadministrative utilities for mobile professionals and residential committees.\nPrivate, local-first architecture with 100% data sovereignty."
    )

    # 2. Pocket Office Pro 4K Header (4096 x 2304)
    create_developer_header_graphic(
        logo_path=logo,
        screenshot_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/pocketoffice_preview_1.jpeg",
        output_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/google_play_header_pocketoffice_4096x2304.png",
        app_name="Pocket Office Pro",
        tagline="Invoicing & Sign-Off in Seconds",
        subtag="Professional mobile invoicing, quote generation, and job tracking.\nCapture live client signatures on-site with zero evening paperwork.\nBuilt for mobile contractors, tradesmen, and service technicians."
    )

    # 3. Hously Pro 4K Header (4096 x 2304)
    create_developer_header_graphic(
        logo_path=logo,
        screenshot_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/hously_preview_1.png",
        output_path="c:/Users/patri/Documents/GitHub/riomhoideas/assets/img/google_play_header_hously_4096x2304.png",
        app_name="Hously Pro",
        tagline="Clear Residential Oversight",
        subtag="Smart bank statement scanning, arrears reconciliation, and AGM-ready reports.\nUnified management platform for residential committees, OMCs, and factors.\nScoped local database ensuring complete financial privacy."
    )
