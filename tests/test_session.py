import os
import unittest

from search_cnki import Query, Session
from search_cnki.search_response import ArticleLink

def add(a, b):
  return a + b

class TestSession(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(TestSession, self).__init__(*args, **kwargs)
    self.session = Session()

  def test_search_one_article(self):
     title = "“三孩”政策背景下我国乡村生育政策的创新与完善研究"
     author = "周晓焱"
     query = Query().subject(title).author(author)
     response = self.session.search(query)
     self.assertEqual(response.count, 1)
     first_article: ArticleLink = None

     for article in response:
       first_article = article
       break

     self.assertEqual(first_article.title, title)
     self.assertEqual([a.name for a in first_article.authors], [author])

  def test_search_many_articles(self):
    query = Query().subject("中国特色社会主义")
    response = self.session.search(query)
    count = 0
    for _ in response:
      count += 1
      if count > 30:
        break

  def test_fetch_article(self):
    # flake8: noqa
    article_url = "https://kns.cnki.net/kcms2/article/abstract?v=n93avYlexq_wcpkdlval-RrkJ_fo69qIlWxxlDbicofOqqPOq6vlUHin12KU4rScuhDEuIPoIgvtx4qFoKyFjkdayNceSP9u5_tvwmwAAjPHQUBLstWmtbiD2U8_IWL4JkkDio3rgDy_SPeXgyxicg==&uniplatform=NZKPT&language=CHS"
    article = self.session.article(article_url)
    self.assertEqual(article.title, "一份调查报告里的务实作风")
    self.assertEqual(article.doi, "10.14061/j.cnki.cn13-1033/d.2024.11.025")

    # 需要登陆才能下载，测试时记得加 Cookies
    # self.session.download_pdf(
    #   article.pdf_href,
    #   article_url,
    #   os.path.normpath(os.path.join(
    #     os.path.dirname(os.path.abspath(__file__)),
    #     "../dist/test.pdf",
    #   )),
    # )


if __name__ == "__main__":
  unittest.main()
