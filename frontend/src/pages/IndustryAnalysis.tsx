import React, { useState, useEffect } from 'react';
import { Card, Tree, Table, Tag, Spin, Row, Col, Statistic } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import ReactECharts from 'echarts-for-react';
import { industryApi } from '../services/api';

interface IndustryNode {
  code: string;
  name: string;
  level: number;
  children?: IndustryNode[];
}

interface StockInfo {
  code: string;
  name: string;
  change_rate: number;
}

const IndustryAnalysis: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [industryTree, setIndustryTree] = useState<IndustryNode[]>([]);
  const [selectedIndustry, setSelectedIndustry] = useState<string>('');
  const [stocks, setStocks] = useState<StockInfo[]>([]);

  useEffect(() => {
    loadIndustryTree();
  }, []);

  const loadIndustryTree = async () => {
    setLoading(true);
    try {
      const mockTree: IndustryNode[] = [
        {
          code: '金融',
          name: '金融',
          level: 1,
          children: [
            { code: '银行', name: '银行', level: 2 },
            { code: '证券', name: '证券', level: 2 },
            { code: '保险', name: '保险', level: 2 },
          ],
        },
        {
          code: '科技',
          name: '科技',
          level: 1,
          children: [
            { code: '半导体', name: '半导体', level: 2 },
            { code: '软件服务', name: '软件服务', level: 2 },
            { code: '电子', name: '电子', level: 2 },
          ],
        },
        {
          code: '消费',
          name: '消费',
          level: 1,
          children: [
            { code: '食品饮料', name: '食品饮料', level: 2 },
            { code: '家电', name: '家电', level: 2 },
            { code: '纺织服装', name: '纺织服装', level: 2 },
          ],
        },
      ];
      setIndustryTree(mockTree);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (keys: React.Key[]) => {
    if (keys.length > 0) {
      const key = keys[0] as string;
      setSelectedIndustry(key);
      const mockStocks: StockInfo[] = [
        { code: '000001', name: '平安银行', change_rate: 2.5 },
        { code: '600000', name: '浦发银行', change_rate: 1.8 },
        { code: '601398', name: '工商银行', change_rate: 1.2 },
      ];
      setStocks(mockStocks);
    }
  };

  const columns: ColumnsType<StockInfo> = [
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_rate',
      key: 'change_rate',
      render: (rate: number) => (
        <Tag color={rate >= 0 ? 'red' : 'green'}>
          {rate >= 0 ? '+' : ''}{rate}%
        </Tag>
      ),
    },
  ];

  const chartOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['银行', '证券', '保险', '半导体', '软件'],
    },
    yAxis: {
      type: 'value',
      name: '涨跌幅%',
    },
    series: [
      {
        data: [1.5, 2.1, -0.8, 3.2, 1.9],
        type: 'bar',
        itemStyle: {
          color: (params: { value: number }) => {
            return params.value >= 0 ? '#ff4d4f' : '#52c41a';
          },
        },
      },
    ],
  };

  if (loading) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />;
  }

  return (
    <div>
      <h1>行业趋势分析</h1>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="行业分类" bordered={false}>
            <Tree
              showLine
              defaultExpandAll
              treeData={industryTree.map((item) => ({
                key: item.code,
                title: item.name,
                children: item.children?.map((child) => ({
                  key: child.code,
                  title: child.name,
                })),
              }))}
              onSelect={handleSelect}
            />
          </Card>
        </Col>
        <Col xs={24} lg={16}>
          <Card title="行业涨跌幅" bordered={false}>
            <ReactECharts option={chartOption} style={{ height: 300 }} />
          </Card>
          <Card title={`${selectedIndustry || '请选择行业'} - 个股列表`} bordered={false} style={{ marginTop: 16 }}>
            <Table
              columns={columns}
              dataSource={stocks}
              rowKey="code"
              pagination={{ pageSize: 10 }}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default IndustryAnalysis;
