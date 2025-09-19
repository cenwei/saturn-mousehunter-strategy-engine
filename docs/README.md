# 策略引擎API索引

## 📚 文档目录

| 文件 | 描述 | API数量 |
|------|------|---------|
| [openapi.json](./api/openapi.json) | 主OpenAPI规范文件 | 35个接口总览 |
| [strategy-definitions.json](./api/strategy-definitions.json) | 策略定义管理 | 7个接口 |
| [strategy-signals.json](./api/strategy-signals.json) | 交易信号管理 | 9个接口 |
| [strategy-backtests.json](./api/strategy-backtests.json) | 回测管理 | 17个接口 |
| [system.json](./api/system.json) | 系统接口 | 2个接口 |
| [FRONTEND_DEVELOPMENT_GUIDE.md](./FRONTEND_DEVELOPMENT_GUIDE.md) | 前端开发指南 | - |

## 🔗 快速链接

### 服务地址
- **在线API文档**: http://192.168.8.168:8002/docs
- **策略引擎服务**: http://192.168.8.168:8002
- **认证服务**: http://192.168.8.168:8001

### 核心功能
- **[策略管理](#策略管理)**: 策略的创建、查询、审批等
- **[信号管理](#信号管理)**: 多时间周期交易信号处理
- **[回测管理](#回测管理)**: 完整的回测生命周期管理

## 📋 API接口清单

### 策略管理
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/strategies` | 创建策略 |
| GET | `/api/v1/strategies` | 获取策略列表 |
| GET | `/api/v1/strategies/{id}` | 获取策略详情 |
| PUT | `/api/v1/strategies/{id}` | 更新策略 |
| DELETE | `/api/v1/strategies/{id}` | 删除策略 |
| GET | `/api/v1/strategies/{id}/approve` | 审批策略 |
| GET | `/api/v1/strategies/stats/popular` | 获取热门策略 |

### 信号管理
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/signals/` | 创建信号 |
| GET | `/api/v1/signals/` | 获取信号列表 |
| GET | `/api/v1/signals/{signal_id}` | 获取信号详情 |
| PUT | `/api/v1/signals/{signal_id}/status` | 更新信号状态 |
| GET | `/api/v1/signals/symbol/{symbol}/timeframe/{timeframe}` | 按标的和周期获取信号 |
| GET | `/api/v1/signals/stats/{strategy_instance_id}` | 获取信号统计 |
| GET | `/api/v1/signals/latest/all` | 获取最新信号 |
| POST | `/api/v1/signals/maintenance/expire-old` | 批量过期旧信号 |
| DELETE | `/api/v1/signals/maintenance/cleanup` | 清理旧信号数据 |

### 回测管理
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/backtests/` | 创建回测任务 |
| GET | `/api/v1/backtests/` | 获取回测列表 |
| GET | `/api/v1/backtests/{id}` | 获取回测详情 |
| PUT | `/api/v1/backtests/{id}/status` | 更新回测状态 |
| POST | `/api/v1/backtests/{id}/results` | 保存回测结果 |
| GET | `/api/v1/backtests/{id}/results` | 获取回测结果 |
| GET | `/api/v1/backtests/{id}/complete` | 获取完整回测信息 |
| GET | `/api/v1/backtests/with-results/list` | 获取带结果的回测列表 |
| GET | `/api/v1/backtests/performance/{strategy_id}/comparison` | 绩效对比 |
| POST | `/api/v1/backtests/{id}/start` | 启动回测 |
| POST | `/api/v1/backtests/{id}/cancel` | 取消回测 |
| DELETE | `/api/v1/backtests/{id}` | 删除回测 |
| POST | `/api/v1/backtests/maintenance/cleanup` | 清理旧回测 |
| GET | `/api/v1/backtests/engine/status` | 回测引擎状态 |
| GET | `/api/v1/backtests/templates` | 回测模板 |

### 系统接口
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/` | 根路径 |

## 🎯 关键特性

### 多时间周期支持
支持以下时间周期：
- **分钟级**: 1m, 5m, 15m, 30m
- **小时级**: 1h, 4h
- **日级**: 1d
- **周/月级**: 1w, 1M

### 信号类型
- **BUY**: 买入信号
- **SELL**: 卖出信号
- **HOLD**: 持有信号
- **LONG**: 开多信号
- **SHORT**: 开空信号
- **CLOSE**: 平仓信号

### 认证与权限
- **JWT Token**: 所有API需要Bearer认证
- **权限级别**: admin, tenant_admin, user
- **认证集成**: 调用外部认证服务验证

## 🔧 开发工具

### 生成客户端代码
```bash
# TypeScript客户端
npx @openapitools/openapi-generator-cli generate \
  -i ./docs/api/openapi.json \
  -g typescript-fetch \
  -o ./generated/typescript

# Python客户端
npx @openapitools/openapi-generator-cli generate \
  -i ./docs/api/openapi.json \
  -g python \
  -o ./generated/python
```

### Mock服务
```bash
# 启动Mock服务器
prism mock ./docs/api/openapi.json --port 3001
```

## 📊 使用统计

- **总计API接口**: 35个
- **支持时间周期**: 9种
- **信号类型**: 6种
- **回测状态**: 5种
- **策略状态**: 5种

## 🚀 快速测试

使用提供的测试脚本快速验证API功能：

```bash
# 完整功能测试
./test_complete_strategy_api.sh

# 基础功能测试
./test_strategy_api.sh
```

## 📞 技术支持

如有问题请参考：
1. [前端开发指南](./FRONTEND_DEVELOPMENT_GUIDE.md)
2. 在线API文档: http://192.168.8.168:8002/docs
3. 测试脚本验证功能

---

*文档更新时间: 2024-01-01*
*API版本: 1.0.0*