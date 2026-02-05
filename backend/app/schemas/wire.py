"""Pydantic schemas for wire transfers."""
from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from typing import Optional
from decimal import Decimal


class WireBase(BaseModel):
    """Base wire schema."""

    sender_name: str = Field(..., min_length=1, max_length=200)
    recipient_name: str = Field(..., min_length=1, max_length=200)
    amount: condecimal(max_digits=15, decimal_places=2, gt=0)  # type: ignore
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")


class WireCreate(WireBase):
    """Schema for creating a wire transfer."""

    pass


class WireUpdate(BaseModel):
    """Schema for updating a wire transfer."""

    sender_name: Optional[str] = Field(None, min_length=1, max_length=200)
    recipient_name: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[condecimal(max_digits=15, decimal_places=2, gt=0)] = None  # type: ignore
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")


class WireResponse(WireBase):
    """Schema for wire transfer response."""

    id: int
    status: str
    reference_number: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class WireListResponse(BaseModel):
    """Schema for paginated wire list response."""

    wires: list[WireResponse]
    total: int
    page: int
    page_size: int
    cached: bool = False
