import akshare as ak
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from utils.logger import logger


class AkShareService:
    def __init__(self):
        logger.info("AkShare service initialized")

    def get_realtime_quotes(self, codes: List[str]) -> List[Dict[str, Any]]:
        try:
            df = ak.stock_zh_a_spot_em()
            if df is None or df.empty:
                return []
            
            codes_set = set(codes)
            df = df[df['代码'].isin(codes_set)]
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": row['代码'],
                    "name": row['名称'],
                    "close_price": float(row['最新价']) if pd.notna(row['最新价']) else None,
                    "change_rate": float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                    "volume": int(row['成交量']) if pd.notna(row['成交量']) else None,
                    "amount": float(row['成交额']) if pd.notna(row['成交额']) else None,
                    "amplitude": float(row['振幅']) if pd.notna(row['振幅']) else None,
                    "high_price": float(row['最高']) if pd.notna(row['最高']) else None,
                    "low_price": float(row['最低']) if pd.notna(row['最低']) else None,
                    "open_price": float(row['今开']) if pd.notna(row['今开']) else None,
                    "prev_close": float(row['昨收']) if pd.notna(row['昨收']) else None,
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching realtime quotes: {e}")
            return []

    def get_stock_historical(self, code: str, period: str = "daily", adjust: str = "qfq") -> List[Dict[str, Any]]:
        try:
            symbol = f"{code}" if code.startswith('6') else f"{code}"
            df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date='20240101', adjust=adjust)
            
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row['日期'],
                    "open": float(row['开盘']) if pd.notna(row['开盘']) else None,
                    "close": float(row['收盘']) if pd.notna(row['收盘']) else None,
                    "high": float(row['最高']) if pd.notna(row['最高']) else None,
                    "low": float(row['最低']) if pd.notna(row['最低']) else None,
                    "volume": int(row['成交量']) if pd.notna(row['成交量']) else None,
                    "amount": float(row['成交额']) if pd.notna(row['成交额']) else None,
                    "change_rate": float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching historical data for {code}: {e}")
            return []

    def get_industry_list(self) -> List[Dict[str, Any]]:
        try:
            df = ak.stock_board_industry_name_em()
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": row['板块代码'],
                    "name": row['板块名称'],
                    "stock_count": int(row['股票家数']) if pd.notna(row['股票家数']) else 0,
                    "change_rate": float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                    "total_market_cap": float(row['总市值']) if pd.notna(row['总市值']) else None,
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching industry list: {e}")
            return []

    def get_industry_stocks(self, industry_code: str) -> List[Dict[str, Any]]:
        try:
            df = ak.stock_board_industry_cons_em(symbol=industry_code)
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": row['代码'],
                    "name": row['名称'],
                    "close_price": float(row['最新价']) if pd.notna(row['最新价']) else None,
                    "change_rate": float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                    "volume": int(row['成交量']) if pd.notna(row['成交量']) else None,
                    "amount": float(row['成交额']) if pd.notna(row['成交额']) else None,
                    "amplitude": float(row['振幅']) if pd.notna(row['振幅']) else None,
                    "turnover_rate": float(row['换手率']) if pd.notna(row['换手率']) else None,
                    "pe": float(row['市盈率']) if pd.notna(row['市盈率']) else None,
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching industry stocks for {industry_code}: {e}")
            return []

    def get_concept_list(self) -> List[Dict[str, Any]]:
        try:
            df = ak.stock_board_concept_name_em()
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": row['板块代码'],
                    "name": row['板块名称'],
                    "stock_count": int(row['股票家数']) if pd.notna(row['股票家数']) else 0,
                    "change_rate": float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching concept list: {e}")
            return []

    def get_concept_stocks(self, concept_code: str) -> List[Dict[str, Any]]:
        try:
            df = ak.stock_board_concept_cons_em(symbol=concept_code)
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": row['代码'],
                    "name": row['名称'],
                    "close_price": float(row['最新价']) if pd.notna(row['最新价']) else None,
                    "change_rate": float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching concept stocks for {concept_code}: {e}")
            return []

    def get_hs300_stocks(self) -> List[Dict[str, Any]]:
        try:
            df = ak.index_stock_cons_csindex(symbol="000300")
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": row['代码'],
                    "name": row['名称'],
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching HS300 stocks: {e}")
            return []

    def get_stock_info(self, code: str) -> Dict[str, Any]:
        try:
            df = ak.stock_individual_info_em(symbol=code)
            if df is None or df.empty:
                return {}
            
            info = {}
            for _, row in df.iterrows():
                info[row['item']] = row['value']
            
            return {
                "code": code,
                "name": info.get('股票简称'),
                "industry": info.get('所属行业'),
                "listing_date": info.get('上市时间'),
                "total_shares": info.get('总股本(万股)'),
                "float_shares": info.get('流通股本(万股)'),
                "market_cap": info.get('总市值(亿元)'),
                "pe": info.get('市盈率'),
                "pb": info.get('市净率'),
            }
        except Exception as e:
            logger.error(f"Error fetching stock info for {code}: {e}")
            return {}

    def get_fund_flow(self, code: str) -> Dict[str, Any]:
        try:
            df = ak.stock_individual_fund_flow(stock=code, market="sh" if code.startswith('6') else "sz")
            if df is None or df.empty:
                return {}
            
            return {
                "code": code,
                "main_fund_flow": float(df.iloc[0]['主力净流入-净额']) if '主力净流入-净额' in df.columns else None,
                "small_fund_flow": float(df.iloc[0]['小单净流入-净额']) if '小单净流入-净额' in df.columns else None,
                "net_flow": float(df.iloc[0]['净流入额']) if '净流入额' in df.columns else None,
            }
        except Exception as e:
            logger.error(f"Error fetching fund flow for {code}: {e}")
            return {}


ak_share_service = AkShareService()
