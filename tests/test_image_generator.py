import tempfile, unittest
from pathlib import Path
from PIL import Image
from app.image_generator import create_blog_image

class ImageGeneratorTests(unittest.TestCase):
    def test_renders_blog_content_as_1080x1350_image(self):
        blog = {
            'technical_topic': 'Understanding HTTP Caching',
            'description': 'HTTP caching helps browsers reuse previously downloaded resources and reduce repeated network requests.',
            'points': [
                {'title': f'Section {i}', 'description': ('This detailed section explains the technology, how it works, and the practical implications for developers. ' * 3)}
                for i in range(1, 6)
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path, palette = create_blog_image(blog, 'https://developer.mozilla.org/docs/Web/HTTP/Caching', 'Smart Learning Lab 247', Path(tmp)/'post.jpg')
            self.assertTrue(path.is_file())
            self.assertIn(palette, range(6))
            with Image.open(path) as image:
                self.assertEqual(image.size, (1080, 1350))
                self.assertEqual(image.format, 'JPEG')

    def test_palette_avoids_last_five_palettes(self):
        blog = {'technical_topic':'Topic','description':'An explanation long enough for a test image.','points':[{'title':f'Section {i}','description':'Detailed technical context for this section.'} for i in range(5)]}
        with tempfile.TemporaryDirectory() as tmp:
            _, palette = create_blog_image(blog, 'https://example.com/source', 'SLL', Path(tmp)/'recent.jpg', recent_palettes=[0,1,2,3,4])
            self.assertEqual(palette, 5)

    def test_palette_changes_from_previous_run(self):
        blog = {'technical_topic':'Topic','description':'An explanation long enough for a test image.','points':[{'title':f'Section {i}','description':'Detailed technical context for this section.'} for i in range(5)]}
        with tempfile.TemporaryDirectory() as tmp:
            _, palette = create_blog_image(blog, 'https://example.com/source', 'SLL', Path(tmp)/'one.jpg', previous_palette=2)
            self.assertNotEqual(palette, 2)

if __name__ == '__main__': unittest.main()
