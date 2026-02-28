import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import Home from './pages/Home';
import IndustryAnalysis from './pages/IndustryAnalysis';
import StarChart from './pages/StarChart';
import HotTopics from './pages/HotTopics';
import NavBar from './components/NavBar';

const { Content, Footer } = Layout;

const App: React.FC = () => {
  return (
    <Layout className="layout" style={{ minHeight: '100vh' }}>
      <NavBar />
      <Content style={{ padding: '0 50px', marginTop: 64 }}>
        <div className="site-layout-content" style={{ background: '#fff', padding: 24, minHeight: 'calc(100vh - 64 - 70px)' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/industry" element={<IndustryAnalysis />} />
            <Route path="/star-chart" element={<StarChart />} />
            <Route path="/hot-topics" element={<HotTopics />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        A股智能选股分析平台 ©2026 - 仅供参考，不构成投资建议
      </Footer>
    </Layout>
  );
};

export default App;
