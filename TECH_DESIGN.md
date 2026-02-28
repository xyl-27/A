# A股智能选股分析平台 技术设计文档

## 1. 系统架构设计

### 1.1 整体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端层        │    │   服务层        │    │   数据层        │
│                 │    │                 │    │                 │
│ • React SPA     │◄──►│ • FastAPI       │◄──►│ • MySQL         │
│ • ECharts       │    │ • 数据服务      │    │ • Redis         │
│ • Ant Design    │    │ • LLM服务       │    │ • Tushare/AkShare│
│ • WebSocket     │    │ • 爬虫服务      │    │ • 本地缓存      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 技术栈选型

| 层次 | 技术选型                  | 说明 |
|------|-----------------------|------|
| **前端** | React 18 + TypeScript | 现代化前端框架，类型安全 |
| | ECharts 5             | 专业的数据可视化库 |
| | Ant Design 5          | UI组件库，快速构建界面 |
| | Axios                 | HTTP请求库 |
| | React Router 6        | 路由管理 |
| **后端** | Python 3.10+          | 主要开发语言 |
| | FastAPI               | 高性能Web框架，自动生成API文档 |
| | SQLAlchemy            | ORM框架 |
| | Pydantic              | 数据验证和序列化 |
| **数据库** | MySQL 8.0             | 主数据存储 |
| | Redis 7.0             | 缓存和会话存储 |
| **LLM** | 智谱(GLM4.6)            | 主要LLM服务 |
| | 通义千问 (Qwen)           | 备选方案 |
| | deepseek              | 备选方案 |
| **数据源** | Tushare Pro           | 专业股票数据接口 |
| | AkShare               | 开源金融数据接口 |
| | 自建爬虫                  | 财经社区数据 |
| **部署** | Docker                | 容器化部署 |
| | Nginx                 | 反向代理 |
| | PM2                   | 进程管理 |

### 1.3 模块划分

```
后端模块:
├── api/           # API接口层
│   ├── v1/        # API版本1
│   │   ├── market.py      # 市场数据接口
│   │   ├── industry.py    # 行业分析接口
│   │   ├── star_chart.py  # 大盘星图接口
│   │   └── hot_topics.py  # 热点分析接口
│   └── __init__.py
├── services/      # 业务逻辑层
│   ├── data_service.py    # 数据服务
│   ├── llm_service.py     # LLM服务
│   ├── crawler_service.py # 爬虫服务
│   └── cache_service.py   # 缓存服务
├── models/        # 数据模型
│   ├── market.py  # 市场数据模型
│   ├── industry.py # 行业数据模型
│   └── hot_topic.py # 热点话题模型
├── utils/         # 工具类
│   ├── database.py # 数据库连接
│   ├── config.py   # 配置管理
│   └── logger.py   # 日志工具
└── main.py        # 应用入口

前端模块:
├── src/
│   ├── components/    # 通用组件
│   │   ├── Chart/     # 图表组件
│   │   ├── IndustryTree/ # 行业树组件
│   │   └── StarChart/    # 星图组件
│   ├── pages/         # 页面组件
│   │   ├── Home/      # 首页
│   │   ├── Industry/  # 行业分析页
│   │   ├── StarChart/ # 大盘星图页
│   │   └── HotTopics/ # 热点分析页
│   ├── services/      # API服务
│   ├── store/         # 状态管理
│   └── utils/         # 工具函数
└── public/            # 静态资源
```

## 2. 数据库设计

### 2.1 核心表结构

#### 股票基础信息表 (stocks)
```sql
CREATE TABLE stocks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    name VARCHAR(50) NOT NULL COMMENT '股票名称',
    industry_l1 VARCHAR(50) COMMENT '一级行业',
    industry_l2 VARCHAR(50) COMMENT '二级行业',
    market_type ENUM('主板', '创业板', '科创板', '北证') COMMENT '市场类型',
    listing_date DATE COMMENT '上市日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code (code),
    INDEX idx_industry_l1 (industry_l1),
    INDEX idx_industry_l2 (industry_l2),
    INDEX idx_market_type (market_type)
);
```

