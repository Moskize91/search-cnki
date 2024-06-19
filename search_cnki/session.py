import requests

from .interval_limiter import IntervalLimiter
from .query_builder import Query
from .search_response import SearchResponse

class Session:
  def __init__(self) -> None:
    self._limiter: IntervalLimiter = IntervalLimiter(1.0)
    self._session = requests.Session()
    self._session.get("http://kns.cnki.net/kns/brief/result.aspx")

  def search(self, query: Query) -> SearchResponse:
    return SearchResponse(query, self._limiter, self._session)
