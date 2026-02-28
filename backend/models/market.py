from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, JSON, DECIMAL, Index
from sqlalchemy.sql import func
from utils.database import Base
import enum


class MarketType(str, enum.Enum):
    MAIN = "主板"
    CHINEXT = "创业板"
    STAR = "科创板"
    BEI = "北证"


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(50), nullable=False)
    industry_l1 = Column(String(50), index=True)
    industry_l2 = Column(String(50), index=True)
    market_type = Column(Enum(MarketType), index=True)
    listing_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_industry_l1_l2", "industry_l1", "industry_l2"),
    )


class StockQuote(Base):
    __tablename__ = "stock_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, nullable=False, index=True)
    trade_date = Column(Date, nullable=False, index=True)
    open_price = Column(DECIMAL(10, 2))
    close_price = Column(DECIMAL(10, 2))
    high_price = Column(DECIMAL(10, 2))
    low_price = Column(DECIMAL(10, 2))
    volume = Column(Integer)
    amount = Column(DECIMAL(15, 2))
    change_rate = Column(DECIMAL(8, 4), index=True)
    turnover_rate = Column(DECIMAL(8, 4))
    pe_ratio = Column(DECIMAL(10, 2))
    market_cap = Column(DECIMAL(20, 2))
    float_market_cap = Column(DECIMAL(20, 2))
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_stock_date", "stock_id", "trade_date", unique=True),
    )


class UserStock(Base):
    __tablename__ = "user_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    stock_id = Column(Integer, nullable=False)
    added_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_user_stock", "user_id", "stock_id", unique=True),
    )