#### 股票行情数据表 (stock_quotes)
```sql
CREATE TABLE stock_quotes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL COMMENT '股票ID',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open_price DECIMAL(10,2) COMMENT '开盘价',
    close_price DECIMAL(10,2) COMMENT '收盘价',
    high_price DECIMAL(10,2) COMMENT '最高价',
    low_price DECIMAL(10,2) COMMENT '最低价',
    volume BIGINT COMMENT '成交量',
    amount DECIMAL(15,2) COMMENT '成交额',
    change_rate DECIMAL(8,4) COMMENT '涨跌幅',
    turnover_rate DECIMAL(8,4) COMMENT '换手率',
    pe_ratio DECIMAL(10,2) COMMENT '市盈率',
    market_cap DECIMAL(20,2) COMMENT '总市值',
    float_market_cap DECIMAL(20,2) COMMENT '流通市值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE KEY uk_stock_date (stock_id, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_change_rate (change_rate),
    INDEX idx_volume (volume)
);
```

#### 行业数据表 (industries)
```sql
CREATE TABLE industries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) NOT NULL COMMENT '行业代码',
    name VARCHAR(100) NOT NULL COMMENT '行业名称',
    level INT NOT NULL COMMENT '行业层级(1:一级,2:二级)',
    parent_id INT COMMENT '父级行业ID',
    weight DECIMAL(8,4) COMMENT '行业权重',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES industries(id),
    UNIQUE KEY uk_code (code),
    INDEX idx_level (level),
    INDEX idx_parent_id (parent_id)
);
```

#### 行业指数表 (industry_indices)
```sql
CREATE TABLE industry_indices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    industry_id INT NOT NULL COMMENT '行业ID',
    trade_date DATE NOT NULL COMMENT '交易日期',
    close_index DECIMAL(15,2) COMMENT '收盘指数',
    change_rate DECIMAL(8,4) COMMENT '涨跌幅',
    volume BIGINT COMMENT '成交量',
    amount DECIMAL(20,2) COMMENT '成交额',
    pe_ratio DECIMAL(10,2) COMMENT '市盈率',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (industry_id) REFERENCES industries(id),
    UNIQUE KEY uk_industry_date (industry_id, trade_date),
    INDEX idx_trade_date (trade_date)
);
```

#### 热点话题表 (hot_topics)
```sql
CREATE TABLE hot_topics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(500) NOT NULL COMMENT '话题标题',
    content TEXT COMMENT '话题内容',
    source VARCHAR(50) NOT NULL COMMENT '数据来源(雪球/股吧)',
    url VARCHAR(500) COMMENT '原始链接',
    sentiment_score DECIMAL(5,4) COMMENT '情感得分(-1到1)',
    sentiment_label ENUM('看涨', '看跌', '中性') COMMENT '情感标签',
   热度 INT DEFAULT 0 COMMENT '热度值',
    stock_codes JSON COMMENT '涉及股票代码数组',
    keywords JSON COMMENT '关键词数组',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_source (source),
    INDEX idx_sentiment (sentiment_label)
);
```

#### 用户自选股表 (user_stocks)
```sql
CREATE TABLE user_stocks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    stock_id INT NOT NULL COMMENT '股票ID',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE KEY uk_user_stock (user_id, stock_id),
    INDEX idx_user_id (user_id)
);
```

### 2.2 缓存策略

#### Redis缓存设计
```bash
# 股票实时行情缓存 (TTL: 5分钟)
key: stock:quote:{stock_code}
value: JSON格式的股票行情数据

# 行业数据缓存 (TTL: 10分钟)
key: industry:data:{industry_code}
value: JSON格式的行业数据

# 热点话题缓存 (TTL: 30分钟)
key: hot:topics
value: JSON格式的热点话题列表

# 大盘星图数据缓存 (TTL: 2分钟)
key: star:chart:{market_type}:{period}
value: JSON格式的星图数据

# LLM分析结果缓存 (TTL: 1小时)
key: llm:analysis:{content_hash}
value: JSON格式的分析结果
```

