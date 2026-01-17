from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, date
import uuid


class New(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    original_title: str
    url: str
    category: str
    ai_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Subscriber(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    is_active: bool = True
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class MarketSnapshot(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    snapshot_date: date = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MarketItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    snapshot_id: uuid.UUID = Field(foreign_key="marketsnapshot.id")

    type: str  # "stock" | "crypto"
    symbol: str
    price: Optional[float]
    market_cap: Optional[float]
    change_24h: Optional[float]
    image: Optional[str]

    created_at: datetime = Field(default_factory=datetime.utcnow)
