from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.market import Stock, StockQuote, MarketType
from models.industry import Industry, IndustryIndex
from datetime import datetime, timedelta
from utils.logger import logger


class DataService:
    def __init__(self, db: Session):
        self.db = db

    async def get_stocks(
        self,
        market_type: Optional[str] = None,
        industry_l1: Optional[str] = None,
        industry_l2: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        query = select(Stock)
        
        if market_type:
            query = query.where(Stock.market_type == MarketType(market_type))
        if industry_l1:
            query = query.where(Stock.industry_l1 == industry_l1)
        if industry_l2:
            query = query.where(Stock.industry_l2 == industry_l2)
        
        total_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(total_query)
        total_count = total.scalar()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        stocks = result.scalars().all()
        
        return {
            "stocks": [self._stock_to_dict(s) for s in stocks],
            "total": total_count,
            "page": page,
            "page_size": page_size
        }

    def _stock_to_dict(self, stock: Stock) -> Dict[str, Any]:
        return {
            "code": stock.code,
            "name": stock.name,
            "industry_l1": stock.industry_l1,
            "industry_l2": stock.industry_l2,
            "market_type": stock.market_type.value if stock.market_type else None,
            "listing_date": stock.listing_date.isoformat() if stock.listing_date else None
        }

    async def get_stock_quotes(self, codes: List[str], trade_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        if not trade_date:
            trade_date = datetime.now()
        
        date = trade_date.date()
        
        query = select(Stock, StockQuote).join(
            StockQuote, Stock.id == StockQuote.stock_id
        ).where(
            Stock.code.in_(codes),
            StockQuote.trade_date == date
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "code": stock.code,
                "name": stock.name,
                "close_price": float(quote.close_price) if quote.close_price else None,
                "change_rate": float(quote.change_rate) if quote.change_rate else None,
                "volume": quote.volume,
                "amount": float(quote.amount) if quote.amount else None,
                "pe_ratio": float(quote.pe_ratio) if quote.pe_ratio else None,
                "market_cap": float(quote.market_cap) if quote.market_cap else None,
                "float_market_cap": float(quote.float_market_cap) if quote.float_market_cap else None,
            }
            for stock, quote in rows
        ]

    async def get_industry_tree(self) -> List[Dict[str, Any]]:
        query = select(Industry).where(Industry.level == 1).order_by(Industry.code)
        result = await self.db.execute(query)
        industries = result.scalars().all()
        
        tree = []
        for ind in industries:
            children_query = select(Industry).where(
                Industry.parent_id == ind.id
            ).order_by(Industry.code)
            children_result = await self.db.execute(children_query)
            children = children_result.scalars().all()
            
            tree.append({
                "code": ind.code,
                "name": ind.name,
                "level": ind.level,
                "children": [
                    {
                        "code": c.code,
                        "name": c.name,
                        "level": c.level
                    }
                    for c in children
                ]
            })
        
        return tree