## 3. API接口设计

### 3.1 市场数据接口

#### 获取股票列表
```http
GET /api/v1/market/stocks
```

**请求参数:**
```json
{
    "market_type": "主板|创业板|科创板|北证",  // 可选
    "industry_l1": "金融",                      // 可选
    "industry_l2": "银行",                      // 可选
    "page": 1,                                 // 可选
    "page_size": 100                           // 可选
}
```

**响应格式:**
```json
{
    "code": 200,
    "data": {
        "stocks": [
            {
                "code": "000001",
                "name": "平安银行",
                "industry_l1": "金融",
                "industry_l2": "银行",
                "market_type": "主板",
                "quote": {
                    "close_price": 12.34,
                    "change_rate": 2.5,
                    "volume": 1000000,
                    "amount": 12340000,
                    "pe_ratio": 8.5,
                    "market_cap": 250000000000
                }
            }
        ],
        "total": 1000,
        "page": 1,
        "page_size": 100
    }
}
```

#### 获取实时行情
```http
GET /api/v1/market/quotes
```

**请求参数:**
```json
{
    "codes": ["000001", "000002", "600000"],  // 股票代码列表
    "fields": ["close_price", "change_rate", "volume"]  // 需要的字段
}
```

### 3.2 行业分析接口

#### 获取行业树结构
```http
GET /api/v1/industry/tree
```

**响应格式:**
```json
{
    "code": 200,
    "data": [
        {
            "code": "金融",
            "name": "金融",
            "level": 1,
            "children": [
                {
                    "code": "银行",
                    "name": "银行",
                    "level": 2,
                    "stocks": [
                        {"code": "000001", "name": "平安银行"},
                        {"code": "600000", "name": "浦发银行"}
                    ],
                    "stats": {
                        "avg_change_rate": 1.5,
                        "total_volume": 50000000,
                        "up_count": 15,
                        "down_count": 5
                    }
                }
            ]
        }
    ]
}
```

#### 获取行业资金流向
```http
GET /api/v1/industry/funds
```

**请求参数:**
```json
{
    "industry_code": "银行",
    "days": 5  // 时间周期
}
```

### 3.3 大盘星图接口

#### 获取星图数据
```http
GET /api/v1/star-chart/data
```

**请求参数:**
```json
{
    "market_type": "沪深A股",
    "period": "5日",  // 3日/5日/10日/20日/60日/年初至今
    "size_metric": "市值",  // 市值/成交额
    "highlight_stocks": ["000001", "600000"]  // 高亮股票
}
```

**响应格式:**
```json
{
    "code": 200,
    "data": {
        "stocks": [
            {
                "code": "000001",
                "name": "平安银行",
                "change_rate": 2.5,
                "market_cap": 250000000000,
                "volume": 1000000,
                "size": 150,  // 气泡大小
                "color": "#ff0000",  // 气泡颜色
                "is_my_stock": true
            }
        ],
        "summary": {
            "total_count": 5000,
            "up_count": 2500,
            "down_count": 2400,
            "avg_change_rate": 0.5
        }
    }
}
```

### 3.4 热点分析接口

#### 获取热点话题
```http
GET /api/v1/hot-topics/list
```

**请求参数:**
```json
{
    "limit": 30,
    "sentiment": "看涨",  // 可选：看涨/看跌/中性
    "source": "雪球"      // 可选：雪球/股吧
}
```

#### LLM分析热点
```http
POST /api/v1/hot-topics/analyze
```

**请求参数:**
```json
{
    "content": "最近人工智能板块表现强势，多家公司发布相关产品...",
    "analysis_type": "sentiment"  // sentiment: 情感分析, keywords: 关键词提取
}
```

