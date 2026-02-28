from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.database import get_db
from services.data_service import DataService

router = APIRouter(prefix="/market", tags=["market"])


class StockResponse(BaseModel):
    code: str
    name: str
    industry_l1: Optional[str]
    industry_l2: Optional[str]
    market_type: Optional[str]
    listing_date: Optional[str]


class StockListResponse(BaseModel):
    stocks: List[StockResponse]
    total: int
    page: int
    page_size: int


class QuoteResponse(BaseModel):
    code: str
    name: str
    close_price: Optional[float]
    change_rate: Optional[float]
    volume: Optional[int]
    amount: Optional[float]
    pe_ratio: Optional[float]
    market_cap: Optional[float]
    float_market_cap: Optional[float]


@router.get("/stocks", response_model=StockListResponse)
async def get_stocks(
    market_type: Optional[str] = Query(None, description="Market type: 主板/创业板/科创板/北证"),
    industry_l1: Optional[str] = Query(None, description="Primary industry"),
    industry_l2: Optional[str] = Query(None, description="Secondary industry"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    service = DataService(db)
    result = await service.get_stocks(
        market_type=market_type,
        industry_l1=industry_l1,
        industry_l2=industry_l2,
        page=page,
        page_size=page_size
    )
    return result


@router.get("/quotes", response_model=List[QuoteResponse])
async def get_quotes(
    codes: str = Query(..., description="Stock codes separated by comma"),
    db: Session = Depends(get_db)
):
    code_list = codes.split(",")
    service = DataService(db)
    result = await service.get_stock_quotes(code_list)
    return result
