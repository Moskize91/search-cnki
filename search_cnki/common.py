from lxml import etree

Referer = "https://kns.cnki.net/kns8s/defaultresult"

def first_ele(elements: list):
  for element in elements:
    return element
  return None

def dom_text(dome) -> str:
  return etree.tostring(dome, method="text", encoding="unicode").strip()

def check_is_verify_page(root) -> bool:
  title_dom = first_ele(root.xpath('//head//title'))
  if title_dom is None:
    return False
  if "超时验证" in dom_text(title_dom):
    return True
  return False