**响应格式:**
```json
{
    "code": 200,
    "data": {
        "sentiment_score": 0.8,
        "sentiment_label": "看涨",
        "keywords": ["人工智能", "板块", "产品", "强势"],
        "summary": "该内容整体呈现积极情绪，主要讨论人工智能板块的强势表现..."
    }
}
```

## 4. 前端架构设计

### 4.1 组件架构

```
App
├── Layout
│   ├── Header (导航栏)
│   ├── Sidebar (侧边栏)
│   └── Content (内容区域)
├── Pages
│   ├── Home
│   │   ├── MarketOverview (市场概览)
│   │   ├── QuickStats (快速统计)
│   │   └── HotNews (热点新闻)
│   ├── IndustryAnalysis
│   │   ├── IndustryTree (行业树)
│   │   ├── IndustryChart (行业图表)
│   │   └── StockList (股票列表)
│   ├── StarChart
│   │   ├── ChartControls (图表控制)
│   │   ├── BubbleChart (气泡图)
│   │   └── Tooltip (提示信息)
│   └── HotTopics
│       ├── TopicList (话题列表)
│       ├── WordCloud (词云图)
│       └── SentimentChart (情感分析图)
└── Components
    ├── Chart (图表组件)
    ├── Loading (加载组件)
    └── ErrorBoundary (错误边界)
```

### 4.2 状态管理

使用 Zustand 进行状态管理：

```typescript
// store/useMarketStore.ts
interface MarketState {
    stocks: Stock[];
    loading: boolean;
    error: string | null;
    fetchStocks: (params: StockParams) => Promise<void>;
}

export const useMarketStore = create<MarketState>((set) => ({
    stocks: [],
    loading: false,
    error: null,
    fetchStocks: async (params) => {
        set({ loading: true });
        try {
            const data = await marketService.getStocks(params);
            set({ stocks: data, loading: false });
        } catch (error) {
            set({ error: error.message, loading: false });
        }
    }
}));
```

### 4.3 路由设计

```typescript
// router/index.ts
const routes = [
    {
        path: '/',
        element: <Layout />,
        children: [
            { path: '', element: <Home /> },
            { path: 'industry', element: <IndustryAnalysis /> },
            { path: 'star-chart', element: <StarChart /> },
            { path: 'hot-topics', element: <HotTopics /> }
        ]
    }
];
```

### 4.4 图表组件设计

#### 大盘星图组件
```typescript
interface StarChartProps {
    marketType: MarketType;
    period: Period;
    sizeMetric: 'market_cap' | 'volume';
    highlightStocks?: string[];
}

const StarChart: React.FC<StarChartProps> = ({
    marketType,
    period,
    sizeMetric,
    highlightStocks
}) => {
    const { data, loading } = useStarChart(marketType, period, sizeMetric);
    
    return (
        <div className="star-chart">
            <ChartControls />
            <BubbleChart
                data={data.stocks}
                sizeMetric={sizeMetric}
                highlightStocks={highlightStocks}
            />
            <ChartLegend />
        </div>
    );
};
```

## 5. 数据采集与处理

### 5.1 股票数据采集

#### Tushare数据获取
```python
# services/data_service.py
import tushare as ts

class DataService:
    def __init__(self):
        self.pro = ts.pro_api('your_token')
    
    def get_stock_basic(self):
        """获取股票基础信息"""
        df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        return df.to_dict('records')
    
    def get_daily_data(self, trade_date):
        """获取日线数据"""
        df = self.pro.daily(trade_date=trade_date)
        return df.to_dict('records')
    
    def get_industry_classify(self):
        """获取行业分类"""
        df = self.pro.ths_classify(level='2', exchange='A')
        return df.to_dict('records')
```

#### AkShare数据获取
```python
import akshare as ak

class AkShareService:
    def get_stock_info(self):
        """获取股票信息"""
        df = ak.stock_zh_a_spot_em()
        return df.to_dict('records')
    
    def get_industry_data(self):
        """获取行业数据"""
        df = ak.stock_board_industry_name_em()
        return df.to_dict('records')
```

