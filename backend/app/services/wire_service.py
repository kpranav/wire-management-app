"""Wire service for business logic."""
import secrets
import string

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Wire, WireStatus


def generate_reference_number(length: int = 12) -> str:
    """Generate a unique wire reference number."""
    chars = string.ascii_uppercase + string.digits
    return "WIRE-" + "".join(secrets.choice(chars) for _ in range(length))


async def create_wire(
    db: AsyncSession,
    sender_name: str,
    recipient_name: str,
    amount: float,
    currency: str,
    user: User,
) -> Wire:
    """Create a new wire transfer."""
    # Generate unique reference number
    reference_number = generate_reference_number()

    # Ensure reference number is unique
    while True:
        result = await db.execute(
            select(Wire).where(Wire.reference_number == reference_number)
        )
        existing = result.scalar_one_or_none()
        if not existing:
            break
        reference_number = generate_reference_number()

    # Create wire
    wire = Wire(
        sender_name=sender_name,
        recipient_name=recipient_name,
        amount=amount,
        currency=currency,
        reference_number=reference_number,
        created_by=user.id,
        status=WireStatus.PENDING,
    )

    db.add(wire)
    await db.commit()
    await db.refresh(wire)

    return wire


async def get_wire_by_id(db: AsyncSession, wire_id: int, user: User) -> Wire | None:
    """Get a wire by ID for the current user."""
    result = await db.execute(
        select(Wire).where(Wire.id == wire_id, Wire.created_by == user.id)
    )
    return result.scalar_one_or_none()


async def get_wires_paginated(
    db: AsyncSession,
    user: User,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
) -> tuple[list[Wire], int]:
    """Get paginated wires for the current user."""
    query = select(Wire).where(Wire.created_by == user.id)

    # Filter by status if provided
    if status:
        try:
            wire_status = WireStatus(status)
            query = query.where(Wire.status == wire_status)
        except ValueError:
            pass  # Invalid status, ignore filter

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(Wire.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    wires = result.scalars().all()

    return list(wires), total
