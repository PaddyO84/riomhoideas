import functools
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter


@functools.lru_cache(maxsize=32)
def load_image(image_path: str) -> Image.Image:
    """
    Loads and caches RGBA PIL images in memory to prevent repeated disk I/O.
    """
    return Image.open(image_path).convert("RGBA")

@dataclass
class GraphicConfig:
    logo_path: str
    screenshot_path: str
    output_path: str
    app_name: str
    tagline: str
    subtag: str
    width: int = 1024
    height: int = 500
    badges: Optional[List[str]] = None

    def __post_init__(self):
        if self.badges is None:
            self.badges = [
                "100% Offline-First",
                "Zero Telemetry",
                "Local Scoped Database",
                "County Donegal, Ireland"
            ]


def create_gradient_background(width: int, height: int, top_color: Tuple[int, int, int, int], bottom_color: Tuple[int, int, int, int]) -> Image.Image:
    """
    Generates a vertical linear gradient canvas in near-zero time using 1D image scaling.
    Replaces slow line-by-line pixel loops.
    """
    gradient_1d = Image.new("RGBA", (1, height))
    draw_1d = ImageDraw.Draw(gradient_1d)

    for y in range(height):
        ratio = y / float(height - 1) if height > 1 else 0.0
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        a = int(top_color[3] * (1 - ratio) + bottom_color[3] * ratio)
        draw_1d.point((0, y), fill=(r, g, b, a))

    return gradient_1d.resize((width, height), Image.Resampling.NEAREST)


def add_ambient_glows(img: Image.Image, width: int, height: int, blur_radius: int = 60, glows: Optional[List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]]] = None) -> Image.Image:
    """
    Applies atmospheric glowing radial orbs onto the canvas.
    """
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    if glows is None:
        glows = [
            ((-100, -50, 450, 500), (100, 255, 218, 40)),
            ((650, 50, 1150, 550), (0, 229, 255, 30))
        ]

    for bbox, fill in glows:
        glow_draw.ellipse(bbox, fill=fill)

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return Image.alpha_composite(img, glow_layer)


def render_logo_badge(img: Image.Image, logo_path: str, x: int, y: int, size: int, badge_radius: int, badge_pad: int, border_width: int = 2) -> Image.Image:
    """
    Renders a soft glowing logo badge and inserts the rounded logo image.
    """
    if not os.path.exists(logo_path):
        return img

    width, height = img.size
    logo = load_image(logo_path).copy()
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)

    badge_rect = [
        x - badge_pad,
        y - badge_pad,
        x + size + badge_pad,
        y + size + badge_pad
    ]

    # Outer glow
    badge_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(badge_glow)
    bg_draw.rounded_rectangle(badge_rect, radius=badge_radius, fill=(100, 255, 218, 80))
    badge_glow = badge_glow.filter(ImageFilter.GaussianBlur(radius=int(badge_pad * 0.8)))
    img = Image.alpha_composite(img, badge_glow)

    # Frame
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(badge_rect, radius=badge_radius, fill=(7, 17, 32, 240), outline=(100, 255, 218, 200), width=border_width)

    # Rounded logo mask
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=int(badge_radius * 0.7), fill=255)
    img.paste(logo, (x, y), mask)

    return img


def render_phone_screenshot(img: Image.Image, screenshot_path: str, chassis_x: int, chassis_y: int, ph_w: int, crop_h: int, corner_radius: int = 24, border_width: int = 2) -> Image.Image:
    """
    Renders a perspective phone chassis frame with drop shadow and cropped screenshot.
    """
    if not os.path.exists(screenshot_path):
        return img

    width, height = img.size
    ss = load_image(screenshot_path).copy()
    ss_resized = ss.resize((ph_w, int(ph_w * (ss.height / ss.width))), Image.Resampling.LANCZOS)

    # Drop shadow
    phone_shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ps_draw = ImageDraw.Draw(phone_shadow)
    shadow_margin = int(ph_w * 0.04)
    ps_draw.rounded_rectangle([chassis_x - shadow_margin, chassis_y - shadow_margin, chassis_x + ph_w + shadow_margin, chassis_y + crop_h + shadow_margin], radius=corner_radius + 6, fill=(0, 0, 0, 180))
    phone_shadow = phone_shadow.filter(ImageFilter.GaussianBlur(radius=int(corner_radius * 0.8)))
    img = Image.alpha_composite(img, phone_shadow)

    # Frame
    draw = ImageDraw.Draw(img)
    margin = border_width * 3
    draw.rounded_rectangle([chassis_x - margin, chassis_y - margin, chassis_x + ph_w + margin, chassis_y + crop_h + margin], radius=corner_radius + 6, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=border_width)

    # Screenshot insertion
    crop_box = (0, 0, ph_w, crop_h)
    ss_cropped = ss_resized.crop(crop_box)
    ss_mask = Image.new("L", (ph_w, crop_h), 0)
    ss_mask_draw = ImageDraw.Draw(ss_mask)
    ss_mask_draw.rounded_rectangle([0, 0, ph_w, crop_h], radius=corner_radius, fill=255)
    img.paste(ss_cropped, (chassis_x, chassis_y), ss_mask)

    return img