### 5.2 财经社区爬虫

#### 雪球热门帖子爬虫
```python
# services/crawler_service.py
import requests
from bs4 import BeautifulSoup
import time

class XueqiuCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_hot_posts(self, limit=100):
        """获取热门帖子"""
        url = f"https://xueqiu.com/v4/statuses/hot_timeline.json?since_id=0&count={limit}"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        
        posts = []
        for item in data.get('list', []):
            posts.append({
                'title': item.get('title'),
                'content': item.get('description'),
                'source': '雪球',
                'url': f"https://xueqiu.com/{item.get('id')}",
                'created_at': item.get('created_at')
            })
        
        return posts
```

#### 东方财富股吧爬虫
```python
class EastMoneyCrawler:
    def get_guba_hot_posts(self, limit=100):
        """获取股吧热门帖子"""
        url = f"http://guba.eastmoney.com/list,zxrl_hots.html"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        posts = []
        for item in soup.select('.articleh'):
            title = item.select_one('.title a').text
            content = item.select_one('.content').text if item.select_one('.content') else ''
            posts.append({
                'title': title,
                'content': content,
                'source': '东方财富股吧',
                'url': item.select_one('.title a')['href']
            })
        
        return posts[:limit]
```

### 5.3 LLM分析服务

#### 情感分析
```python
# services/llm_service.py
import openai
import json

class LLMService:
    def __init__(self, api_key, base_url=None):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    def analyze_sentiment(self, text):
        """情感分析"""
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
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
```

#### 关键词提取
```python
    def extract_keywords(self, text):
        """关键词提取"""
        prompt = f"""
        请从以下财经文本中提取关键词：
        
        文本：{text}
        
        要求：
        1. 提取3-8个关键词
        2. 关键词应该是名词或名词短语
        3. 按重要性排序
        4. 返回JSON格式：
        {{"keywords": ["关键词1", "关键词2", ...]}}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
```

## 6. 性能优化策略

### 6.1 前端性能优化

#### 虚拟化长列表
```typescript
// 使用 react-virtualized 优化长列表
import { FixedSizeList as List } from 'react-virtualized';

const VirtualizedStockList = ({ stocks }) => (
    <List
        height={600}
        itemCount={stocks.length}
        itemSize={50}
        itemData={stocks}
    >
        {({ index, style, data }) => (
            <div style={style}>
                <StockItem stock={data[index]} />
            </div>
        )}
    </List>
);
```

#### 图表性能优化
```typescript
// 使用 ECharts 的大数据优化
const chartOptions = {
    series: [{
        type: 'scatter',
        large: true,  // 启用大数据优化
        largeThreshold: 2000,  // 数据量超过2000时启用
        data: chartData
    }]
};
```

#### 图片懒加载
```typescript
// 使用 Intersection Observer 实现懒加载
const LazyImage = ({ src, alt }) => {
    const [isLoaded, setIsLoaded] = useState(false);
    const imgRef = useRef();
    
    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsLoaded(true);
                    observer.disconnect();
                }
            }
        );
        
        if (imgRef.current) {
            observer.observe(imgRef.current);
        }
        
        return () => observer.disconnect();
    }, []);
    
    return (
        <div ref={imgRef}>
            {isLoaded && <img src={src} alt={alt} />}
        </div>
    );
};
```

### 6.2 后端性能优化

#### 数据库查询优化
```python
# 使用索引优化查询
class StockService:
    def get_stocks_by_industry(self, industry_code, limit=100):
        # 使用索引查询
        query = select(Stock).where(
            Stock.industry_l1 == industry_code
        ).limit(limit)
        
        # 添加缓存
        cache_key = f"stocks:industry:{industry_code}:{limit}"
        cached = self.cache_service.get(cache_key)
        if cached:
            return cached
        
        result = self.db.execute(query).scalars().all()
        self.cache_service.set(cache_key, result, ttl=600)  # 缓存10分钟
        return result
```

