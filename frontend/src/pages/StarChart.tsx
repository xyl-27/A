import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, Radio, Statistic, Spin } from 'antd';
import ReactECharts from 'echarts-for-react';
import { starChartApi } from '../services/api';

interface StockPoint {
  code: string;
  name: string;
  change_rate: number;
  market_cap: number;
  volume: number;
  size: number;
  color: string;
  is_my_stock: boolean;
}

interface StarChartData {
  stocks: StockPoint[];
  summary: {
    total_count: number;
    up_count: number;
    down_count: number;
    avg_change_rate: number;
  };
}

const StarChart: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<StarChartData | null>(null);
  const [marketType, setMarketType] = useState('沪深A股');
  const [period, setPeriod] = useState('5日');
  const [sizeMetric, setSizeMetric] = useState('市值');

  useEffect(() => {
    loadData();
  }, [marketType, period, sizeMetric]);

  const loadData = async () => {
    setLoading(true);
    try {
      const mockData: StarChartData = {
        stocks: Array.from({ length: 100 }, (_, i) => ({
          code: `${String(i).padStart(6, '0')}`,
          name: `股票${i}`,
          change_rate: (Math.random() - 0.5) * 10,
          market_cap: Math.random() * 100000000000,
          volume: Math.random() * 100000000,
          size: Math.random() * 100 + 20,
          color: '#ff0000',
          is_my_stock: false,
        })).map((stock) => ({
          ...stock,
          color: stock.change_rate >= 0 ? '#ff4d4f' : '#52c41a',
        })),
        summary: {
          total_count: 5000,
          up_count: 2800,
          down_count: 2100,
          avg_change_rate: 0.85,
        },
      };
      setData(mockData);
    } finally {
      setLoading(false);
    }
  };

  const chartOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: { data: StockPoint }) => {
        if (params.data) {
          return `${params.data.name}<br/>代码: ${params.data.code}<br/>涨跌幅: ${params.data.change_rate}%<br/>市值: ${(params.data.market_cap / 100000000).toFixed(2)}亿`;
        }
        return '';
      },
    },
    xAxis: {
      show: false,
      type: 'value',
    },
    yAxis: {
      show: false,
      type: 'value',
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (val: number[]) => val[2],
        data: data?.stocks.map((stock) => [
          Math.random() * 1000,
          Math.random() * 1000,
          stock.size,
          stock.code,
          stock.name,
          stock.change_rate,
          stock.market_cap,
          stock.is_my_stock,
        ]) || [],
        itemStyle: {
          color: (params: { data: (string | number)[] }) => {
            const changeRate = params.data[5] as number;
            return changeRate >= 0 ? '#ff4d4f' : '#52c41a';
          },
          opacity: 0.8,
        },
        emphasis: {
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 2,
          },
        },
      },
    ],
  };

  if (loading || !data) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />;
  }

  return (
    <div>
      <h1>大盘星图</h1>
      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col>
            <Select
              value={marketType}
              onChange={setMarketType}
              style={{ width: 120 }}
              options={[
                { value: '沪深A股', label: '沪深A股' },
                { value: '上证A股', label: '上证A股' },
                { value: '深证A股', label: '深证A股' },
                { value: '创业板', label: '创业板' },
                { value: '科创板', label: '科创板' },
              ]}
            />
          </Col>
          <Col>
            <Radio.Group value={period} onChange={(e) => setPeriod(e.target.value)}>
              <Radio.Button value="3日">3日</Radio.Button>
              <Radio.Button value="5日">5日</Radio.Button>
              <Radio.Button value="10日">10日</Radio.Button>
              <Radio.Button value="20日">20日</Radio.Button>
            </Radio.Group>
          </Col>
          <Col>
            <Radio.Group value={sizeMetric} onChange={(e) => setSizeMetric(e.target.value)}>
              <Radio.Button value="市值">市值</Radio.Button>
              <Radio.Button value="成交额">成交额</Radio.Button>
            </Radio.Group>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col>
            <Statistic title="股票总数" value={data.summary.total_count} />
          </Col>
          <Col>
            <Statistic title="上涨" value={data.summary.up_count} valueStyle={{ color: '#ff4d4f' }} />
          </Col>
          <Col>
            <Statistic title="下跌" value={data.summary.down_count} valueStyle={{ color: '#52c41a' }} />
          </Col>
          <Col>
            <Statistic
              title="平均涨跌幅"
              value={data.summary.avg_change_rate}
              precision={2}
              suffix="%"
            />
          </Col>
        </Row>

        <ReactECharts
          option={chartOption}
          style={{ height: '600px' }}
          opts={{ renderer: 'canvas' }}
        />

        <div style={{ marginTop: 16 }}>
          <span style={{ marginRight: 16 }}>图例:</span>
          <span style={{ color: '#ff4d4f', marginRight: 16 }}>● 上涨</span>
          <span style={{ color: '#52c41a' }}>● 下跌</span>
        </div>
      </Card>
    </div>
  );
};

export default StarChart;
