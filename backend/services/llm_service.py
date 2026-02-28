from typing import Dict, Any, List, Optional
import json
import hashlib
from openai import OpenAI
from utils.config import settings
from utils.logger import logger


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        prompt = f"""
请对以下财经文本进行情感分析：

文本：{text}

请从以下方面分析：
1. 情感倾向：看涨/看跌/中性
2. 情感强度：-1到1之间的数值
3. 关键词提取：提取3-5个关键词
4. 简要总结：50字以内的总结

请以JSON格式返回结果：
{{
    "sentiment": "看涨|看跌|中性",
    "score": 0.8,
    "keywords": ["关键词1", "关键词2"],
    "summary": "总结内容"
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Sentiment analysis result: {result}")
            return result
        except Exception as e:
            logger.error(f"LLM sentiment analysis error: {e}")
            return {
                "sentiment": "中性",
                "score": 0.0,
                "keywords": [],
                "summary": "分析失败"
            }

    async def extract_keywords(self, texts: List[str]) -> List[str]:
        combined_text = "\n".join(texts[:20])
        
        prompt = f"""
请从以下财经文本中提取关键词：

文本：
{combined_text}

要求：
1. 提取10-20个关键词
2. 关键词应该是名词或名词短语
3. 按重要性排序
4. 返回JSON格式：{{"keywords": ["关键词1", "关键词2", ...]}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("keywords", [])
        except Exception as e:
            logger.error(f"LLM keyword extraction error: {e}")
            return []

    async def generate_industry_report(self, industry_name: str, data: Dict[str, Any]) -> str:
        prompt = f"""
请根据以下行业数据分析生成投资建议报告：

行业：{industry_name}

数据：
- 涨跌幅：{data.get('change_rate', 0)}%
- 成交额：{data.get('amount', 0)}万元
- 主力资金流向：{data.get('fund_flow', '未知')}
- 涨停家数：{data.get('up_count', 0)}
- 跌停家数：{data.get('down_count', 0)}

请生成一份简要的分析报告，包含：
1. 行业整体表现
2. 资金流向分析
3. 投资建议（仅供参考）
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM report generation error: {e}")
            return "生成报告失败，请稍后重试"
