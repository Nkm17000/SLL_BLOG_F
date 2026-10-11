import unittest, os, json
from unittest.mock import patch, Mock
from app.article_content import extract_article, summarize_article, build_text_post
from app.facebook_service import FacebookService

class ArticleContentTests(unittest.TestCase):
    def test_extracts_full_article_paragraphs(self):
        html='<html><body><article><h1>Title</h1><p>This article explains a technical system and why the design matters to developers in production.</p><p>It also describes the architecture, deployment trade-offs, and operational considerations that teams should validate before adopting it.</p></article></body></html>'
        text=extract_article(html)
        self.assertIn('architecture',text)
        self.assertGreater(len(text),100)

    def test_groq_creates_five_substantive_sections(self):
        article=' '.join([f'The system uses component {i} to manage data and coordinate requests across the service in production, with documented interfaces and operational trade-offs.' for i in range(1,16)])
        points=[{'title':f'Specific technical section {i}','description':(f'This detailed section explains component {i}, the role it plays in the reported architecture, and what the article specifically says about its operation, implementation context, and limitations. ' * 3),'items':[f'Article fact {i}']} for i in range(1,6)]
        payload={'technical_topic':'Technical system architecture update','description':'A detailed overview grounded in the full source article. It explains the reported development, the named technical components, and the implementation context without adding unsupported claims and with practical technical context for readers.','points':points}
        response=Mock(); response.raise_for_status.return_value=None; response.json.return_value={'choices':[{'message':{'content':json.dumps(payload)}}]}
        with patch.dict(os.environ,{'GROQ_API_KEY':'test-key','GROQ_MODEL':'openai/gpt-oss-120b'}), patch('app.article_content.requests.post',return_value=response) as groq:
            data=summarize_article('Technical system update',article,'RSS snippet','https://example.com/article')
        self.assertEqual(len(data['points']),5)
        self.assertTrue(all(len(p['description'])>=280 for p in data['points']))
        self.assertEqual(data['summary_mode'],'groq_full_article')
        self.assertEqual(groq.call_args.kwargs['json']['model'],'openai/gpt-oss-120b')

    def test_refuses_rss_only_summary(self):
        with patch.dict(os.environ,{'GROQ_API_KEY':'test-key'}):
            with self.assertRaisesRegex(RuntimeError,'too short'):
                summarize_article('Headline','Only a short snippet.','Only a short snippet.','https://example.com/article')

    def test_requires_groq_key(self):
        article='A complete article with useful technical context. ' * 30
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,'GROQ_API_KEY is required'):
                summarize_article('Technical update',article,'RSS','https://example.com/article')

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

class PublisherUrlResolutionTests(unittest.TestCase):
    def test_resolves_canonical_publisher_url(self):
        from app.article_content import _publisher_url
        page='<html><head><link rel="canonical" href="https://publisher.example.com/story/123"></head></html>'
        self.assertEqual(_publisher_url(page,'https://news.google.com/rss/articles/abc'), 'https://publisher.example.com/story/123')