#### 异步处理
```python
# 使用 asyncio 优化I/O密集型操作
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncDataService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def fetch_multiple_stocks(self, stock_codes):
        """异步获取多只股票数据"""
        loop = asyncio.get_event_loop()
        tasks = []
        
        for code in stock_codes:
            task = loop.run_in_executor(
                self.executor,
                self.sync_fetch_stock,
                code
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
```

#### 分页和流式处理
```python
# 大数据量分页处理
@app.get("/api/v1/market/stocks")
async def get_stocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    market_type: str = Query(None)
):
    offset = (page - 1) * page_size
    
    query = select(Stock)
    if market_type:
        query = query.where(Stock.market_type == market_type)
    
    # 总数查询
    total_query = select(func.count()).select_from(query)
    total = await db.execute(total_query)
    total_count = total.scalar()
    
    # 数据查询
    stocks_query = query.offset(offset).limit(page_size)
    stocks = await db.execute(stocks_query)
    
    return {
        "stocks": [stock.to_dict() for stock in stocks.scalars()],
        "total": total_count,
        "page": page,
        "page_size": page_size
    }
```

### 6.3 缓存策略

#### 多级缓存
```python
class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.local_cache = {}
    
    async def get(self, key: str):
        # 先查本地缓存
        if key in self.local_cache:
            return self.local_cache[key]
        
        # 再查Redis
        value = await self.redis_client.get(key)
        if value:
            # 解析JSON并存入本地缓存
            data = json.loads(value)
            self.local_cache[key] = data
            return data
        
        return None
    
    async def set(self, key: str, value, ttl: int = 3600):
        # 设置Redis缓存
        json_value = json.dumps(value, ensure_ascii=False)
        await self.redis_client.setex(key, ttl, json_value)
        
        # 设置本地缓存（短期）
        self.local_cache[key] = value
```

## 7. 部署架构

### 7.1 Docker容器化

#### 后端Dockerfile
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端Dockerfile
```dockerfile
# 前端构建镜像
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# 生产镜像
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # 后端服务
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:password@mysql:3306/stock_analysis
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - mysql
      - redis
    restart: unless-stopped

  # 前端服务
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  # MySQL数据库
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: stock_analysis
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### 7.2 Nginx配置

```nginx
# nginx.conf
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # 前端静态资源
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket支持
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 7.3 监控和日志

#### Prometheus监控
```yaml
# docker-compose.yml 中添加监控
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
```

#### 日志配置
```python
# logging.conf
[loggers]
keys=root,app,api

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[logger_app]
level=DEBUG
handlers=consoleHandler
qualname=app
propagate=0

[logger_api]
level=INFO
handlers=fileHandler
qualname=api
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=detailedFormatter
args=('logs/app.log', 'a')

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s
```

## 8. 安全策略

### 8.1 API安全

#### 认证中间件
```python
# middleware/auth.py
from fastapi import Request, HTTPException
import jwt
from datetime import datetime, timedelta

class AuthMiddleware:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    async def authenticate(self, request: Request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            request.state.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

#### 限流中间件
```python
# middleware/rate_limit.py
from fastapi import Request, HTTPException
from redis.asyncio import Redis
import time

class RateLimitMiddleware:
    def __init__(self, redis_client: Redis, limit: int = 100, window: int = 60):
        self.redis = redis_client
        self.limit = limit
        self.window = window
    
    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        current_time = time.time()
        window_start = current_time - self.window
        
        # 移除窗口外的请求记录
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # 计算当前窗口内的请求数
        request_count = await self.redis.zcard(key)
        
        if request_count >= self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # 记录当前请求
        await self.redis.zadd(key, {str(current_time): current_time})
        await self.redis.expire(key, self.window)
```

### 8.2 数据安全

#### 敏感信息加密
```python
# utils/encryption.py
from cryptography.fernet import Fernet
import os

