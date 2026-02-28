import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Spin } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, StockOutlined, FireOutlined } from '@ant-design/icons';

interface MarketSummary {
  totalCount: number;
  upCount: number;
  downCount: number;
  avgChangeRate: number;
}

const Home: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<MarketSummary>({
    totalCount: 0,
    upCount: 0,
    downCount: 0,
    avgChangeRate: 0,
  });

  useEffect(() => {
    setTimeout(() => {
      setSummary({
        totalCount: 5000,
        upCount: 2800,
        downCount: 2100,
        avgChangeRate: 0.85,
      });
      setLoading(false);
    }, 500);
  }, []);

  if (loading) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />;
  }

  return (
    <div>
      <h1>欢迎使用A股智能选股分析平台</h1>
      <p style={{ marginBottom: 24, color: '#666' }}>
        利用AI大模型技术，帮助您分析行业趋势、把握市场热点、做出更明智的投资决策
      </p>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="A股总数"
              value={summary.totalCount}
              prefix={<StockOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="上涨家数"
              value={summary.upCount}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="下跌家数"
              value={summary.downCount}
              valueStyle={{ color: '#52c41a' }}
              prefix={<ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均涨跌幅"
              value={summary.avgChangeRate}
              precision={2}
              suffix="%"
              valueStyle={{ color: summary.avgChangeRate >= 0 ? '#ff4d4f' : '#52c41a' }}
              prefix={summary.avgChangeRate >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="功能导航" bordered={false}>
            <ul style={{ paddingLeft: 20 }}>
              <li><strong>行业分析</strong>：查看各一级、二级行业走势，了解资金流向</li>
              <li><strong>大盘星图</strong>：可视化全市场股票涨跌情况，一目了然</li>
              <li><strong>市场热点</strong>：追踪雪球、股吧等社区热门话题，把握市场情绪</li>
            </ul>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="风险提示" bordered={false} style={{ backgroundColor: '#fffbe6' }}>
            <ul style={{ paddingLeft: 20, color: '#666' }}>
              <li>本平台数据仅供参考，不构成任何投资建议</li>
              <li>股市有风险，投资需谨慎</li>
              <li>请勿将本平台信息作为投资决策的唯一依据</li>
            </ul>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Home;
