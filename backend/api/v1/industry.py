from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.database import get_db
from services.data_service import DataService

router = APIRouter(prefix="/industry", tags=["industry"])


class IndustryNode(BaseModel):
    code: str
    name: str
    level: int
    children: Optional[List[Dict[str, Any]]] = None
    stocks: Optional[List[Dict[str, str]]] = None
    stats: Optional[Dict[str, Any]] = None


@router.get("/tree", response_model=List[Dict[str, Any]])
async def get_industry_tree(db: Session = Depends(get_db)):
    service = DataService(db)
    result = await service.get_industry_tree()
    return result


@router.get("/funds")
async def get_industry_funds(
    industry_code: str = Query(..., description="Industry code"),
    days: int = Query(5, ge=1, le=60),
    db: Session = Depends(get_db)
):
    return {
        "industry_code": industry_code,
        "days": days,
        "main_fund_flow": 100000000,
        "small_fund_flow": -50000000,
        "net_flow": 50000000,
        "trend": "inflow"
    }


@router.get("/stocks")
async def get_industry_stocks(
    industry_code: str = Query(..., description="Industry code"),
    level: int = Query(1, ge=1, le=2),
    db: Session = Depends(get_db)
):
    return {
        "industry_code": industry_code,
        "level": level,
        "stocks": [
            {"code": "000001", "name": "平安银行", "change_rate": 2.5},
            {"code": "600000", "name": "浦发银行", "change_rate": 1.8}
        ]
    }
