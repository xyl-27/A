from sqlalchemy import Column, Integer, String, Date, DateTime, DECIMAL, ForeignKey, Index
from sqlalchemy.sql import func
from utils.database import Base


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("industries.id"), index=True)
    weight = Column(DECIMAL(8, 4))
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_level_parent", "level", "parent_id"),
    )


class IndustryIndex(Base):
    __tablename__ = "industry_indices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_id = Column(Integer, nullable=False, index=True)
    trade_date = Column(Date, nullable=False, index=True)
    close_index = Column(DECIMAL(15, 2))
    change_rate = Column(DECIMAL(8, 4))
    volume = Column(Integer)
    amount = Column(DECIMAL(20, 2))
    pe_ratio = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_industry_date", "industry_id", "trade_date", unique=True),
    )
