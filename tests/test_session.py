import unittest

from search_cnki import Query, Session
from search_cnki.search_response import SearchArticle

def add(a, b):
  return a + b

class TestSession(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(TestSession, self).__init__(*args, **kwargs)
    self.session = Session()

  def test_search_one_article(self):
     title = "三孩政策背景下我国生育政策转型研究"
     author = "王涛"
     query = Query().subject(title).author(author)
     response = self.session.search(query)
     self.assertEqual(response.count, 1)
     first_article: SearchArticle = None

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


if __name__ == "__main__":
  unittest.main()
