from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID


try:
  from pydantic.v1 import BaseModel, Field
except ImportError:
  from pydantic import BaseModel, Field


class FooEnum(str, Enum):
    OPTION_1 = "option_1"
    OPTION_2 = "option_2"


class Bar(BaseModel):
    field_1: str
    field_2: Optional[bool]


class Document(BaseModel):
    field_1: str


class Foo(BaseModel):
    field_1: str
    field_2: int
    field_3: Optional[float]
    field_4: Optional[bool]
    field_5: Optional[str] = Field(default="default")
    field_6: Optional[str] = Field(default="default")
    field_7: Optional[Bar]
    field_8: Optional[str]


class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]]


class PaginatedFoo(BaseModel):
    results: List[Foo]
    offset: int
    limit: int
    size: int


