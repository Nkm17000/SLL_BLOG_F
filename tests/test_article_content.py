import unittest
from unittest.mock import patch
from app.article_content import extract_article, summarize_article, build_text_post
from app.facebook_service import FacebookService

class ArticleContentTests(unittest.TestCase):
    def test_extracts_full_article_paragraphs(self):
        html='<html><body><article><h1>Title</h1><p>This article explains a technical system and why the design matters to developers in production.</p><p>It also describes the architecture, deployment trade-offs, and operational considerations that teams should validate before adopting it.</p></article></body></html>'
        text=extract_article(html)
        self.assertIn('architecture',text)
        self.assertGreater(len(text),100)

    def test_fallback_has_five_descriptive_sections(self):
        article=' '.join([f'The system uses component {i} to manage data and coordinate requests across the service in production.' for i in range(1,11)])
        data=summarize_article('Technical system update',article,'RSS snippet','https://example.com/article')
        self.assertEqual(len(data['points']),5)
        self.assertTrue(all(len(p['description'])>30 for p in data['points']))

    def test_text_post_contains_context_and_source_not_images(self):
        data={'description':'This update explains the technical context and why it matters to engineers operating these systems.', 'points':[{'title':f'Section {i}','description':f'Detailed context for section {i} with relevant facts and practical meaning.' ,'items':[]} for i in range(1,6)]}
        post=build_text_post('A technical update',data,'https://example.com/article',app_name='Smart Learning Lab 247')
        self.assertIn('Detailed context for section 3',post)
        self.assertIn('https://example.com/article',post)
        self.assertIn('Smart Learning Lab 247',post)
        self.assertGreater(len(post),500)

    def test_facebook_text_post_sends_one_feed_request(self):
        with patch.object(FacebookService,'_request',return_value={'id':'page_1_post_9'}) as request:
            with patch('app.facebook_service.Config.FACEBOOK_PAGE_ID','page_1'), patch('app.facebook_service.Config.FACEBOOK_PAGE_TOKEN','token'):
                result=FacebookService.post_text('A sufficiently detailed technical article ' * 20)
        self.assertEqual(result['post_id'],'page_1_post_9')
        self.assertEqual(request.call_count,1)
        self.assertTrue(request.call_args.args[1].endswith('/feed'))
        self.assertNotIn('files',request.call_args.kwargs)

if __name__=='__main__': unittest.main()
