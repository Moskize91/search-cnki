import requests
import threading

from .interval_limiter import IntervalLimiter
from .query_builder import Query
from .search_response import SearchResponse
from .article_fetcher import Article, ArticleFetcher

# thread safe object
class Session:
  def __init__(
    self,
    cookies: dict = None,
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
  ) -> None:
    self._user_agent: str = user_agent
    self._limiter: IntervalLimiter = IntervalLimiter(1.0)
    self._lock: threading.Lock = threading.Lock()
    self._session = requests.Session()
    self._article_fetcher: ArticleFetcher = ArticleFetcher(
      limiter=self._limiter,
      lock=self._lock,
      session=self._session,
      user_agent=user_agent,
    )
    if cookies is not None:
      self._session.cookies.update(cookies)

  def set_cookies(self, cookies: dict) -> None:
    with self._lock:
      self._session.cookies.update(cookies)

  def search(self, query: Query) -> SearchResponse:
    return SearchResponse(
      query,
      lock=self._lock,
      limiter=self._limiter,
      session=self._session,
      user_agent=self._user_agent,
    )

  # href 本身可能过期，此时会抛出 TimeoutVerifyException
  # 在重新验证之后，请刷新以获取新的 href 重新调用
  def article(self, href: str) -> Article:
    return self._article_fetcher.article(href)

  def download_pdf(self, href: str, from_url: str, file_path: str):
    self._article_fetcher.download_pdf(href, from_url, file_path)
