# Strategy Engine API Documentation

## 完整功能实现总结

### 1. 数据库集成 ✅
- **PostgreSQL集成**: 使用AsyncDAO模式，支持连接池管理
- **表结构**: 使用mh_strategy_*前缀的完整数据库表结构
- **主要表**:
  - `mh_strategy_definitions`: 策略定义表
  - `mh_strategy_versions`: 策略版本表
  - `mh_strategy_instances`: 策略实例表
  - `mh_strategy_signals`: 信号管理表
  - `mh_strategy_pools`: 策略池表
  - `mh_strategy_pool_members`: 策略池成员表
  - `mh_strategy_backtests`: 回测任务表
  - `mh_strategy_backtest_results`: 回测结果表

### 2. JWT认证集成 ✅
- **认证中间件**: 调用auth微服务(192.168.8.168:8001)验证token
- **权限管理**: 支持admin、tenant_admin等不同权限级别
- **安全保护**: 所有API接口都受JWT保护

### 3. 信号管理系统 ✅
- **多时间周期**: 支持1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
- **信号类型**: BUY, SELL, HOLD, LONG, SHORT, CLOSE
- **完整记录**: 时间、周期、价格、数量、置信度
- **状态管理**: PENDING, EXECUTED, CANCELLED, EXPIRED

### 4. 回测功能API ✅
- **完整回测管理**: 创建、启动、监控、取消回测任务
- **绩效分析**: 收益率、夏普比率、最大回撤等指标
- **历史对比**: 策略历史回测绩效对比功能

## API接口列表

### 策略定义 (Strategy Definition)
```
POST   /api/v1/strategies              # 创建策略
GET    /api/v1/strategies              # 获取策略列表
GET    /api/v1/strategies/{id}         # 获取策略详情
PUT    /api/v1/strategies/{id}         # 更新策略
DELETE /api/v1/strategies/{id}         # 删除策略
GET    /api/v1/strategies/{id}/approve # 审批策略
GET    /api/v1/strategies/stats/popular # 获取热门策略
```

### 信号管理 (Signal Management)
```
POST   /api/v1/signals/                           # 创建信号
GET    /api/v1/signals/{signal_id}               # 获取信号详情
GET    /api/v1/signals/                          # 获取信号列表
PUT    /api/v1/signals/{signal_id}/status        # 更新信号状态
GET    /api/v1/signals/symbol/{symbol}/timeframe/{timeframe} # 按标的和周期获取信号
GET    /api/v1/signals/stats/{strategy_instance_id}         # 获取信号统计
GET    /api/v1/signals/latest/all                # 获取最新信号
POST   /api/v1/signals/maintenance/expire-old    # 批量过期旧信号
DELETE /api/v1/signals/maintenance/cleanup       # 清理旧信号数据
```

### 回测管理 (Backtest Management)
```
POST   /api/v1/backtests/                        # 创建回测任务
GET    /api/v1/backtests/{backtest_id}          # 获取回测任务详情
GET    /api/v1/backtests/                       # 获取回测任务列表
PUT    /api/v1/backtests/{backtest_id}/status   # 更新回测状态
POST   /api/v1/backtests/{backtest_id}/results  # 保存回测结果
GET    /api/v1/backtests/{backtest_id}/results  # 获取回测结果
GET    /api/v1/backtests/{backtest_id}/complete # 获取完整回测信息
GET    /api/v1/backtests/with-results/list      # 获取带结果的回测列表
GET    /api/v1/backtests/performance/{strategy_id}/comparison # 绩效对比
POST   /api/v1/backtests/{backtest_id}/start    # 启动回测任务
POST   /api/v1/backtests/{backtest_id}/cancel   # 取消回测任务
DELETE /api/v1/backtests/{backtest_id}          # 删除回测任务
POST   /api/v1/backtests/maintenance/cleanup    # 清理旧回测数据
GET    /api/v1/backtests/engine/status          # 回测引擎状态
GET    /api/v1/backtests/templates              # 回测模板
```

## 多时间周期信号管理设计

### 支持的时间周期
- **分钟级**: 1m, 5m, 15m, 30m
- **小时级**: 1h, 4h
- **日级**: 1d
- **周/月级**: 1w, 1M

### 信号类型详细说明
```json
{
  "BUY": "买入信号",
  "SELL": "卖出信号",
  "HOLD": "持有信号",
  "LONG": "开多信号",
  "SHORT": "开空信号",
  "CLOSE": "平仓信号"
}
```

### 信号数据结构
```json
{
  "id": "uuid",
  "strategy_instance_id": "策略实例ID",
  "signal_type": "信号类型",
  "symbol": "交易标的",
  "timeframe": "时间周期",
  "price": "信号价格",
  "quantity": "数量",
  "confidence": "置信度(0-1)",
  "metadata": "元数据",
  "signal_time": "信号时间",
  "execution_time": "执行时间",
  "status": "状态",
  "created_at": "创建时间"
}
```

## 回测功能详细说明

### 回测任务状态
- **PENDING**: 等待执行
- **RUNNING**: 运行中
- **COMPLETED**: 已完成
- **FAILED**: 失败
- **CANCELLED**: 已取消

### 回测结果指标
```json
{
  "total_return": "总收益率",
  "annualized_return": "年化收益率",
  "volatility": "波动率",
  "sharpe_ratio": "夏普比率",
  "max_drawdown": "最大回撤",
  "win_rate": "胜率",
  "total_trades": "总交易次数",
  "profitable_trades": "盈利交易次数",
  "avg_trade_return": "平均交易收益",
  "detailed_metrics": "详细指标",
  "equity_curve": "净值曲线数据",
  "trade_history": "交易历史"
}
```

## 认证集成说明

### JWT Token验证流程
1. 客户端从auth服务获取token
2. 请求strategy服务时携带Bearer token
3. Strategy服务调用auth服务验证token
4. 验证成功后执行业务逻辑

### 权限级别
- **admin**: 管理员，拥有所有权限
- **tenant_admin**: 租户管理员
- **user**: 普通用户

## 服务配置
- **服务地址**: http://192.168.8.168:8002
- **数据库**: PostgreSQL (saturn_mousehunter database)
- **认证服务**: http://192.168.8.168:8001
- **API文档**: http://192.168.8.168:8002/docs

## 测试脚本
使用 `test_complete_strategy_api.sh` 进行完整功能测试，验证：
- 数据库连接和表结构
- JWT认证集成
- 策略管理API
- 信号管理API
- 回测管理API
- 多时间周期信号处理