"""
策略引擎服务简化测试版本
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from decimal import Decimal


class StrategyIn(BaseModel):
    strategy_name: str
    strategy_type: str
    description: Optional[str] = None
    author: str


class StrategyOut(BaseModel):
    id: str
    strategy_name: str
    strategy_type: str
    description: Optional[str]
    author: str
    status: str = "DRAFT"
    created_at: datetime
    is_active: bool = True


# 简化的内存存储
strategies_db = {}
strategy_counter = 1

app = FastAPI(
    title="Saturn MouseHunter Strategy Engine",
    version="1.0.0",
    description="策略引擎服务 - 提供策略管理、信号生成、回测功能"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "Saturn MouseHunter Strategy Engine",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "strategy-engine",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/v1/strategies", response_model=StrategyOut)
def create_strategy(strategy_data: StrategyIn):
    """创建策略"""
    global strategy_counter

    # 检查策略名称重复
    for strategy in strategies_db.values():
        if strategy.strategy_name == strategy_data.strategy_name:
            raise HTTPException(status_code=400, detail="策略名称已存在")

    strategy_id = f"strategy_{strategy_counter}"
    strategy_counter += 1

    new_strategy = StrategyOut(
        id=strategy_id,
        strategy_name=strategy_data.strategy_name,
        strategy_type=strategy_data.strategy_type,
        description=strategy_data.description,
        author=strategy_data.author,
        created_at=datetime.now(timezone.utc)
    )

    strategies_db[strategy_id] = new_strategy
    return new_strategy


@app.get("/api/v1/strategies", response_model=List[StrategyOut])
def list_strategies(
    strategy_type: Optional[str] = None,
    author: Optional[str] = None,
    limit: int = 50
):
    """获取策略列表"""
    strategies = list(strategies_db.values())

    # 过滤条件
    if strategy_type:
        strategies = [s for s in strategies if s.strategy_type == strategy_type]
    if author:
        strategies = [s for s in strategies if s.author == author]

    return strategies[:limit]


@app.get("/api/v1/strategies/{strategy_id}", response_model=StrategyOut)
def get_strategy(strategy_id: str):
    """获取策略详情"""
    if strategy_id not in strategies_db:
        raise HTTPException(status_code=404, detail="策略不存在")

    return strategies_db[strategy_id]


@app.put("/api/v1/strategies/{strategy_id}", response_model=StrategyOut)
def update_strategy(strategy_id: str, update_data: dict):
    """更新策略"""
    if strategy_id not in strategies_db:
        raise HTTPException(status_code=404, detail="策略不存在")

    strategy = strategies_db[strategy_id]

    # 更新字段
    for field, value in update_data.items():
        if hasattr(strategy, field) and field != 'id':
            setattr(strategy, field, value)

    return strategy


@app.delete("/api/v1/strategies/{strategy_id}")
def delete_strategy(strategy_id: str):
    """删除策略"""
    if strategy_id not in strategies_db:
        raise HTTPException(status_code=404, detail="策略不存在")

    del strategies_db[strategy_id]
    return {"message": "策略删除成功"}


@app.get("/api/v1/strategies/{strategy_id}/approve", response_model=StrategyOut)
def approve_strategy(strategy_id: str):
    """审批策略"""
    if strategy_id not in strategies_db:
        raise HTTPException(status_code=404, detail="策略不存在")

    strategy = strategies_db[strategy_id]
    strategy.status = "APPROVED"

    return strategy


@app.get("/api/v1/strategies/stats/popular", response_model=List[StrategyOut])
def get_popular_strategies(limit: int = 10):
    """获取热门策略"""
    strategies = list(strategies_db.values())
    # 简化实现，返回前N个
    return strategies[:limit]


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动策略引擎服务...")
    print("📍 访问地址:")
    print("   - API文档: http://192.168.8.168:8002/docs")
    print("   - 健康检查: http://192.168.8.168:8002/health")
    print("   - 创建策略: POST http://192.168.8.168:8002/api/v1/strategies")

    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=8002,
        reload=False
    )