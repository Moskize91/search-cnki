import requests

from lxml import html, etree
from .data import Article, Author, Source
from .query_builder import Query
from .interval_limiter import IntervalLimiter

class SearchResponse:
  def __init__(self, query: Query, limiter: IntervalLimiter, session: requests.Session):
    self._limiter: IntervalLimiter = limiter
    self._query_json: dict = query.json()
    self._session: requests.Session = session
    self._current_page: int = 0
    root = self._request(self._current_page)
    self.count = self._get_items_count(root)

    if self.count > 0:
      self._articles = self._get_articles(root)
    else:
      self._articles = []

  def __iter__(self):
      return SearchResponseIterable(self)

  def _fetch_article(self, index: int) -> Article:
    while index >= len(self._articles):
      self._current_page += 1
      root = self._request(self._current_page)
      articles = self._get_articles(root)
      self._articles.extend(articles)

    return self._articles[index]

  def _request(self, cur_page: int):
    self._limiter.limit()
    self._session.get("https://kns.cnki.net/")
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
    post_resp = self._session.post(search_url, data=post_data, headers={
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
      "Referer": "https://kns.cnki.net/kns8s/defaultresult",
    })
    return html.fromstring(post_resp.text)

  def _get_items_count(self, root) -> int:
    child = first_ele(root.xpath('//span[@class="pagerTitleCell"]/em/text()'))
    if child is not None:
      # 大数字计数，知网会插入逗号，例如： 23,423
      return int(child.replace(",", ""))
    else:
      return 0

  def _get_articles(self, root) -> list[Article]:
    articles: list[Article] = []
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
        title = etree.tostring(title_dom, method="text", encoding="unicode").strip()
        href = title_dom.get("href")

      author_dom = first_ele(tr_dom.xpath('td[@class="author"]'))
      authors: list[Author] = []

      if author_dom is not None:
        for a_dom in author_dom.getchildren():
          if a_dom.tag != "a":
            continue
          authors.append(Author(
            name=etree.tostring(a_dom, method="text", encoding="unicode").strip(),
            href=a_dom.get("href"),
          ))

      source_dom = first_ele(tr_dom.xpath('td[@class="source"]/a'))
      source: Source = None

      if source_dom is not None:
        source = Source(
          name=etree.tostring(source_dom, method="text", encoding="unicode").strip(),
          href=source_dom.get("href"),
        )

      published_at_dom = first_ele(tr_dom.xpath('td[@class="date"]'))
      published_at: str = ""

      if published_at_dom is not None:
        published_at = etree.tostring(published_at_dom, method="text", encoding="unicode").strip()

      articles.append(Article(
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

  def __iter__(self):
      return self

  def __next__(self):
      if self._index >= self._parent.count:
          raise StopIteration
      article = self._parent._fetch_article(self._index)
      self._index += 1
      return article

class Session:
  def __init__(self) -> None:
    self._limiter: IntervalLimiter = IntervalLimiter(1.0)
    self._session = requests.Session()
    self._session.get("http://kns.cnki.net/kns/brief/result.aspx")

  def search(self, query: Query) -> SearchResponse:
    return SearchResponse(query, self._limiter, self._session)


def first_ele(elements: list):
  for element in elements:
    return element
  return None