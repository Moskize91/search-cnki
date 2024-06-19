import json
from typing import Self

class Query:
  def __init__(self):
    self._next_logic: int = 0
    self._query_group: dict[dict] = []

  def with_and(self) -> Self:
    self._next_logic = 0
    return self

  def with_or(self) -> Self:
    self._next_logic = 1
    return self

  def with_not(self) -> Self:
    self._next_logic = 2
    return self

  def subject(self, value: str) -> Self:
    return self._add_condition("主题", "SU", "TOPRANK", value)

  def author(self, value: str) -> Self:
    return self._add_condition("作者", "AU", "DEFAULT", value)

  def json(self) -> str:
    return json.dumps({
      "Platform": "CJFQ",
      "Resource": "JOURNAL",
      "Classid": "YSTT4HG0",
      "Products": "",
      "QNode": {
        "QGroup": [
          {
            "Key": "Subject",
            "Title": "",
            "Logic": 0,
            "Items": [],
            "ChildItems": self._query_group
          },
          {
            "Key": "ControlGroup",
            "Title": "",
            "Logic": 0,
            "Items": [],
            "ChildItems": []
          }
        ]
      },
      "ExScope": "1",
      "SearchType": 1,
      "Rlang": "CHINESE",
      "KuaKuCode": "",
      "View": "changeDBOnlyFT"
    })

  def _add_condition(self, title: str, field: str, operator: str, value: str):
    index = len(self._query_group) + 1
    self._query_group.append({
      "Key": f"input[data-tipid=gradetxt-{index}]",
      "Title": title,
      "Logic": self._next_logic,
      "Items": [
        {
          "Key": "input[data-tipid=gradetxt-{tipid}]",
          "Title": title,
          "Logic": 0,
          "Field": field,
          "Operator": operator,
          "Value": value,
          "Value2": ""
        }
      ],
      "ChildItems": [],
    })
    self._next_logic = 0
    return self
