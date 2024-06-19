class Author:
  def __init__(
    self,
    name: str,
    href: str,
  ):
    self.name: str = name
    self.href: str = href

  def __str__(self) -> str:
    return f"<Author {self.name}>"

class Source:
  def __init__(self, name: str, href: str) -> None:
    self.name: str = name
    self.href: str = href

  def __str__(self) -> str:
    return f"<Source {self.name}>"

class Article:
  def __init__(
    self,
    title: str,
    href: str,
    published_at: str,
    authors: list[Author],
    source: Source,
  ):
    self.title: str = title
    self.href: str = href
    self.published_at: str = published_at
    self.authors: list[Author] = authors
    self.source: Source = source

  def __str__(self) -> str:
    return f"<Article {self.title}>"
