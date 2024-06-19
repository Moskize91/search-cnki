import requests

from .interval_limiter import IntervalLimiter
from .query_builder import Query
from .search_response import SearchResponse
from .article_fetcher import Article, ArticleFetcher

class Session:
  def __init__(self, cookies: dict = None) -> None:
    self._limiter: IntervalLimiter = IntervalLimiter(1.0)
    self._session = requests.Session()
    self._article_fetcher: ArticleFetcher = ArticleFetcher(self._limiter, self._session)

    if cookies is not None:
      self._session.cookies.update(cookies)

  def search(self, query: Query) -> SearchResponse:
    return SearchResponse(query, self._limiter, self._session)

  def article(self, href: str) -> Article:
    return self._article_fetcher.article(href)
