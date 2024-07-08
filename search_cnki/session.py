import requests
import threading

from .interval_limiter import IntervalLimiter
from .query_builder import Query
from .search_response import SearchResponse
from .article_fetcher import Article, ArticleFetcher

# thread safe object
class Session:
  def __init__(self, cookies: dict = None) -> None:
    self._limiter: IntervalLimiter = IntervalLimiter(1.0)
    self._lock: threading.Lock = threading.Lock()
    self._session = requests.Session()
    self._article_fetcher: ArticleFetcher = ArticleFetcher(
      self._limiter,
      self._lock,
      self._session,
    )
    if cookies is not None:
      self._session.cookies.update(cookies)

  def set_cookies(self, cookies: dict) -> None:
    with self._lock:
      self._session.cookies.update(cookies)

  def search(self, query: Query) -> SearchResponse:
    return SearchResponse(query, self._lock, self._limiter, self._session)

  # href 本身可能过期，此时会抛出 TimeoutVerifyException
  # 在重新验证之后，请刷新以获取新的 href 重新调用
  def article(self, href: str) -> Article:
    return self._article_fetcher.article(href)

  def download_pdf(self, href: str, from_url: str, file_path: str):
    self._article_fetcher.download_pdf(href, from_url, file_path)
