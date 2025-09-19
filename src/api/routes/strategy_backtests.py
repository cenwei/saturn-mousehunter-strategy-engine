"""
Strategy Backtest Routes
策略回测API路由
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from api.middleware.auth import get_current_user, get_current_active_user, require_admin
from api.dependencies.services import get_strategy_backtest_repo
from infrastructure.repositories.strategy_backtest_repo import StrategyBacktestRepository
from saturn_mousehunter_shared.log.logger import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/api/v1/backtests", tags=["strategy-backtests"])


# Pydantic Models
class BacktestCreate(BaseModel):
    """创建回测任务请求"""
    backtest_name: str
    strategy_id: str
    version_id: Optional[str] = None
    start_date: date
    end_date: date
    initial_capital: Decimal = Field(default=Decimal('100000.00'), gt=0)
    parameters: Optional[Dict[str, Any]] = None


class BacktestResponse(BaseModel):
    """回测任务响应"""
    id: str
    backtest_name: str
    strategy_id: str
    version_id: Optional[str]
    start_date: date
    end_date: date
    initial_capital: Decimal
    parameters: Optional[Dict[str, Any]]
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_by: str


class BacktestResults(BaseModel):
    """回测结果"""
    id: str
    backtest_id: str
    total_return: Optional[Decimal]
    annualized_return: Optional[Decimal]
    volatility: Optional[Decimal]
    sharpe_ratio: Optional[Decimal]
    max_drawdown: Optional[Decimal]
    win_rate: Optional[Decimal]
    total_trades: Optional[int]
    profitable_trades: Optional[int]
    avg_trade_return: Optional[Decimal]
    detailed_metrics: Optional[Dict[str, Any]]
    equity_curve: Optional[List[Dict[str, Any]]]
    trade_history: Optional[List[Dict[str, Any]]]
    created_at: datetime


class BacktestWithResults(BaseModel):
    """带结果的回测任务"""
    # 回测任务信息
    id: str
    backtest_name: str
    strategy_id: str
    version_id: Optional[str]
    start_date: date
    end_date: date
    initial_capital: Decimal
    parameters: Optional[Dict[str, Any]]
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_by: str

    # 回测结果信息
    total_return: Optional[Decimal]
    annualized_return: Optional[Decimal]
    volatility: Optional[Decimal]
    sharpe_ratio: Optional[Decimal]
    max_drawdown: Optional[Decimal]
    win_rate: Optional[Decimal]
    total_trades: Optional[int]
    profitable_trades: Optional[int]
    avg_trade_return: Optional[Decimal]
    detailed_metrics: Optional[Dict[str, Any]]
    equity_curve: Optional[List[Dict[str, Any]]]
    trade_history: Optional[List[Dict[str, Any]]]


class BacktestStatusUpdate(BaseModel):
    """回测状态更新"""
    status: str = Field(..., regex=r'^(PENDING|RUNNING|COMPLETED|FAILED|CANCELLED)$')
    progress: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None


class PerformanceComparison(BaseModel):
    """绩效对比"""
    backtest_name: str
    start_date: date
    end_date: date
    initial_capital: Decimal
    metric_value: Optional[Decimal]
    total_return: Optional[Decimal]
    annualized_return: Optional[Decimal]
    sharpe_ratio: Optional[Decimal]
    max_drawdown: Optional[Decimal]


@router.post("/", response_model=BacktestResponse)
async def create_backtest(
    backtest_data: BacktestCreate,
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """创建新的回测任务"""
    try:
        # 验证日期范围
        if backtest_data.end_date <= backtest_data.start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")

        backtest_dict = await backtest_repo.create_backtest(
            backtest_name=backtest_data.backtest_name,
            strategy_id=backtest_data.strategy_id,
            version_id=backtest_data.version_id,
            start_date=backtest_data.start_date,
            end_date=backtest_data.end_date,
            initial_capital=backtest_data.initial_capital,
            parameters=backtest_data.parameters,
            created_by=current_user.get("username", "unknown")
        )

        log.info(f"Created backtest: {backtest_dict['id']}")
        return BacktestResponse(**backtest_dict)

    except Exception as e:
        log.error(f"Error creating backtest: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: str,
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """获取回测任务详情"""
    backtest_dict = await backtest_repo.get_by_id(backtest_id)

    if not backtest_dict:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return BacktestResponse(**backtest_dict)


@router.get("/", response_model=List[BacktestResponse])
async def list_backtests(
    strategy_id: Optional[str] = Query(None, description="策略ID"),
    status: Optional[str] = Query(None, description="回测状态"),
    created_by: Optional[str] = Query(None, description="创建者"),
    limit: int = Query(50, le=200, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """获取回测任务列表"""
    backtests = await backtest_repo.list_backtests(
        strategy_id=strategy_id,
        status=status,
        created_by=created_by,
        limit=limit,
        offset=offset
    )

    return [BacktestResponse(**backtest) for backtest in backtests]


@router.put("/{backtest_id}/status", response_model=dict)
async def update_backtest_status(
    backtest_id: str,
    update_data: BacktestStatusUpdate,
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """更新回测任务状态"""
    # 确定时间参数
    started_at = None
    completed_at = None

    if update_data.status == 'RUNNING':
        started_at = datetime.now()
    elif update_data.status in ['COMPLETED', 'FAILED', 'CANCELLED']:
        completed_at = datetime.now()

    success = await backtest_repo.update_backtest_status(
        backtest_id=backtest_id,
        status=update_data.status,
        progress=update_data.progress,
        error_message=update_data.error_message,
        started_at=started_at,
        completed_at=completed_at
    )

    if not success:
        raise HTTPException(status_code=404, detail="Backtest not found or update failed")

    return {"message": "Backtest status updated successfully", "backtest_id": backtest_id}


@router.post("/{backtest_id}/results", response_model=BacktestResults)
async def save_backtest_results(
    backtest_id: str,
    results_data: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """保存回测结果"""
    try:
        results_dict = await backtest_repo.save_backtest_results(
            backtest_id=backtest_id,
            total_return=results_data.get('total_return'),
            annualized_return=results_data.get('annualized_return'),
            volatility=results_data.get('volatility'),
            sharpe_ratio=results_data.get('sharpe_ratio'),
            max_drawdown=results_data.get('max_drawdown'),
            win_rate=results_data.get('win_rate'),
            total_trades=results_data.get('total_trades'),
            profitable_trades=results_data.get('profitable_trades'),
            avg_trade_return=results_data.get('avg_trade_return'),
            detailed_metrics=results_data.get('detailed_metrics'),
            equity_curve=results_data.get('equity_curve'),
            trade_history=results_data.get('trade_history')
        )

        return BacktestResults(**results_dict)

    except Exception as e:
        log.error(f"Error saving backtest results: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{backtest_id}/results", response_model=Optional[BacktestResults])
async def get_backtest_results(
    backtest_id: str,
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """获取回测结果"""
    results_dict = await backtest_repo.get_backtest_results(backtest_id)

    if not results_dict:
        return None

    return BacktestResults(**results_dict)


@router.get("/{backtest_id}/complete", response_model=Optional[BacktestWithResults])
async def get_complete_backtest(
    backtest_id: str,
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """获取完整的回测信息（任务+结果）"""
    complete_dict = await backtest_repo.get_backtest_with_results(backtest_id)

    if not complete_dict:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return BacktestWithResults(**complete_dict)


@router.get("/with-results/list", response_model=List[BacktestWithResults])
async def list_backtests_with_results(
    strategy_id: Optional[str] = Query(None, description="策略ID"),
    status: Optional[str] = Query(None, description="回测状态"),
    limit: int = Query(20, le=100, description="返回数量限制"),
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """获取带结果的回测列表"""
    backtests = await backtest_repo.list_backtests_with_results(
        strategy_id=strategy_id,
        status=status,
        limit=limit
    )

    return [BacktestWithResults(**backtest) for backtest in backtests]


@router.get("/performance/{strategy_id}/comparison", response_model=List[PerformanceComparison])
async def get_performance_comparison(
    strategy_id: str,
    metric: str = Query('total_return', description="对比指标"),
    limit: int = Query(10, le=50, description="返回数量限制"),
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """获取策略历史回测绩效对比"""
    comparisons = await backtest_repo.get_strategy_performance_comparison(
        strategy_id=strategy_id,
        metric=metric,
        limit=limit
    )

    return [PerformanceComparison(**comp) for comp in comparisons]


@router.post("/{backtest_id}/start", response_model=dict)
async def start_backtest(
    backtest_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """启动回测任务"""
    # 更新状态为运行中
    success = await backtest_repo.update_backtest_status(
        backtest_id=backtest_id,
        status='RUNNING',
        progress=0,
        started_at=datetime.now()
    )

    if not success:
        raise HTTPException(status_code=404, detail="Backtest not found")

    # 在实际应用中，这里应该启动异步回测任务
    # background_tasks.add_task(run_backtest_engine, backtest_id)

    return {
        "message": "Backtest started successfully",
        "backtest_id": backtest_id,
        "status": "RUNNING"
    }


@router.post("/{backtest_id}/cancel", response_model=dict)
async def cancel_backtest(
    backtest_id: str,
    current_user: dict = Depends(get_current_active_user),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """取消回测任务"""
    success = await backtest_repo.update_backtest_status(
        backtest_id=backtest_id,
        status='CANCELLED',
        completed_at=datetime.now()
    )

    if not success:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return {
        "message": "Backtest cancelled successfully",
        "backtest_id": backtest_id,
        "status": "CANCELLED"
    }


@router.delete("/{backtest_id}", response_model=dict)
async def delete_backtest(
    backtest_id: str,
    current_user: dict = Depends(require_admin),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """删除回测任务（管理员权限）"""
    success = await backtest_repo.delete_backtest(backtest_id)

    if not success:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return {
        "message": "Backtest deleted successfully",
        "backtest_id": backtest_id
    }


@router.post("/maintenance/cleanup", response_model=dict)
async def cleanup_old_backtests(
    days_old: int = Query(90, description="清理天数"),
    current_user: dict = Depends(require_admin),
    backtest_repo: StrategyBacktestRepository = Depends(get_strategy_backtest_repo)
):
    """清理旧回测数据（管理员权限）"""
    deleted_count = await backtest_repo.cleanup_old_backtests(days_old=days_old)

    return {
        "message": f"Cleaned up {deleted_count} old backtests",
        "deleted_count": deleted_count
    }


# 辅助端点：回测引擎状态
@router.get("/engine/status", response_model=dict)
async def get_backtest_engine_status(
    current_user: dict = Depends(get_current_active_user)
):
    """获取回测引擎状态"""
    # 在实际应用中，这里应该返回回测引擎的实际状态
    return {
        "engine_status": "running",
        "active_backtests": 0,
        "queue_size": 0,
        "max_concurrent": 5,
        "version": "1.0.0"
    }


# 辅助端点：回测模板
@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_backtest_templates(
    current_user: dict = Depends(get_current_active_user)
):
    """获取回测模板"""
    templates = [
        {
            "name": "快速回测",
            "description": "适用于快速验证策略效果",
            "parameters": {
                "commission_rate": 0.0003,
                "slippage": 0.001,
                "benchmark": "000300.SH"
            }
        },
        {
            "name": "详细回测",
            "description": "适用于完整的策略评估",
            "parameters": {
                "commission_rate": 0.0003,
                "slippage": 0.001,
                "benchmark": "000300.SH",
                "enable_sector_analysis": True,
                "enable_risk_metrics": True
            }
        }
    ]

    return templates