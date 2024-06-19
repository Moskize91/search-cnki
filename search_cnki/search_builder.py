from typing import Self, Union

class SearchBuilder:

  def __init__(self):
    self._magazines_count: int = 0
    self._conditions_count: int = 0
    self._condition_type: Union[str, None] = None
    self._fields: dict[str, str] = {}

  def fields(self) -> dict[str, str]:
    fields = self._fields
    self.fields = {}
    return fields

  # 并且
  def with_and(self) -> Self:
    return self._condition_type("and")

  # 或者
  def with_or(self) -> Self:
    return self._condition_type("or")

  # 不含
  def with_not(self) -> Self:
    return self._condition_type("not")

  # 主题
  def subject(self, value: str) -> Self:
    return self._condition("SU$%=|", value)

  # 关键词
  def keyword(self, value: str) -> Self:
    return self._condition("KY", value)

  # 篇名
  def title(self, value: str) -> Self:
    return self._condition("TI", value)

  # 摘要
  def abstract(self, value: str) -> Self:
    return self._condition("AB", value)

  # 全文
  def full_text(self, value: str) -> Self:
    return self._condition("FT", value)

  # 被引文献
  def reference(self, value: str) -> Self:
    return self._condition("RF", value)

  # 期刊来源
  def magazine(self, value: str) -> Self:
    index = self._magazines_count + 1
    self._fields["magazine_value{index}"] = value
    self._fields[f"magazine_special{index}"] = "%"
    self._magazines_count += 1
    return self

  # 中图分类号
  def chinese_library_classification(self, value: str) -> Self:
    return self._condition("CLC$=|??", value)

  def _condition_type(self, type: str) -> Self:
    if self._conditions_count == 0:
      raise Exception("first condition cannot be with type")
    self._condition_type = type
    return self

  def _condition(self, sel: str, value: str) -> Self:
    condition_type = self._condition_type
    index = self._conditions_count + 1

    if condition_type is not None:
      self._fields[f"txt_{index}_logical"] = condition_type

    self._fields[f"txt_{index}_sel"] = sel
    self._fields[f"txt_{index}_value1"] = value
    self._fields[f"txt_{index}_relation"] = "#CNKI_AND"
    self._fields[f"txt_{index}_special1"] = "="
    self._condition_type = None
    self._conditions_count += 1

    return self


def build_search() -> SearchBuilder:
  return SearchBuilder()
