"""Pydantic schemas used for request validation and response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CityUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)


class CityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
