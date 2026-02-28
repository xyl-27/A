import React from 'react';
import { Link } from 'react-router-dom';
import { Menu } from 'antd';
import { HomeOutlined, LineChartOutlined, StarOutlined, FireOutlined } from '@ant-design/icons';

const NavBar: React.FC = () => {
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/industry',
      icon: <LineChartOutlined />,
      label: <Link to="/industry">行业分析</Link>,
    },
    {
      key: '/star-chart',
      icon: <StarOutlined />,
      label: <Link to="/star-chart">大盘星图</Link>,
    },
    {
      key: '/hot-topics',
      icon: <FireOutlined />,
      label: <Link to="/hot-topics">市场热点</Link>,
    },
  ];

  return (
    <Menu
      theme="dark"
      mode="horizontal"
      defaultSelectedKeys={['/']}
      items={menuItems}
      style={{ position: 'fixed', top: 0, width: '100%', zIndex: 1000 }}
    />
  );
};

export default NavBar;
