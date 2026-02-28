import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const marketApi = {
  getStocks: (params: {
    market_type?: string;
    industry_l1?: string;
    industry_l2?: string;
    page?: number;
    page_size?: number;
  }) => apiClient.get('/market/stocks', { params }),

  getQuotes: (codes: string[]) =>
    apiClient.get('/market/quotes', { params: { codes: codes.join(',') } }),
};

export const industryApi = {
  getTree: () => apiClient.get('/industry/tree'),
  getFunds: (industryCode: string, days: number) =>
    apiClient.get('/industry/funds', { params: { industry_code: industryCode, days } }),
  getStocks: (industryCode: string, level: number) =>
    apiClient.get('/industry/stocks', { params: { industry_code: industryCode, level } }),
};

export const starChartApi = {
  getData: (params: {
    market_type?: string;
    period?: string;
    size_metric?: string;
    highlight_stocks?: string;
  }) => apiClient.get('/star-chart/data', { params }),
};

export const hotTopicsApi = {
  getList: (params: { limit?: number; sentiment?: string; source?: string }) =>
    apiClient.get('/hot-topics/list', { params }),
  analyze: (content: string, analysisType: string = 'sentiment') =>
    apiClient.post('/hot-topics/analyze', { content, analysis_type: analysisType }),
  refresh: () => apiClient.post('/hot-topics/refresh'),
};

export default apiClient;
