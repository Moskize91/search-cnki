class AuthorLink:
  def __init__(
    self,
    name: str,
    href: str,
  ):
    self.name: str = name
    self.href: str = href

  def __str__(self) -> str:
    return f"<Author {self.name}>"

class SourceLink:
  def __init__(self, name: str, href: str) -> None:
    self.name: str = name
    self.href: str = href

  def __str__(self) -> str:
    return f"<Source {self.name}>"

class ArticleLink:
  def __init__(
    self,
    title: str,
    href: str,
    published_at: str,
    authors: list[AuthorLink],
    source: SourceLink,
  ):
    self.title: str = title
    self.href: str = href
    self.published_at: str = published_at
    self.authors: list[AuthorLink] = authors
    self.source: SourceLink = source

  def __str__(self) -> str:
    return f"<Article {self.title}>"
