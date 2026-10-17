import os
import sys
import unittest
from PIL import Image

# Add scratch directory to sys.path
scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scratch'))
if scratch_dir not in sys.path:
    sys.path.insert(0, scratch_dir)

from graphic_utils import (
    GraphicConfig,
    create_gradient_background,
    render_logo_badge,
    render_phone_screenshot
)


class TestGraphicUtils(unittest.TestCase):

    def test_graphic_config_defaults(self):
        config = GraphicConfig(
            logo_path="logo.png",
            screenshot_path="ss.png",
            output_path="out.png",
            app_name="TestApp",
            tagline="Tagline",
            subtag="Subtag"
        )
        self.assertIsNotNone(config.badges)
        self.assertIn("100% Offline-First", config.badges)
        self.assertIn("Zero Telemetry", config.badges)
        self.assertEqual(config.width, 1024)
        self.assertEqual(config.height, 500)

    def test_create_gradient_background_standard(self):
        top_color = (10, 25, 47, 255)
        bottom_color = (4, 11, 21, 255)
        img = create_gradient_background(100, 200, top_color, bottom_color)
        self.assertEqual(img.size, (100, 200))
        self.assertEqual(img.mode, "RGBA")

        top_pixel = img.getpixel((0, 0))
        bottom_pixel = img.getpixel((0, 199))
        self.assertEqual(top_pixel, top_color)
        self.assertEqual(bottom_pixel, bottom_color)

    def test_create_gradient_background_height_one_edge_case(self):
        top_color = (100, 100, 100, 255)
        bottom_color = (200, 200, 200, 255)
        # Should handle height=1 without ZeroDivisionError
        img = create_gradient_background(50, 1, top_color, bottom_color)
        self.assertEqual(img.size, (50, 1))

    def test_render_logo_badge_missing_file(self):
        base_img = Image.new("RGBA", (500, 500), (0, 0, 0, 255))
        result = render_logo_badge(base_img, "non_existent_logo.png", 50, 50, 100, 20, 10)
        self.assertIs(result, base_img)

    def test_render_phone_screenshot_missing_file(self):
        base_img = Image.new("RGBA", (500, 500), (0, 0, 0, 255))
        result = render_phone_screenshot(base_img, "non_existent_screenshot.png", 50, 50, 200, 300)
        self.assertIs(result, base_img)


if __name__ == '__main__':
    unittest.main()