class EncryptionService:
    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            os.environ['ENCRYPTION_KEY'] = key.decode()
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

#### SQL注入防护
```python
# 使用 SQLAlchemy ORM 防止SQL注入
from sqlalchemy import select
from models import Stock

class StockService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_stocks_by_industry(self, industry_code: str):
        # 使用参数化查询，防止SQL注入
        query = select(Stock).where(Stock.industry_l1 == industry_code)
        result = await self.db.execute(query)
        return result.scalars().all()
```

## 9. 测试策略

### 9.1 单元测试

#### 后端单元测试
```python
# tests/test_market_service.py
import pytest
from services.market_service import MarketService
from unittest.mock import Mock, patch

class TestMarketService:
    @pytest.fixture
    def market_service(self):
        return MarketService()
    
    @patch('services.market_service.tushare.pro_api')
    def test_get_stock_basic(self, mock_pro):
        # Mock Tushare API
        mock_df = Mock()
        mock_df.to_dict.return_value = [{'code': '000001', 'name': '平安银行'}]
        mock_pro.return_value.stock_basic.return_value = mock_df
        
        result = self.market_service.get_stock_basic()
        
        assert len(result) == 1
        assert result[0]['code'] == '000001'
```

#### 前端单元测试
```typescript
// tests/components/StarChart.test.tsx
import { render, screen } from '@testing-library/react';
import StarChart from '../components/StarChart';
import { useStarChart } from '../hooks/useStarChart';

jest.mock('../hooks/useStarChart');

const mockUseStarChart = useStarChart as jest.MockedFunction<typeof useStarChart>;

describe('StarChart', () => {
    it('should render loading state', () => {
        mockUseStarChart.mockReturnValue({
            data: null,
            loading: true,
            error: null
        });
        
        render(<StarChart marketType="沪深A股" period="5日" sizeMetric="市值" />);
        
        expect(screen.getByText('加载中...')).toBeInTheDocument();
    });
});
```

### 9.2 集成测试

#### API集成测试
```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_stocks():
    response = client.get("/api/v1/market/stocks?market_type=主板&page=1&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert 'stocks' in data['data']
    assert len(data['data']['stocks']) <= 10
```

### 9.3 性能测试

#### 压力测试
```python
# tests/test_performance.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class PerformanceTest:
    async def test_concurrent_requests(self):
        """测试并发请求性能"""
        start_time = time.time()
        
        # 模拟100个并发请求
        tasks = []
        for i in range(100):
            task = self.make_request(f"/api/v1/market/stocks?page={i+1}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"100个并发请求耗时: {duration:.2f}秒")
        print(f"平均响应时间: {duration/100:.2f}秒")
        
        # 验证所有请求都成功
        assert all(result.status_code == 200 for result in results)
```

## 10. 开发规范

### 10.1 代码规范

#### Python代码规范
```python
# 使用 Black 格式化代码
# 使用 isort 排序导入
# 使用 flake8 检查代码质量

# 示例：符合规范的代码
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from models import Stock


class StockService:
    """股票服务类"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_stocks(
        self, 
        market_type: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 100
    ) -> List[Stock]:
        """
        获取股票列表
        
        Args:
            market_type: 市场类型
            industry: 行业代码
            limit: 限制数量
            
        Returns:
            股票列表
        """
        query = select(Stock)
        
        if market_type:
            query = query.where(Stock.market_type == market_type)
        
        if industry:
            query = query.where(Stock.industry_l1 == industry)
        
        query = query.limit(limit)
        result = await self.db.execute(query)
        
        return result.scalars().all()
```

#### TypeScript代码规范
```typescript
// 使用 ESLint + Prettier
// 遵循 React Hooks 规范

interface Stock {
    code: string;
    name: string;
    changeRate: number;
    marketCap: number;
}

interface StockListProps {
    stocks: Stock[];
    loading: boolean;
    onStockClick: (stock: Stock) => void;
}

const StockList: React.FC<StockListProps> = ({ 
    stocks, 
    loading, 
    onStockClick 
}) => {
    if (loading) {
        return <div>加载中...</div>;
    }
    
    return (
        <div className="stock-list">
            {stocks.map((stock) => (
                <StockItem 
                    key={stock.code}
                    stock={stock}
                    onClick={() => onStockClick(stock)}
                />
            ))}
        </div>
    );
};
```

