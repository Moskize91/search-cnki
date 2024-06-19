import unittest

from search_cnki import Query, Session

def add(a, b):
  return a + b

class TestSession(unittest.TestCase):

  def test_search_title(self):
     session = Session()
     query = Query().subject("中国").author("冯文韬")
     session.search(query)


if __name__ == '__main__':
    unittest.main()
