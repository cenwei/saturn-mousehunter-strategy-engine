"""
Strategy Signal Routes
策略信号API路由
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from api.middleware.auth import get_current_user, get_current_active_user
from api.dependencies.services import get_strategy_signal_repo
from infrastructure.repositories.strategy_signal_repo import StrategySignalRepository
from saturn_mousehunter_shared.log.logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/api/v1/signals", tags=["strategy-signals"])


# Pydantic Models
class SignalCreate(BaseModel):
    """创建信号请求"""
    strategy_instance_id: str
    signal_type: str = Field(..., regex=r'^(BUY|SELL|HOLD|LONG|SHORT|CLOSE)$')
    symbol: str
    timeframe: str = Field(..., regex=r'^(1m|5m|15m|30m|1h|4h|1d|1w|1M)$')
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    confidence: Optional[Decimal] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None
    signal_time: Optional[datetime] = None


class SignalResponse(BaseModel):
    """信号响应"""
    id: str
    strategy_instance_id: str
    signal_type: str
    symbol: str
    timeframe: str
    price: Optional[Decimal]
    quantity: Optional[int]
    confidence: Optional[Decimal]
    metadata: Optional[Dict[str, Any]]
    signal_time: datetime
    execution_time: Optional[datetime]
    status: str
    created_at: datetime


class SignalUpdate(BaseModel):
    """更新信号状态"""
    status: str = Field(..., regex=r'^(PENDING|EXECUTED|CANCELLED|EXPIRED)$')
    execution_time: Optional[datetime] = None


class SignalQuery(BaseModel):
    """信号查询参数"""
    strategy_instance_id: Optional[str] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    signal_type: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class SignalStats(BaseModel):
    """信号统计"""
    total_signals: int
    buy_signals: int
    sell_signals: int
    avg_confidence: Optional[Decimal]
    unique_symbols: int
    unique_timeframes: int


@router.post("/", response_model=SignalResponse)
async def create_signal(
    signal_data: SignalCreate,
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """创建新的交易信号"""
    try:
        signal_dict = await signal_repo.create_signal(
            strategy_instance_id=signal_data.strategy_instance_id,
            signal_type=signal_data.signal_type,
            symbol=signal_data.symbol,
            timeframe=signal_data.timeframe,
            price=signal_data.price,
            quantity=signal_data.quantity,
            confidence=signal_data.confidence,
            metadata=signal_data.metadata,
            signal_time=signal_data.signal_time
        )

        return SignalResponse(**signal_dict)

    except Exception as e:
        log.error(f"Error creating signal: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: str,
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """获取单个信号详情"""
    signal_dict = await signal_repo.get_by_id(signal_id)

    if not signal_dict:
        raise HTTPException(status_code=404, detail="Signal not found")

    return SignalResponse(**signal_dict)


@router.get("/", response_model=List[SignalResponse])
async def list_signals(
    strategy_instance_id: Optional[str] = Query(None, description="策略实例ID"),
    symbol: Optional[str] = Query(None, description="交易标的"),
    timeframe: Optional[str] = Query(None, description="时间周期"),
    signal_type: Optional[str] = Query(None, description="信号类型"),
    status: Optional[str] = Query(None, description="信号状态"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(100, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """获取信号列表"""
    if strategy_instance_id:
        signals = await signal_repo.list_by_instance(
            strategy_instance_id=strategy_instance_id,
            timeframe=timeframe,
            symbol=symbol,
            signal_type=signal_type,
            status=status,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
    else:
        signals = await signal_repo.get_latest_signals(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )

    return [SignalResponse(**signal) for signal in signals]


@router.put("/{signal_id}/status", response_model=dict)
async def update_signal_status(
    signal_id: str,
    update_data: SignalUpdate,
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """更新信号状态"""
    success = await signal_repo.update_signal_status(
        signal_id=signal_id,
        status=update_data.status,
        execution_time=update_data.execution_time
    )

    if not success:
        raise HTTPException(status_code=404, detail="Signal not found or update failed")

    return {"message": "Signal status updated successfully", "signal_id": signal_id}


@router.get("/symbol/{symbol}/timeframe/{timeframe}", response_model=List[SignalResponse])
async def get_signals_by_symbol_timeframe(
    symbol: str,
    timeframe: str,
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    signal_types: Optional[List[str]] = Query(None, description="信号类型列表"),
    limit: int = Query(100, le=1000, description="返回数量限制"),
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """根据交易标的和时间周期获取信号"""
    signals = await signal_repo.list_by_symbol_and_timeframe(
        symbol=symbol,
        timeframe=timeframe,
        start_time=start_time,
        end_time=end_time,
        signal_types=signal_types,
        limit=limit
    )

    return [SignalResponse(**signal) for signal in signals]


@router.get("/stats/{strategy_instance_id}", response_model=SignalStats)
async def get_signal_performance_stats(
    strategy_instance_id: str,
    start_date: Optional[datetime] = Query(None, description="统计开始日期"),
    end_date: Optional[datetime] = Query(None, description="统计结束日期"),
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """获取策略实例的信号绩效统计"""
    stats_dict = await signal_repo.get_performance_stats(
        strategy_instance_id=strategy_instance_id,
        start_date=start_date,
        end_date=end_date
    )

    return SignalStats(**stats_dict)


@router.get("/latest/all", response_model=List[SignalResponse])
async def get_latest_signals(
    limit: int = Query(20, le=100, description="返回数量限制"),
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """获取最新信号"""
    signals = await signal_repo.get_latest_signals(limit=limit)
    return [SignalResponse(**signal) for signal in signals]


@router.post("/maintenance/expire-old", response_model=dict)
async def expire_old_signals(
    expiry_hours: int = Query(24, description="过期小时数"),
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """批量过期旧信号"""
    # 需要管理员权限
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")

    expired_count = await signal_repo.batch_update_expired_signals(expiry_hours=expiry_hours)
    return {
        "message": f"Expired {expired_count} old signals",
        "expired_count": expired_count
    }


@router.delete("/maintenance/cleanup", response_model=dict)
async def cleanup_old_signals(
    days_old: int = Query(30, description="清理天数"),
    current_user: dict = Depends(get_current_active_user),
    signal_repo: StrategySignalRepository = Depends(get_strategy_signal_repo)
):
    """清理旧信号数据"""
    # 需要管理员权限
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")

    deleted_count = await signal_repo.delete_old_signals(days_old=days_old)
    return {
        "message": f"Deleted {deleted_count} old signals",
        "deleted_count": deleted_count
    }