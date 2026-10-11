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
from make_feature_graphics import create_feature_graphic


class TestFeatureGraphics(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create dummy logo (100x100)
        self.logo_path = os.path.join(self.temp_dir.name, "logo.png")
        logo_img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        logo_img.save(self.logo_path)

        # Create dummy screenshot (300x600)
        self.screenshot_path = os.path.join(self.temp_dir.name, "screenshot.png")
        ss_img = Image.new("RGBA", (300, 600), (0, 255, 0, 255))
        ss_img.save(self.screenshot_path)

        self.output_path = os.path.join(self.temp_dir.name, "output_feature.png")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_feature_graphic_success(self):
        config = GraphicConfig(
            logo_path=self.logo_path,
            screenshot_path=self.screenshot_path,
            output_path=self.output_path,
            app_name="TestApp",
            tagline="Test Tagline",
            subtag="Test Subtag",
            width=1024,
            height=500,
            badges=["Feature A", "Feature B"]
        )

        create_feature_graphic(config)

        self.assertTrue(os.path.exists(self.output_path), "Output image file should be created")

        with Image.open(self.output_path) as img:
            self.assertEqual(img.size, (1024, 500), "Generated image dimensions should be 1024x500")
            self.assertEqual(img.format, "PNG", "Generated image should be PNG format")


if __name__ == '__main__':
    unittest.main()
