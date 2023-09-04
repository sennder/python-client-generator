from enum import Enum
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from fastapi import APIRouter, FastAPI, File, Header, Query, UploadFile
from pydantic import BaseModel
from pydantic.generics import GenericModel
from starlette.exceptions import HTTPException


router = APIRouter()

T_Results = TypeVar("T_Results")


class FooEnum(str, Enum):
    OPTION_1 = "option_1"
    OPTION_2 = "option_2"


class Bar(BaseModel):
    field_1: str
    field_2: Optional[bool]


class Foo(BaseModel):
    field_1: str
    field_2: int
    field_3: Optional[float]
    field_4: Optional[bool]
    field_5: str = "default"
    field_6: Optional[str] = "default"
    field_7: Optional[Bar]
    field_8: Optional[FooEnum]


class Paginated(GenericModel, Generic[T_Results]):
    results: List[T_Results]
    offset: int
    limit: int
    size: int


class Document(BaseModel):
    field_1: str


@router.get("/{foo_id}", response_model=Foo)
async def read_foo(foo_id: UUID) -> Foo:
    pass


@router.get("", response_model=Paginated[Foo])
async def list_foos(
    some_field: Optional[str] = Query(None, max_length=10, description="description"),
    show_deleted: bool = Query(False),
    offset: Optional[int] = Query(0, ge=0, description="Query result offset"),
    limit: Optional[int] = Query(10, le=100, description="Query result limit"),
) -> Paginated[Foo]:
    pass


@router.post("", response_model=Foo)
async def create_foo(
    foo_create: Foo,
    x_custom_header: str = Header(default="default_value"),
) -> Foo:
    # TODO: get this to show in the openapi.json file
    if foo_create.field_1 == "something":
        raise HTTPException(409, "some custom exception")
    return foo_create


@router.patch("/{foo_id}", response_model=Foo)
async def update_foo(foo_id: UUID) -> Foo:
    pass


@router.put("/{foo_id}", response_model=Foo)
async def put_foo(foo_id: UUID) -> Foo:
    pass


@router.delete("/{foo_id}", response_model=Foo)
async def delete_foo(foo_id: UUID) -> Foo:
    pass


@router.post("/{foo_id}/documents", response_model=Document)
async def upload_doc(foo_id: UUID, file: UploadFile = File(...)) -> Document:
    pass


app = FastAPI()
app.include_router(router, prefix="/api/foo")
