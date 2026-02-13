"""Wire transfer CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, WireStatus
from app.schemas import WireCreate, WireListResponse, WireResponse, WireUpdate
from app.services.auth_service import get_current_user
from app.services.wire_service import create_wire, get_wire_by_id, get_wires_paginated

router = APIRouter(prefix="/api/wires", tags=["Wires"])


@router.post("", response_model=WireResponse, status_code=status.HTTP_201_CREATED)
async def create_wire_endpoint(
    wire_data: WireCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new wire transfer."""
    wire = await create_wire(
        db=db,
        sender_name=wire_data.sender_name,
        recipient_name=wire_data.recipient_name,
        amount=float(wire_data.amount),
        currency=wire_data.currency,
        user=current_user,
    )

    return wire


@router.get("", response_model=WireListResponse)
async def list_wires(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List wire transfers with pagination."""
    wires, total = await get_wires_paginated(
        db=db,
        user=current_user,
        page=page,
        page_size=page_size,
        status=status,
    )

    return WireListResponse(
        wires=wires,
        total=total,
        page=page,
        page_size=page_size,
        cached=False,
    )


@router.get("/{wire_id}", response_model=WireResponse)
async def get_wire(
    wire_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single wire transfer by ID."""
    wire = await get_wire_by_id(db, wire_id, current_user)

    if not wire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wire with ID {wire_id} not found",
        )

    return wire


@router.put("/{wire_id}", response_model=WireResponse)
async def update_wire(
    wire_id: int,
    wire_data: WireUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a wire transfer."""
    wire = await get_wire_by_id(db, wire_id, current_user)

    if not wire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wire with ID {wire_id} not found",
        )

    # Update fields
    update_data = wire_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "status" and value:
            try:
                setattr(wire, key, WireStatus(value))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {value}",
                )
        else:
            setattr(wire, key, value)

    await db.commit()
    await db.refresh(wire)

    return wire


@router.delete("/{wire_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wire(
    wire_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a wire transfer."""
    wire = await get_wire_by_id(db, wire_id, current_user)

    if not wire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wire with ID {wire_id} not found",
        )

    await db.delete(wire)
    await db.commit()

    return None
