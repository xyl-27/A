from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, Index, Text, DECIMAL
from sqlalchemy.sql import func
from utils.database import Base
import enum


class SentimentLabel(str, enum.Enum):
    BULL = "看涨"
    BEAR = "看跌"
    NEUTRAL = "中性"


class HotTopic(Base):
    __tablename__ = "hot_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source = Column(String(50), nullable=False, index=True)
    url = Column(String(500))
    sentiment_score = Column(DECIMAL(5, 4))
    sentiment_label = Column(Enum(SentimentLabel), index=True)
    heat = Column(Integer, default=0, index=True)
    stock_codes = Column(JSON)
    keywords = Column(JSON)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    __table_args__ = (
        Index("idx_created_source", "created_at", "source"),
    )
