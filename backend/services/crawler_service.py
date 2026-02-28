from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from utils.logger import logger


class CrawlerService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.request_delay = 2  # seconds between requests

    async def get_xueqiu_hot_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        posts = []
        try:
            url = f"https://xueqiu.com/v4/statuses/historical.data.json?since_id=0&max_id=0&count={limit}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get('list', []):
                            posts.append({
                                'title': item.get('title', ''),
                                'content': item.get('text', ''),
                                'source': '雪球',
                                'url': f"https://xueqiu.com/S/{item.get('symbol', '')}",
                                'user': item.get('user', {}).get('screen_name', ''),
                                'created_at': item.get('created_at'),
                                'reply_count': item.get('reply_count', 0),
                            })
                    else:
                        logger.warning(f"Xueqiu request failed with status {response.status}")
            
            await asyncio.sleep(self.request_delay)
            
        except Exception as e:
            logger.error(f"Xueqiu crawler error: {e}")
        
        return posts[:limit]

    async def get_eastmoney_guba_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        posts = []
        try:
            url = "http://guba.eastmoney.com/list,zxrl_hots.html"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for item in soup.select('.articleh')[:limit]:
                            title_elem = item.select_one('.title a')
                            if title_elem:
                                posts.append({
                                    'title': title_elem.get_text(strip=True),
                                    'content': '',
                                    'source': '东方财富股吧',
                                    'url': f"http://guba.eastmoney.com{title_elem.get('href', '')}",
                                    'reply_count': 0,
                                })
                    else:
                        logger.warning(f"Eastmoney request failed with status {response.status}")
            
            await asyncio.sleep(self.request_delay)
            
        except Exception as e:
            logger.error(f"Eastmoney crawler error: {e}")
        
        return posts[:limit]

    async def get_all_hot_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        tasks = [
            self.get_xueqiu_hot_posts(limit // 2),
            self.get_eastmoney_guba_posts(limit // 2)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_posts = []
        for result in results:
            if isinstance(result, list):
                all_posts.extend(result)
        
        all_posts.sort(key=lambda x: x.get('reply_count', 0), reverse=True)
        
        return all_posts[:limit]
