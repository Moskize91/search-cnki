import requests
from .query_builder import Query

class SearchResponse:
  def __init__(self, query: Query, session: requests.Session):
    self.query_json: dict = query.json()
    self._session: requests.Session = session
    self._request(0)

  def _request(self, cur_page: int):
    self._session.get("https://kns.cnki.net/")
    search_url = "https://kns.cnki.net/kns8s/brief/grid"
    post_data = {
      "boolSearch": True,
      "queryJson": self.query_json,
      "aside": "主题：国家",
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

class Session:
  def __init__(self) -> None:
    self._session = requests.Session()
    self._session.get("http://kns.cnki.net/kns/brief/result.aspx")

  def search(self, query: Query):
    return SearchResponse(query, self._session)
