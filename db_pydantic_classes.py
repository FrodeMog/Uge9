from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime

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
    name: str = Field(..., max_length=50)
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

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, regex="^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str
    is_admin: Optional[bool] = False

class UserInDB(UserBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True