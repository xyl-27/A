from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.database import get_db
from services.akshare_service import ak_share_service

router = APIRouter(prefix="/industry", tags=["industry"])


class IndustryResponse(BaseModel):
    code: str
    name: str
    stock_count: Optional[int] = None
    change_rate: Optional[float] = None
    total_market_cap: Optional[float] = None


class StockResponse(BaseModel):
    code: str
    name: str
    close_price: Optional[float]
    change_rate: Optional[float]
    volume: Optional[int]
    amount: Optional[float]
    amplitude: Optional[float]
    turnover_rate: Optional[float]
    pe: Optional[float]


@router.get("/list", response_model=List[IndustryResponse])
async def get_industry_list():
    result = ak_share_service.get_industry_list()
    return result


@router.get("/stocks", response_model=List[StockResponse])
async def get_industry_stocks(
    industry_code: str = Query(..., description="Industry code"),
):
    result = ak_share_service.get_industry_stocks(industry_code)
    return result


@router.get("/concept/list")
async def get_concept_list():
    result = ak_share_service.get_concept_list()
    return result


@router.get("/concept/stocks")
async def get_concept_stocks(
    concept_code: str = Query(..., description="Concept code"),
):
    result = ak_share_service.get_concept_stocks(concept_code)
    return result


@router.get("/fund-flow")
async def get_fund_flow(
    code: str = Query(..., description="Stock code"),
):
    result = ak_share_service.get_fund_flow(code)
    return result
