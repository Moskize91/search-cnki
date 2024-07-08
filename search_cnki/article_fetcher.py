import requests
import threading

from lxml import html
from urllib.parse import urljoin

from .link import AuthorLink
from .common import headers, check_is_verify_page, first_ele, dom_text
from .interval_limiter import IntervalLimiter
from .exception import TimeoutVerifyException, AuthVerifyException

class Article:
  def __init__(
    self,
    title: str,
    authors: list[AuthorLink],
    abstract: str,
    keywords: list[str],
    doi: str,
    pdf_href: str,
    html_href: str,
  ) -> None:
    self.title: str = title
    self.authors: list[AuthorLink] = authors
    self.abstract: str = abstract
    self.keywords: list[str] = keywords
    self.doi: str = doi
    self.pdf_href: str = pdf_href
    self.html_href: str = html_href

# thread safe object
class ArticleFetcher:
  def __init__(self, limiter: IntervalLimiter, lock: threading.Lock, session: requests.Session):
    self._limiter: IntervalLimiter = limiter
    self._lock: threading.Lock = lock
    self._session: requests.Session = session

  def article(self, href: str) -> Article:
    self._limiter.limit()
    with self._lock:
      resp = self._session.get(href, headers=headers())

    root = html.fromstring(resp.text)
    if check_is_verify_page(root):
      raise TimeoutVerifyException("read article timeout")

    meta_info_prefix = '//div[@class="brief"]//div[@class="wx-tit"]'
    title_dom = first_ele(root.xpath(f'{meta_info_prefix}//h1'))
    title: str = ""

    if title_dom is not None:
      title = dom_text(title_dom)

    authors: list[AuthorLink] = []
    author_panel_dom = title_dom.getnext()

    if author_panel_dom is not None and author_panel_dom.tag == "h3":
      for child in author_panel_dom.getchildren():
        if child.tag == "a":
          authors.append(AuthorLink(
            name=dom_text(child),
            href=urljoin(href, child.get("href")),
          ))
        elif child.tag == "span":
          authors.append(AuthorLink(
            name=dom_text(child),
            href=None,
          ))

    abstract_dom = first_ele(root.xpath('//div[@class="brief"]//div[@class="abstract-text"]'))
    abstract: str = ""

    if abstract_dom is not None:
      abstract = dom_text(abstract_dom)

    keywords: list[str] = []

    for keyword_dom in root.xpath('//div[@class="brief"]//p[@class="keywords"]'):
      if keyword_dom.tag != "a":
        continue
      keywords.append(dom_text(keyword_dom).replace(";", ""))

    doi: str = None

    for row_dom in root.xpath('//span[@class="rowtit"]'):
      row_dom_text = dom_text(row_dom)
      if row_dom_text.startswith("DOI"):
        doi_dom = row_dom.getnext()
        if doi_dom.tag == "p":
          doi = dom_text(doi_dom)
          break

    pdf_href: str = None
    pdf_button_dom = first_ele(root.xpath('//div[@id="DownLoadParts"]//li[@class="btn-dlpdf"]//a'))

    if pdf_button_dom is not None:
      pdf_href = pdf_button_dom.get("href")

    html_href: str = None
    html_button_dom = first_ele(root.xpath('//div[@id="DownLoadParts"]//li[@class="btn-html"]//a'))

    if html_button_dom is not None:
      html_href = html_button_dom.get("href")

    return Article(
      title=title,
      authors=authors,
      abstract=abstract,
      keywords=keywords,
      doi=doi,
      pdf_href=pdf_href,
      html_href=html_href,
    )

  def download_pdf(self, pdf_href: str, from_url: str, pdf_file_path: str):
    self._limiter.limit()
    headers_content = {
      **headers(),
      "Referer": from_url,
    }
    with self._lock:
      response = self._session.get(pdf_href, stream=True, headers=headers_content)

    content_type = response.headers.get("Content-Type")
    chunk_size = 8192

    if "text/html" in content_type:
      raise AuthVerifyException("download PDF auth verify failed")

    with open(pdf_file_path, "wb") as file:
      for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
          file.write(chunk)
