from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/star-chart", tags=["star-chart"])


class StockPoint(BaseModel):
    code: str
    name: str
    change_rate: float
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    size: float
    color: str
    is_my_stock: bool = False


class StarChartSummary(BaseModel):
    total_count: int
    up_count: int
    down_count: int
    avg_change_rate: float


class StarChartResponse(BaseModel):
    stocks: List[StockPoint]
    summary: StarChartSummary


@router.get("/data", response_model=StarChartResponse)
async def get_star_chart_data(
    market_type: str = Query("沪深A股", description="Market type"),
    period: str = Query("5日", description="Period: 3日/5日/10日/20日/60日/年初至今"),
    size_metric: str = Query("市值", description="Size metric: 市值/成交额"),
    highlight_stocks: Optional[str] = Query(None, description="Comma-separated stock codes")
):
    highlight_list = highlight_stocks.split(",") if highlight_stocks else []
    
    mock_stocks = [
        {
            "code": "000001",
            "name": "平安银行",
            "change_rate": 2.5,
            "market_cap": 250000000000,
            "volume": 100000000,
            "size": 150,
            "color": "#ff0000",
            "is_my_stock": "000001" in highlight_list
        },
        {
            "code": "600000",
            "name": "浦发银行",
            "change_rate": 1.8,
            "market_cap": 180000000000,
            "volume": 80000000,
            "size": 120,
            "color": "#ff6600",
            "is_my_stock": "600000" in highlight_list
        },
        {
            "code": "000002",
            "name": "万科A",
            "change_rate": -1.2,
            "market_cap": 150000000000,
            "volume": 60000000,
            "size": 100,
            "color": "#00cc00",
            "is_my_stock": "000002" in highlight_list
        }
    ]
    
    return {
        "stocks": mock_stocks,
        "summary": {
            "total_count": 5000,
            "up_count": 2500,
            "down_count": 2400,
            "avg_change_rate": 0.5
        }
    }
