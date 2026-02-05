"""Pydantic schemas for wire transfers."""
from datetime import datetime

from pydantic import BaseModel, Field, condecimal


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

    sender_name: str | None = Field(None, min_length=1, max_length=200)
    recipient_name: str | None = Field(None, min_length=1, max_length=200)
    amount: condecimal(max_digits=15, decimal_places=2, gt=0) | None = None  # type: ignore
    currency: str | None = Field(None, pattern="^[A-Z]{3}$")
    status: str | None = Field(None, pattern="^(pending|processing|completed|failed)$")


class WireResponse(WireBase):
    """Schema for wire transfer response."""

    id: int
    status: str
    reference_number: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class WireListResponse(BaseModel):
    """Schema for paginated wire list response."""

    wires: list[WireResponse]
    total: int
    page: int
    page_size: int
    cached: bool = False
