from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8)
    is_master: bool = False


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=120)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None
    is_master: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    created_at: datetime
    is_active: bool
    is_master: bool
