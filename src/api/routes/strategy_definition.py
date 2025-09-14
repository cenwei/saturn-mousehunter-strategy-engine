"""
Strategy Definition API Routes
策略定义相关API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from saturn_mousehunter_shared.aop.decorators import measure
from saturn_mousehunter_shared.log.logger import get_logger
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_strategy_definition_service
from application.services.strategy_definition_service import StrategyDefinitionService
from domain.models import (
    StrategyDefinitionIn, StrategyDefinitionOut,
    StrategyDefinitionUpdate, StrategyDefinitionQuery
)

log = get_logger(__name__)
router = APIRouter(prefix="/api/v1/strategies", tags=["策略定义"])


@router.post("/", response_model=StrategyDefinitionOut)
@measure("api_strategy_create_seconds")
async def create_strategy(
    strategy_data: StrategyDefinitionIn,
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """创建策略定义"""
    try:
        # 设置创建者
        strategy_data.created_by = current_user["user_id"]

        strategy = await service.create_strategy(strategy_data)
        return strategy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Failed to create strategy: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{strategy_id}", response_model=StrategyDefinitionOut)
@measure("api_strategy_get_seconds")
async def get_strategy(
    strategy_id: str,
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """获取策略定义"""
    strategy = await service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.put("/{strategy_id}", response_model=StrategyDefinitionOut)
@measure("api_strategy_update_seconds")
async def update_strategy(
    strategy_id: str,
    update_data: StrategyDefinitionUpdate,
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """更新策略定义"""
    try:
        strategy = await service.update_strategy(strategy_id, update_data)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return strategy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Failed to update strategy {strategy_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{strategy_id}")
@measure("api_strategy_delete_seconds")
async def delete_strategy(
    strategy_id: str,
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """删除策略定义"""
    success = await service.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return JSONResponse({"message": "Strategy deleted successfully"})


@router.get("/", response_model=List[StrategyDefinitionOut])
@measure("api_strategy_list_seconds")
async def list_strategies(
    strategy_name: Optional[str] = Query(None),
    strategy_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """获取策略定义列表"""
    query_params = StrategyDefinitionQuery(
        strategy_name=strategy_name,
        strategy_type=strategy_type,
        category=category,
        author=author,
        status=status,
        is_active=is_active,
        limit=limit,
        offset=offset
    )

    strategies = await service.list_strategies(query_params)
    return strategies


@router.get("/stats/count")
@measure("api_strategy_count_seconds")
async def count_strategies(
    strategy_name: Optional[str] = Query(None),
    strategy_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """统计策略定义数量"""
    query_params = StrategyDefinitionQuery(
        strategy_name=strategy_name,
        strategy_type=strategy_type,
        category=category,
        author=author,
        status=status,
        is_active=is_active
    )

    count = await service.count_strategies(query_params)
    return {"count": count}


@router.post("/{strategy_id}/approve", response_model=StrategyDefinitionOut)
@measure("api_strategy_approve_seconds")
async def approve_strategy(
    strategy_id: str,
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """审批策略定义"""
    # 检查用户权限（这里简化处理，实际应该检查具体权限）
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    strategy = await service.approve_strategy(strategy_id, current_user["user_id"])
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.get("/stats/popular", response_model=List[StrategyDefinitionOut])
@measure("api_strategy_popular_seconds")
async def get_popular_strategies(
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """获取热门策略"""
    strategies = await service.get_popular_strategies(limit)
    return strategies


@router.post("/{strategy_id}/usage")
@measure("api_strategy_usage_seconds")
async def increment_usage(
    strategy_id: str,
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """增加策略使用次数"""
    success = await service.increment_usage_count(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return JSONResponse({"message": "Usage count incremented"})


@router.get("/search/{keyword}", response_model=List[StrategyDefinitionOut])
@measure("api_strategy_search_seconds")
async def search_strategies(
    keyword: str,
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """搜索策略"""
    strategies = await service.search_strategies(keyword, category)
    return strategies


@router.post("/{strategy_id}/validate-params")
@measure("api_strategy_validate_params_seconds")
async def validate_strategy_params(
    strategy_id: str,
    params: dict,
    current_user: dict = Depends(get_current_user),
    service: StrategyDefinitionService = Depends(get_strategy_definition_service)
):
    """验证策略参数"""
    try:
        is_valid = await service.validate_strategy_params(strategy_id, params)
        return {"valid": is_valid}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))