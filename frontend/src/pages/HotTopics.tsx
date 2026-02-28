import React, { useState, useEffect } from 'react';
import { Card, Row, Col, List, Tag, Button, Spin, Select, Statistic } from 'antd';
import ReactECharts from 'echarts-for-react';
import { hotTopicsApi } from '../services/api';

interface HotTopic {
  id: number;
  title: string;
  content: string;
  source: string;
  url: string;
  sentiment_label: string;
  sentiment_score: number;
  keywords: string[];
  heat: number;
}

const HotTopics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [topics, setTopics] = useState<HotTopic[]>([]);
  const [sentimentFilter, setSentimentFilter] = useState<string | null>(null);

  useEffect(() => {
    loadTopics();
  }, [sentimentFilter]);

  const loadTopics = async () => {
    setLoading(true);
    try {
      const mockTopics: HotTopic[] = [
        {
          id: 1,
          title: '人工智能板块持续爆发，多家公司发布新产品',
          content: '近日，多家人工智能相关公司发布新产品，板块持续受到资金追捧...',
          source: '雪球',
          url: 'https://xueqiu.com',
          sentiment_label: '看涨',
          sentiment_score: 0.8,
          keywords: ['人工智能', '新产品', '爆发'],
          heat: 15000,
        },
        {
          id: 2,
          title: '新能源车销量不及预期，板块集体回调',
          content: '最新数据显示，新能源车销量环比下降...',
          source: '东方财富股吧',
          url: 'https://guba.eastmoney.com',
          sentiment_label: '看跌',
          sentiment_score: -0.6,
          keywords: ['新能源车', '销量', '回调'],
          heat: 12000,
        },
        {
          id: 3,
          title: '白酒板块震荡整理，关注业绩确定性',
          content: '白酒板块近期走势震荡...',
          source: '雪球',
          url: 'https://xueqiu.com',
          sentiment_label: '中性',
          sentiment_score: 0.1,
          keywords: ['白酒', '业绩', '震荡'],
          heat: 8000,
        },
      ];
      setTopics(mockTopics);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (label: string) => {
    switch (label) {
      case '看涨':
        return 'red';
      case '看跌':
        return 'green';
      default:
        return 'blue';
    }
  };

  const sentimentData = [
    { value: topics.filter((t) => t.sentiment_label === '看涨').length, name: '看涨' },
    { value: topics.filter((t) => t.sentiment_label === '看跌').length, name: '看跌' },
    { value: topics.filter((t) => t.sentiment_label === '中性').length, name: '中性' },
  ];

  const sentimentOption = {
    tooltip: { trigger: 'item' },
    legend: { bottom: '0%' },
    series: [
      {
        name: '情感分布',
        type: 'pie',
        radius: ['40%', '70%'],
        data: sentimentData,
        itemStyle: {
          color: (params: { name: string }) => {
            switch (params.name) {
              case '看涨':
                return '#ff4d4f';
              case '看跌':
                return '#52c41a';
              default:
                return '#1890ff';
            }
          },
        },
      },
    ],
  };

  const keywords = topics.flatMap((t) => t.keywords || []);
  const keywordCount = keywords.reduce(
    (acc, kw) => {
      acc[kw] = (acc[kw] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );
  const topKeywords = Object.entries(keywordCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  if (loading) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />;
  }

  return (
    <div>
      <h1>市场热点分析</h1>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card
            title="热门话题"
            extra={
              <Select
                placeholder="筛选情感"
                style={{ width: 120 }}
                allowClear
                onChange={setSentimentFilter}
                options={[
                  { value: '看涨', label: '看涨' },
                  { value: '看跌', label: '看跌' },
                  { value: '中性', label: '中性' },
                ]}
              />
            }
          >
            <List
              itemLayout="vertical"
              dataSource={topics}
              renderItem={(item) => (
                <List.Item
                  key={item.id}
                  actions={[
                    <Tag color={getSentimentColor(item.sentiment_label)} key="sentiment">
                      {item.sentiment_label}
                    </Tag>,
                    <span key="heat">🔥 {item.heat}</span>,
                    <span key="source">{item.source}</span>,
                  ]}
                >
                  <List.Item.Meta
                    title={<a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>}
                    description={item.content}
                  />
                  <div>
                    {item.keywords?.map((kw) => (
                      <Tag key={kw} style={{ marginBottom: 4 }}>
                        {kw}
                      </Tag>
                    ))}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="情感分布">
            <ReactECharts option={sentimentOption} style={{ height: 250 }} />
          </Card>
          <Card title="热点关键词" style={{ marginTop: 16 }}>
            {topKeywords.map(([kw, count]) => (
              <div key={kw} style={{ marginBottom: 8 }}>
                <span>{kw}</span>
                <span style={{ float: 'right', color: '#666' }}>{count}</span>
              </div>
            ))}
          </Card>
          <Card style={{ marginTop: 16 }}>
            <Statistic title="话题总数" value={topics.length} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HotTopics;
