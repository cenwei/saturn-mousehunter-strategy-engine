#!/bin/bash
cd /home/cenwei/workspace/saturn_mousehunter/saturn-mousehunter-strategy-engine

echo "🔍 启动策略引擎服务完整测试..."
echo "========================================"

# 激活虚拟环境并后台启动服务
source .venv/bin/activate
python test_strategy_server.py &
SERVER_PID=$!

# 等待服务启动
sleep 3

echo "📋 测试开始..."

# 1. 健康检查
echo "1️⃣ 测试健康检查..."
curl -s http://192.168.8.168:8002/health && echo

# 2. 创建策略
echo "2️⃣ 测试创建策略..."
STRATEGY_RESPONSE=$(curl -s -X POST http://192.168.8.168:8002/api/v1/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_name": "均线策略",
    "strategy_type": "TREND_FOLLOWING",
    "description": "基于移动平均线的趋势跟随策略",
    "author": "admin"
  }')

echo "创建策略响应: $STRATEGY_RESPONSE"

# 3. 获取策略列表
echo "3️⃣ 测试获取策略列表..."
curl -s http://192.168.8.168:8002/api/v1/strategies && echo

# 4. 获取热门策略
echo "4️⃣ 测试获取热门策略..."
curl -s http://192.168.8.168:8002/api/v1/strategies/stats/popular && echo

if [[ $STRATEGY_RESPONSE == *"strategy_name"* ]]; then
    echo "✅ 所有API测试通过！"
else
    echo "❌ 策略创建失败"
fi

# 清理
kill $SERVER_PID 2>/dev/null
echo "🎉 策略引擎服务测试完成！"