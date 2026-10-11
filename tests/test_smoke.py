import unittest
from app.article_content import build_text_post, _bold_unicode
from app.config import Config

class ProjectSmokeTests(unittest.TestCase):
    def test_config_brand(self):
        self.assertEqual(Config.APP_NAME, 'Smart Learning Lab 247')
    def test_text_post_has_five_contextual_sections(self):
        blog={'description':'A source-based summary explaining the development and its technical context.', 'points':[{'title':f'Section {i}','description':f'This section explains the technical detail and its relevance to implementation number {i}.','items':[]} for i in range(1,6)]}
        post=build_text_post('A meaningful technical report',blog,'https://example.com/article',app_name=Config.APP_NAME)
        self.assertEqual(sum(1 for i in range(1,6) if _bold_unicode(f'Section {i}') in post),5)
        self.assertIn('https://example.com/article',post)
        self.assertIn('https://smartlearninglab-react.pages.dev/', post)
        self.assertIn('https://www.instagram.com/smartlearninglab247', post)
        self.assertIn('https://www.youtube.com/@smartlearninglab247', post)
        self.assertIn('https://www.facebook.com/smartlearninglab247', post)
        self.assertIn(_bold_unicode('What this means'), post)
if __name__=='__main__': unittest.main()
