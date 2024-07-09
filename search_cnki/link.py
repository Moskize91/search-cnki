from dataclasses import dataclass
from typing import Optional

@dataclass
class AuthorLink:
  name: str
  href: str

@dataclass
class SourceLink:
  name: str
  href: str

@dataclass
class ArticleLink:
  title: str
  href: str
  published_at: str
  authors: list[AuthorLink]
  source: Optional[SourceLink]
