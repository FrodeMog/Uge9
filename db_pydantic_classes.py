from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime
from typing import Dict, Any


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class MfrEnum(str, Enum):
    A = 'A'
    G = 'G'
    K = 'K'
    N = 'N'
    P = 'P'
    Q = 'Q'
    R = 'R'

class TypeEnum(str, Enum):
    C = 'C'
    H = 'H'

class CerealBase(BaseModel):
    name: str
    mfr: MfrEnum
    type: TypeEnum
    calories: int
    protein: int
    fat: int
    sodium: int
    fiber: float
    carbo: float
    sugars: int
    potass: int
    vitamins: int
    shelf: int
    weight: float
    cups: float
    rating: float

    class Config:
        orm_mode = True

class CerealInDB(BaseModel):
    id: int
    name: str
    mfr: MfrEnum
    type: TypeEnum
    calories: int
    protein: int
    fat: int
    sodium: int
    fiber: float
    carbo: float
    sugars: int
    potass: int
    vitamins: int
    shelf: int
    weight: float
    cups: float
    rating: float

    class Config:
        orm_mode = True

class FilterExample(BaseModel):
    filters: Dict[str, Any] = Field(..., example={
        "calories": ["lt", 100],
        "sodium": ["lt", 200]
    })
    order: str = Field('asc', example='asc')

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, regex="^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

class UserAdmin(UserBase):
    username: str = Field(..., min_length=3, regex="^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str
    is_admin: Optional[str] = True

    class Config:
        orm_mode = True

class UserInDB(UserBase):
    id: int
    username: str
    email: EmailStr
    is_admin: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserResposne(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserAdminResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True