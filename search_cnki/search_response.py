import requests
import threading

from typing import Iterator
from lxml import html

from .common import Referer, check_is_verify_page, first_ele, dom_text
from .link import ArticleLink, AuthorLink, SourceLink
from .query_builder import Query
from .interval_limiter import IntervalLimiter
from .exception import TimeoutVerifyException

class SearchResponse:
  def __init__(
      self,
      query: Query,
      lock: threading.Lock,
      limiter: IntervalLimiter,
      session: requests.Session,
      user_agent: str,
    ):
    self._query_json: dict = query.json()
    self._lock: threading.Lock = lock
    self._limiter: IntervalLimiter = limiter
    self._session: requests.Session = session
    self._user_agent: str = user_agent
    self._current_page: int = 0
    root = self._request(self._current_page)

    if check_is_verify_page(root):
      raise TimeoutVerifyException("search timeout")

    self.count = self._get_items_count(root)

    if self.count > 0:
      self._articles = self._get_articles(root)
    else:
      self._articles = []

  def __iter__(self):
      return SearchResponseIterable(self)

  def _fetch_article(self, index: int) -> ArticleLink:
    while index >= len(self._articles):
      self._current_page += 1
      root = self._request(self._current_page)
      articles = self._get_articles(root)
      self._articles.extend(articles)

    return self._articles[index]

  def _request(self, cur_page: int):
    self._limiter.limit()
    search_url = "https://kns.cnki.net/kns8s/brief/grid"
    post_data = {
      "boolSearch": True,
      "queryJson": self._query_json,
      "aside": "主题：未知",
      "pageNum": 1,
      "pageSize": 20,
      "sortField": "",
      "sortType": "",
      "dstyle": "listmode",
      # flake8: noqa
      "productStr": "YSTT4HG0,LSTPFY1C,RMJLXHZ3,JQIRZIYA,JUP3MUPD,1UR4K4HZ,BPBAFJ5S,R79MZMCB,MPMFIG1A,WQ0UVIAA,NB3BWEHK,XVLO76FD,HR1YT1Z9,BLZOG7CK,EMRPGLPA,J708GVCE,ML4DRIDX,PWFIRAGL,NLBO1Z6R,NN3FJMUV,",
      "searchFrom": "资源范围：总库",
      "CurPage": cur_page + 1,
    }
    with self._lock:
      post_resp = self._session.post(
        search_url,
        data=post_data,
        headers={
          "User-Agent": self._user_agent,
          "Referer": Referer,
        },
      )
    return html.fromstring(post_resp.text)

  def _get_items_count(self, root) -> int:
    child = first_ele(root.xpath('//span[@class="pagerTitleCell"]/em/text()'))
    if child is not None:
      # 大数字计数，知网会插入逗号，例如： 23,423
      return int(child.replace(",", ""))
    else:
      return 0

  def _get_articles(self, root) -> list[ArticleLink]:
    articles: list[ArticleLink] = []
    table_body = first_ele(root.xpath('//div[@id="gridTable"]//table[@class="result-table-list"]//tbody'))

    if table_body is None:
      return articles

    for tr_dom in table_body.getchildren():
      if tr_dom.tag != "tr":
        continue

      title_dom = first_ele(tr_dom.xpath('td[@class="name"]/a'))
      title: str = ""
      href: str = ""

      if title_dom is not None:
        title = dom_text(title_dom)
        href = title_dom.get("href")

      author_dom = first_ele(tr_dom.xpath('td[@class="author"]'))
      authors: list[AuthorLink] = []

      if author_dom is not None:
        for a_dom in author_dom.getchildren():
          if a_dom.tag != "a":
            continue
          authors.append(AuthorLink(
            name=dom_text(a_dom),
            href=a_dom.get("href"),
          ))

      source_dom = first_ele(tr_dom.xpath('td[@class="source"]/a'))
      source: SourceLink = None

      if source_dom is not None:
        source = SourceLink(
          name=dom_text(source_dom),
          href=source_dom.get("href"),
        )

      published_at_dom = first_ele(tr_dom.xpath('td[@class="date"]'))
      published_at: str = ""

      if published_at_dom is not None:
        published_at = dom_text(published_at_dom)

      articles.append(ArticleLink(
        title=title,
        href=href,
        published_at=published_at,
        authors=authors,
        source=source,
      ))

    return articles

class SearchResponseIterable:
  def __init__(self, parent: SearchResponse) -> None:
    self._parent = parent
    self._index = -1

  def __iter__(self) -> Iterator[ArticleLink]:
      return self

  def __next__(self) -> ArticleLink:
      if self._index >= self._parent.count:
          raise StopIteration
      article = self._parent._fetch_article(self._index)
      self._index += 1
      return article
