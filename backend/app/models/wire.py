"""Wire model for wire transfers."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
import enum
from app.database import Base


class WireStatus(enum.Enum):
    """Wire transfer status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Wire(Base):
    """Wire transfer model."""

    __tablename__ = "wires"

    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String(200), nullable=False)
    recipient_name = Column(String(200), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(Enum(WireStatus), default=WireStatus.PENDING, nullable=False)
    reference_number = Column(String(50), unique=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Wire(id={self.id}, ref={self.reference_number}, status={self.status.value})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "sender_name": self.sender_name,
            "recipient_name": self.recipient_name,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status.value,
            "reference_number": self.reference_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