### 10.2 Git工作流

#### 分支策略
```
main (生产环境)
├── develop (开发环境)
├── feature/xxx (功能分支)
├── bugfix/xxx (修复分支)
└── hotfix/xxx (紧急修复分支)
```

#### 提交规范
```
<type>: <subject>

<body>

<footer>
```

**类型说明:**
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

**示例:**
```
feat: 添加大盘星图可视化功能

- 实现气泡图组件
- 支持市值/成交额切换
- 添加鼠标悬停提示

Closes #123
```

## 11. 项目里程碑

### 11.1 详细开发计划

| 阶段 | 时间 | 主要任务 | 交付物 |
|------|------|----------|--------|
| **M1: 项目初始化** | 第1周 | • 搭建项目框架<br>• 配置开发环境<br>• 对接Tushare数据源<br>• 建立数据库模型 | • 项目基础框架<br>• 数据库设计文档<br>• 基础API接口 |
| **M2: 行业趋势分析** | 第2周 | • 实现行业树组件<br>• 开发行情数据接口<br>• 实现行业资金流向分析<br>• 前端页面开发 | • 行业分析页面<br>• 相关API接口<br>• 数据可视化组件 |
| **M3: 大盘星图** | 第3周 | • ECharts气泡图实现<br>• 数据处理和映射<br>• 交互功能开发<br>• 性能优化 | • 大盘星图页面<br>• 图表组件<br>• 优化后的数据处理逻辑 |
| **M4: 市场热点分析** | 第4-5周 | • 爬虫开发<br>• LLM集成<br>• 情感分析算法<br>• 词云图实现 | • 热点分析页面<br>• 爬虫服务<br>• LLM分析接口 |
| **M5: 联调测试** | 第6周 | • 端到端测试<br>• 性能调优<br>• 安全加固<br>• 部署上线 | • 测试报告<br>• 部署文档<br>• 上线版本 |

### 11.2 风险控制

| 风险项 | 风险等级 | 应对策略 |
|--------|----------|----------|
| 数据源接口限制 | 高 | • 多数据源备份<br>• 合理控制调用频率<br>• 建立本地缓存机制 |
| LLM API成本 | 中 | • 设置调用频率限制<br>• 结果缓存复用<br>• 选择性价比高的服务商 |
| 爬虫被封禁 | 高 | • 遵守robots.txt<br>• 控制请求频率<br>• 使用代理IP池<br>• 多个数据源备份 |
| 性能问题 | 中 | • 前端虚拟化<br>• 后端异步处理<br>• 数据库索引优化<br>• 缓存策略 |

## 12. 总结

本技术设计文档详细规划了A股智能选股分析平台的技术架构、数据库设计、API接口、前端架构、数据采集、性能优化、部署方案、安全策略、测试策略和开发规范。

### 核心亮点

1. **现代化技术栈**: React + FastAPI + MySQL + Redis
2. **高性能设计**: 多级缓存、异步处理、虚拟化渲染
3. **可扩展架构**: 模块化设计，易于功能扩展
4. **数据驱动**: 多数据源整合，LLM智能分析
5. **容器化部署**: Docker + Nginx，易于运维

### 技术挑战与解决方案

- **大数据量渲染**: 使用ECharts大数据优化 + 虚拟化
- **实时数据更新**: WebSocket + Redis缓存
- **LLM成本控制**: 智能缓存 + 调用频率控制
- **爬虫稳定性**: 多源备份 + 频率控制 + 代理池

通过本技术方案的实施，将构建一个高性能、可扩展、用户体验优秀的A股智能选股分析平台。