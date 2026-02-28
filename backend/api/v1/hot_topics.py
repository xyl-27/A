from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.database import get_db
from services.crawler_service import CrawlerService
from services.llm_service import LLMService

router = APIRouter(prefix="/hot-topics", tags=["hot-topics"])


class HotTopicResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    source: str
    url: Optional[str]
    sentiment_label: Optional[str]
    sentiment_score: Optional[float]
    keywords: Optional[List[str]]
    heat: int


class SentimentAnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "sentiment"


class SentimentAnalysisResponse(BaseModel):
    sentiment: str
    score: float
    keywords: List[str]
    summary: str


@router.get("/list", response_model=List[HotTopicResponse])
async def get_hot_topics(
    limit: int = Query(30, ge=1, le=100),
    sentiment: Optional[str] = Query(None, description="Sentiment: 看涨/看跌/中性"),
    source: Optional[str] = Query(None, description="Source: 雪球/股吧")
):
    mock_topics = [
        {
            "id": 1,
            "title": "人工智能板块持续爆发，多家公司发布新产品",
            "content": "近日，多家人工智能相关公司发布新产品...",
            "source": "雪球",
            "url": "https://xueqiu.com/S/AI",
            "sentiment_label": "看涨",
            "sentiment_score": 0.8,
            "keywords": ["人工智能", "新产品", "爆发"],
            "heat": 15000
        },
        {
            "id": 2,
            "title": "新能源车销量不及预期，板块集体回调",
            "content": "最新数据显示...",
            "source": "东方财富股吧",
            "url": "https://guba.eastmoney.com",
            "sentiment_label": "看跌",
            "sentiment_score": -0.6,
            "keywords": ["新能源车", "销量", "回调"],
            "heat": 12000
        }
    ]
    
    return mock_topics[:limit]


@router.post("/analyze", response_model=SentimentAnalysisResponse)
async def analyze_content(request: SentimentAnalysisRequest):
    llm_service = LLMService()
    
    if request.analysis_type == "sentiment":
        result = await llm_service.analyze_sentiment(request.content)
        return result
    
    return {
        "sentiment": "中性",
        "score": 0.0,
        "keywords": [],
        "summary": "分析失败"
    }


@router.post("/refresh")
async def refresh_hot_topics(db: Session = Depends(get_db)):
    crawler = CrawlerService()
    posts = await crawler.get_all_hot_posts(limit=50)
    
    return {
        "message": "Hot topics refreshed",
        "count": len(posts)
    }
