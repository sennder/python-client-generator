from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID


try:
  from pydantic.v1 import BaseModel, Field
except ImportError:
  from pydantic import BaseModel, Field


class Order(BaseModel):
    id: Optional[int]
    petId: Optional[int]
    quantity: Optional[int]
    shipDate: Optional[datetime]
    status: Optional[str]
    complete: Optional[bool]


class Address(BaseModel):
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]


class Customer(BaseModel):
    id: Optional[int]
    username: Optional[str]
    address: Optional[List[Address]]


class Category(BaseModel):
    id: Optional[int]
    name: Optional[str]


class User(BaseModel):
    id: Optional[int]
    username: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[str]
    password: Optional[str]
    phone: Optional[str]
    userStatus: Optional[int]


class Tag(BaseModel):
    id: Optional[int]
    name: Optional[str]


class Pet(BaseModel):
    id: Optional[int]
    name: str
    category: Optional[Category]
    photoUrls: List[str]
    tags: Optional[List[Tag]]
    status: Optional[str]


class ApiResponse(BaseModel):
    code: Optional[int]
    type: Optional[str]
    message: Optional[str]


