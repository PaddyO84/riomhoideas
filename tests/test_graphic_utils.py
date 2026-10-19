import os
import sys
import unittest
import tempfile
from PIL import Image

# Add scratch directory to sys.path
scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scratch'))
if scratch_dir not in sys.path:
    sys.path.insert(0, scratch_dir)

from graphic_utils import (
    GraphicConfig,
    create_gradient_background,
    add_ambient_glows,
    render_logo_badge,
    render_phone_screenshot,
    load_image,
    load_font
)


class TestGraphicUtils(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_img = Image.new("RGBA", (200, 100), (10, 20, 30, 255))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_graphic_config_default_badges(self):
        """Verifies that GraphicConfig.__post_init__ assigns default badges when none provided."""
        config = GraphicConfig(
            logo_path="dummy_logo.png",
            screenshot_path="dummy_ss.png",
            output_path="dummy_out.png",
            app_name="App",
            tagline="Tag",
            subtag="Sub"
        )
        expected_badges = [
            "100% Offline-First",
            "Zero Telemetry",
            "Local Scoped Database",
            "County Donegal, Ireland"
        ]
        self.assertEqual(config.badges, expected_badges)

    def test_render_logo_badge_missing_path_returns_original_image(self):
        """Verifies render_logo_badge returns original image unmodified if logo path does not exist."""
        missing_path = os.path.join(self.temp_dir.name, "non_existent_logo.png")
        result = render_logo_badge(
            img=self.test_img,
            logo_path=missing_path,
            x=10,
            y=10,
            size=50,
            badge_radius=10,
            badge_pad=5
        )
        self.assertIs(result, self.test_img)

    def test_render_phone_screenshot_missing_path_returns_original_image(self):
        """Verifies render_phone_screenshot returns original image unmodified if screenshot path does not exist."""
        missing_path = os.path.join(self.temp_dir.name, "non_existent_ss.png")
        result = render_phone_screenshot(
            img=self.test_img,
            screenshot_path=missing_path,
            chassis_x=10,
            chassis_y=10,
            ph_w=50,
            crop_h=80
        )
        self.assertIs(result, self.test_img)

    def test_create_gradient_background_height_one_edge_case(self):
        """Verifies that create_gradient_background handles height=1 without ZeroDivisionError."""
        top_color = (10, 25, 47, 255)
        bottom_color = (4, 11, 21, 255)
        grad = create_gradient_background(width=50, height=1, top_color=top_color, bottom_color=bottom_color)
        self.assertEqual(grad.size, (50, 1))
        self.assertEqual(grad.mode, "RGBA")

    def test_create_gradient_background_dimensions_and_colors(self):
        """Verifies that create_gradient_background generates expected dimensions and base colors."""
        top_color = (10, 25, 47, 255)
        bottom_color = (4, 11, 21, 255)
        width, height = 200, 100
        grad = create_gradient_background(width=width, height=height, top_color=top_color, bottom_color=bottom_color)

        self.assertEqual(grad.size, (width, height))
        self.assertEqual(grad.mode, "RGBA")

        # Check top pixel (y=0) and bottom pixel (y=height-1)
        top_pixel = grad.getpixel((width // 2, 0))
        bottom_pixel = grad.getpixel((width // 2, height - 1))
        self.assertEqual(top_pixel, top_color)
        self.assertEqual(bottom_pixel, bottom_color)

    def test_load_image_caching(self):
        """Verifies that load_image caches the PIL Image in memory across calls."""
        img_path = os.path.join(self.temp_dir.name, "sample.png")
        sample = Image.new("RGBA", (64, 64), (100, 150, 200, 255))
        sample.save(img_path)

        first_loaded = load_image(img_path)
        second_loaded = load_image(img_path)
        self.assertIs(first_loaded, second_loaded)

    def test_load_image_missing_file_raises_error(self):
        """Item 1: Verifies load_image raises FileNotFoundError when given a non-existent file path."""
        non_existent = os.path.join(self.temp_dir.name, "does_not_exist.png")
        with self.assertRaises((FileNotFoundError, OSError)):
            load_image(non_existent)

    def test_add_ambient_glows(self):
        """Item 2: Verifies add_ambient_glows composites glowing orbs onto image without changing canvas dimensions."""
        base_img = Image.new("RGBA", (400, 300), (10, 20, 30, 255))
        result = add_ambient_glows(base_img, 400, 300, blur_radius=20)
        self.assertEqual(result.size, (400, 300))
        self.assertEqual(result.mode, "RGBA")

    def test_load_font_caching_and_fallback(self):
        """Item 3: Verifies load_font returns a font, caches it, and safely falls back on non-existent fonts."""
        fallback_font = load_font("non_existent_font_12345.ttf", 24)
        self.assertIsNotNone(fallback_font)

        second_load = load_font("non_existent_font_12345.ttf", 24)
        self.assertIs(fallback_font, second_load)

    def test_render_logo_badge_success_path(self):
        """Item 15: Verifies render_logo_badge successfully composites logo onto canvas when logo path exists."""
        logo_path = os.path.join(self.temp_dir.name, "valid_logo.png")
        logo_img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        logo_img.save(logo_path)

        base_img = Image.new("RGBA", (300, 300), (10, 20, 30, 255))
        result = render_logo_badge(
            img=base_img,
            logo_path=logo_path,
            x=20,
            y=20,
            size=60,
            badge_radius=12,
            badge_pad=8,
            border_width=2
        )
        self.assertEqual(result.size, (300, 300))
        self.assertEqual(result.mode, "RGBA")
        self.assertIsNot(result, base_img)


if __name__ == '__main__':
    unittest.main()
