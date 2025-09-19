# 策略引擎前端开发指南

## 📋 API文档结构

本文档按功能模块拆分为以下几个文件，便于前端团队模块化开发：

### 1. 主文档
- **openapi.json** - 主OpenAPI规范，包含所有API的概览和引用

### 2. 功能模块
- **strategy-definitions.json** - 策略定义管理模块 (7个API)
- **strategy-signals.json** - 交易信号管理模块 (9个API)
- **strategy-backtests.json** - 回测管理模块 (17个API)
- **system.json** - 系统接口模块 (2个API)

## 🚀 快速开始

### 服务器信息
- **服务地址**: http://192.168.8.168:8002
- **API文档**: http://192.168.8.168:8002/docs
- **认证服务**: http://192.168.8.168:8001

### JWT认证
所有API接口都需要JWT认证，获取流程：

```javascript
// 1. 从认证服务获取token
const loginResponse = await fetch('http://192.168.8.168:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { access_token } = await loginResponse.json();

// 2. 在策略引擎API请求中使用token
const strategyResponse = await fetch('http://192.168.8.168:8002/api/v1/strategies', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 📦 前端开发建议

### 1. 页面结构建议
```
src/
  pages/
    strategies/           # 策略管理页面
      StrategyList.jsx    # 策略列表
      StrategyDetail.jsx  # 策略详情
      StrategyCreate.jsx  # 创建策略
    signals/              # 信号管理页面
      SignalDashboard.jsx # 信号看板
      SignalList.jsx      # 信号列表
      SignalChart.jsx     # 信号图表
    backtests/            # 回测管理页面
      BacktestList.jsx    # 回测列表
      BacktestCreate.jsx  # 创建回测
      BacktestResults.jsx # 回测结果
```

### 2. API调用封装
```javascript
// api/strategyEngine.js
class StrategyEngineAPI {
  constructor(baseURL, authToken) {
    this.baseURL = baseURL;
    this.authToken = authToken;
  }

  // 策略管理
  async getStrategies(params = {}) {
    return this.request('GET', '/api/v1/strategies', { params });
  }

  async createStrategy(data) {
    return this.request('POST', '/api/v1/strategies', { data });
  }

  // 信号管理
  async getSignals(params = {}) {
    return this.request('GET', '/api/v1/signals/', { params });
  }

  async createSignal(data) {
    return this.request('POST', '/api/v1/signals/', { data });
  }

  // 回测管理
  async getBacktests(params = {}) {
    return this.request('GET', '/api/v1/backtests/', { params });
  }

  async createBacktest(data) {
    return this.request('POST', '/api/v1/backtests/', { data });
  }

  async request(method, url, options = {}) {
    const config = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.authToken}`
      }
    };

    if (options.data) {
      config.body = JSON.stringify(options.data);
    }

    if (options.params) {
      url += '?' + new URLSearchParams(options.params).toString();
    }

    const response = await fetch(`${this.baseURL}${url}`, config);
    return response.json();
  }
}
```

## 🎯 重点功能开发说明

### 1. 策略管理模块
**主要功能**:
- 策略列表展示和筛选
- 策略创建向导
- 策略详情查看和编辑
- 策略审批流程

**关键API**:
- `GET /api/v1/strategies` - 策略列表
- `POST /api/v1/strategies` - 创建策略
- `GET /api/v1/strategies/{id}` - 策略详情
- `GET /api/v1/strategies/{id}/approve` - 审批策略

### 2. 信号管理模块
**主要功能**:
- 实时信号监控
- 多时间周期信号展示
- 信号统计分析
- 信号执行状态管理

**时间周期支持**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
**信号类型支持**: BUY, SELL, HOLD, LONG, SHORT, CLOSE

**关键API**:
- `GET /api/v1/signals/` - 信号列表
- `POST /api/v1/signals/` - 创建信号
- `GET /api/v1/signals/symbol/{symbol}/timeframe/{timeframe}` - 按标的和周期查询
- `GET /api/v1/signals/stats/{strategy_instance_id}` - 信号统计

### 3. 回测管理模块
**主要功能**:
- 回测任务创建和管理
- 回测进度监控
- 回测结果可视化
- 绩效对比分析

**关键API**:
- `POST /api/v1/backtests/` - 创建回测
- `GET /api/v1/backtests/{id}/complete` - 完整回测信息
- `POST /api/v1/backtests/{id}/start` - 启动回测
- `GET /api/v1/backtests/{id}/results` - 回测结果

## 📊 数据模型参考

### 策略定义
```typescript
interface StrategyDefinition {
  id: string;
  strategy_name: string;
  strategy_type: 'TREND_FOLLOWING' | 'MEAN_REVERSION' | 'ARBITRAGE' | 'MULTI_FACTOR';
  category: string;
  description: string;
  author: string;
  status: 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'ARCHIVED';
  supported_markets: string[];
  time_frames: string[];
  max_position_size: number;
  created_at: string;
}
```

### 交易信号
```typescript
interface TradingSignal {
  id: string;
  strategy_instance_id: string;
  signal_type: 'BUY' | 'SELL' | 'HOLD' | 'LONG' | 'SHORT' | 'CLOSE';
  symbol: string;
  timeframe: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';
  price: number;
  quantity: number;
  confidence: number; // 0-1
  status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'EXPIRED';
  signal_time: string;
  created_at: string;
}
```

### 回测任务
```typescript
interface BacktestTask {
  id: string;
  backtest_name: string;
  strategy_id: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  progress: number; // 0-100
  created_at: string;
}
```

## 🔧 开发工具推荐

### 1. OpenAPI代码生成
```bash
# 使用openapi-generator生成TypeScript客户端
npx @openapitools/openapi-generator-cli generate \
  -i http://192.168.8.168:8002/docs/api/openapi.json \
  -g typescript-fetch \
  -o src/api/generated
```

### 2. API Mock服务
```bash
# 使用prism创建Mock服务
npm install -g @stoplight/prism-cli
prism mock docs/api/openapi.json --port 3001
```

### 3. React查询库推荐
- **React Query** - 用于API状态管理
- **SWR** - 轻量级数据获取
- **Axios** - HTTP客户端

## 📈 实时数据建议

对于信号监控等实时功能，建议使用：
- **WebSocket** - 实时信号推送 (需后端实现)
- **轮询** - 定期获取最新数据
- **Server-Sent Events** - 服务端推送更新

## 🎨 UI组件建议

### 1. 信号展示组件
- 信号卡片组件 (显示信号类型、价格、时间)
- 时间周期选择器
- 信号状态标签
- 置信度进度条

### 2. 回测结果组件
- 净值曲线图表
- 绩效指标卡片
- 交易历史表格
- 回测进度条

### 3. 策略管理组件
- 策略卡片网格
- 策略筛选器
- 策略状态流程图
- 参数配置表单

## 📚 测试数据

使用测试脚本 `test_complete_strategy_api.sh` 可以生成测试数据：
- 创建示例策略
- 生成多时间周期信号
- 创建回测任务

这些数据可以用于前端开发和测试。