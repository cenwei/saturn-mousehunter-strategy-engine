"""
Strategy Definition Service
策略定义业务逻辑服务
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.repositories import StrategyDefinitionRepo
from domain.models import (
    StrategyDefinitionIn, StrategyDefinitionOut,
    StrategyDefinitionUpdate, StrategyDefinitionQuery
)

log = get_logger(__name__)


class StrategyDefinitionService:
    """策略定义服务"""

    def __init__(self, strategy_repo: StrategyDefinitionRepo):
        self.strategy_repo = strategy_repo

    @measure("strategy_definition_create_seconds")
    async def create_strategy(self, strategy_data: StrategyDefinitionIn) -> StrategyDefinitionOut:
        """创建策略定义"""
        # 检查策略名称是否已存在
        existing = await self.strategy_repo.get_by_name(strategy_data.strategy_name)
        if existing:
            raise ValueError(f"Strategy name '{strategy_data.strategy_name}' already exists")

        # 验证策略配置
        await self._validate_strategy_config(strategy_data)

        strategy = await self.strategy_repo.create(strategy_data)
        log.info(f"Created strategy definition: {strategy.strategy_name}")
        return strategy

    @measure("strategy_definition_get_seconds")
    async def get_strategy(self, strategy_id: str) -> Optional[StrategyDefinitionOut]:
        """获取策略定义"""
        return await self.strategy_repo.get_by_id(strategy_id)

    @measure("strategy_definition_update_seconds")
    async def update_strategy(self, strategy_id: str, update_data: StrategyDefinitionUpdate) -> Optional[StrategyDefinitionOut]:
        """更新策略定义"""
        # 检查策略是否存在
        existing = await self.strategy_repo.get_by_id(strategy_id)
        if not existing:
            raise ValueError(f"Strategy {strategy_id} not found")

        # 如果更新策略名称，检查是否重复
        if update_data.strategy_name and update_data.strategy_name != existing.strategy_name:
            duplicate = await self.strategy_repo.get_by_name(update_data.strategy_name)
            if duplicate:
                raise ValueError(f"Strategy name '{update_data.strategy_name}' already exists")

        strategy = await self.strategy_repo.update(strategy_id, update_data)
        if strategy:
            log.info(f"Updated strategy definition: {strategy_id}")
        return strategy

    @measure("strategy_definition_delete_seconds")
    async def delete_strategy(self, strategy_id: str) -> bool:
        """删除策略定义（软删除）"""
        # 检查是否有活跃的策略实例
        # 这里应该调用策略实例服务检查，暂时简化处理
        success = await self.strategy_repo.delete(strategy_id)
        if success:
            log.info(f"Deleted strategy definition: {strategy_id}")
        return success

    @measure("strategy_definition_list_seconds")
    async def list_strategies(self, query_params: StrategyDefinitionQuery) -> List[StrategyDefinitionOut]:
        """获取策略定义列表"""
        return await self.strategy_repo.list(query_params)

    @measure("strategy_definition_count_seconds")
    async def count_strategies(self, query_params: StrategyDefinitionQuery) -> int:
        """统计策略定义数量"""
        return await self.strategy_repo.count(query_params)

    @measure("strategy_definition_approve_seconds")
    async def approve_strategy(self, strategy_id: str, approved_by: str) -> Optional[StrategyDefinitionOut]:
        """审批策略定义"""
        strategy = await self.strategy_repo.approve(strategy_id, approved_by)
        if strategy:
            log.info(f"Approved strategy definition: {strategy_id}")
        return strategy

    @measure("strategy_definition_get_popular_seconds")
    async def get_popular_strategies(self, limit: int = 10) -> List[StrategyDefinitionOut]:
        """获取热门策略"""
        return await self.strategy_repo.get_popular_strategies(limit)

    @measure("strategy_definition_increment_usage_seconds")
    async def increment_usage_count(self, strategy_id: str) -> bool:
        """增加策略使用次数"""
        return await self.strategy_repo.increment_usage_count(strategy_id)

    async def _validate_strategy_config(self, strategy_data: StrategyDefinitionIn) -> None:
        """验证策略配置"""
        # 验证支持的市场
        if not strategy_data.supported_markets:
            raise ValueError("Supported markets cannot be empty")

        # 验证时间框架
        if not strategy_data.time_frames:
            raise ValueError("Time frames cannot be empty")

        allowed_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
        for tf in strategy_data.time_frames:
            if tf not in allowed_timeframes:
                raise ValueError(f"Invalid time frame: {tf}")

        # 验证风险参数
        if strategy_data.max_drawdown and strategy_data.max_drawdown > Decimal("0.5"):
            raise ValueError("Max drawdown cannot exceed 50%")

        if strategy_data.stop_loss_pct and strategy_data.stop_loss_pct > Decimal("0.2"):
            raise ValueError("Stop loss cannot exceed 20%")

        # 验证策略参数边界
        if strategy_data.param_bounds:
            await self._validate_param_bounds(strategy_data.default_params, strategy_data.param_bounds)

    async def _validate_param_bounds(self, params: Dict[str, Any], bounds: Dict[str, Any]) -> None:
        """验证参数边界"""
        for param_name, param_value in params.items():
            if param_name in bounds:
                bound = bounds[param_name]
                if 'min' in bound and param_value < bound['min']:
                    raise ValueError(f"Parameter {param_name} below minimum: {param_value} < {bound['min']}")
                if 'max' in bound and param_value > bound['max']:
                    raise ValueError(f"Parameter {param_name} above maximum: {param_value} > {bound['max']}")

    @measure("strategy_definition_validate_params_seconds")
    async def validate_strategy_params(self, strategy_id: str, params: Dict[str, Any]) -> bool:
        """验证策略参数"""
        strategy = await self.strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")

        if strategy.param_bounds:
            await self._validate_param_bounds(params, strategy.param_bounds)

        return True

    @measure("strategy_definition_search_seconds")
    async def search_strategies(self, keyword: str, category: Optional[str] = None) -> List[StrategyDefinitionOut]:
        """搜索策略"""
        query_params = StrategyDefinitionQuery(
            strategy_name=keyword,
            category=category,
            is_active=True,
            limit=50
        )
        return await self.strategy_repo.list(query_params)