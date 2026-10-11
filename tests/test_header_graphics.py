import os
import sys
import unittest
import tempfile
from PIL import Image

# Add scratch directory to sys.path
scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scratch'))
if scratch_dir not in sys.path:
    sys.path.insert(0, scratch_dir)

from graphic_utils import GraphicConfig
from make_4096x2304_headers import create_developer_header_graphic


class TestHeaderGraphics(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create dummy logo (200x200)
        self.logo_path = os.path.join(self.temp_dir.name, "logo.png")
        logo_img = Image.new("RGBA", (200, 200), (255, 0, 0, 255))
        logo_img.save(self.logo_path)

        # Create dummy screenshot (400x800)
        self.screenshot_path = os.path.join(self.temp_dir.name, "screenshot.png")
        ss_img = Image.new("RGBA", (400, 800), (0, 255, 0, 255))
        ss_img.save(self.screenshot_path)

        self.output_path = os.path.join(self.temp_dir.name, "output_header.png")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_developer_header_graphic_success(self):
        config = GraphicConfig(
            logo_path=self.logo_path,
            screenshot_path=self.screenshot_path,
            output_path=self.output_path,
            app_name="TestApp 4K",
            tagline="4K Tagline",
            subtag="4K Subtag Description",
            width=4096,
            height=2304,
            badges=["4K Feature 1", "4K Feature 2"]
        )

        create_developer_header_graphic(config)

        self.assertTrue(os.path.exists(self.output_path), "4K Header output image file should be created")

        with Image.open(self.output_path) as img:
            self.assertEqual(img.size, (4096, 2304), "Generated image dimensions should be 4096x2304")
            self.assertEqual(img.format, "PNG", "Generated image should be PNG format")


if __name__ == '__main__':
    unittest.main()
