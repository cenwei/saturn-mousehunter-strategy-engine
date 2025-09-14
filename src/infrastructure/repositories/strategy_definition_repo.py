"""
策略引擎 - 策略定义Repository
使用新的表前缀: mh_strategy_definitions
"""
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.db.base_dao import AsyncDAO
from domain.models.strategy_definition import (
    StrategyDefinitionIn, StrategyDefinitionOut,
    StrategyDefinitionUpdate, StrategyDefinitionQuery
)

log = get_logger(__name__)

# 使用新的表前缀
TABLE = "mh_strategy_definitions"


class StrategyDefinitionRepo:
    """策略定义Repository"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_strategy_definition_create_seconds")
    async def create(self, strategy_data: StrategyDefinitionIn) -> StrategyDefinitionOut:
        """创建策略定义"""
        strategy_id = make_ulid()
        now = datetime.now()

        query = f"""
        INSERT INTO {TABLE} (
            id, strategy_name, strategy_type, category, description,
            strategy_config, default_params, param_bounds,
            supported_markets, supported_instruments, time_frames,
            trading_hours, max_position_size, max_drawdown,
            stop_loss_pct, take_profit_pct, author, version,
            status, is_active, usage_count, created_by,
            created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
            $11, $12, $13, $14, $15, $16, $17, $18,
            $19, $20, $21, $22, $23, $24
        ) RETURNING *
        """

        row = await self.dao.fetch_one(
            query,
            strategy_id,
            strategy_data.strategy_name,
            strategy_data.strategy_type,
            strategy_data.category,
            strategy_data.description,
            strategy_data.strategy_config,
            strategy_data.default_params,
            strategy_data.param_bounds,
            strategy_data.supported_markets,
            strategy_data.supported_instruments,
            strategy_data.time_frames,
            strategy_data.trading_hours,
            strategy_data.max_position_size,
            strategy_data.max_drawdown,
            strategy_data.stop_loss_pct,
            strategy_data.take_profit_pct,
            strategy_data.author,
            strategy_data.version,
            strategy_data.status,
            strategy_data.is_active,
            0,  # usage_count初始为0
            strategy_data.created_by,
            now,
            now
        )

        log.info(f"Created strategy definition: {strategy_data.strategy_name}")
        return StrategyDefinitionOut.from_dict(dict(row))

    @read_only_guard()
    @measure("db_strategy_definition_get_seconds")
    async def get_by_id(self, strategy_id: str) -> Optional[StrategyDefinitionOut]:
        """根据ID获取策略定义"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        row = await self.dao.fetch_one(query, strategy_id)

        if row:
            return StrategyDefinitionOut.from_dict(dict(row))
        return None

    @read_only_guard()
    @measure("db_strategy_definition_get_by_name_seconds")
    async def get_by_name(self, strategy_name: str) -> Optional[StrategyDefinitionOut]:
        """根据策略名称获取策略定义"""
        query = f"SELECT * FROM {TABLE} WHERE strategy_name = $1"
        row = await self.dao.fetch_one(query, strategy_name)

        if row:
            return StrategyDefinitionOut.from_dict(dict(row))
        return None

    @measure("db_strategy_definition_update_seconds")
    async def update(self, strategy_id: str, update_data: StrategyDefinitionUpdate) -> Optional[StrategyDefinitionOut]:
        """更新策略定义"""
        set_clauses = []
        params = []
        param_count = 1

        # 动态构建UPDATE语句
        for field, value in update_data.dict(exclude_unset=True).items():
            if field != 'updated_at':
                set_clauses.append(f"{field} = ${param_count}")
                params.append(value)
                param_count += 1

        if not set_clauses:
            return await self.get_by_id(strategy_id)

        # 添加更新时间
        set_clauses.append(f"updated_at = ${param_count}")
        params.append(datetime.now())
        param_count += 1

        # 添加WHERE条件
        params.append(strategy_id)

        query = f"""
        UPDATE {TABLE}
        SET {', '.join(set_clauses)}
        WHERE id = ${param_count}
        RETURNING *
        """

        row = await self.dao.fetch_one(query, *params)
        if row:
            log.info(f"Updated strategy definition: {strategy_id}")
            return StrategyDefinitionOut.from_dict(dict(row))
        return None

    @measure("db_strategy_definition_delete_seconds")
    async def delete(self, strategy_id: str) -> bool:
        """删除策略定义（软删除）"""
        query = f"""
        UPDATE {TABLE}
        SET is_active = false, updated_at = $1
        WHERE id = $2
        """

        result = await self.dao.execute(query, datetime.now(), strategy_id)
        success = result > 0

        if success:
            log.info(f"Deleted strategy definition: {strategy_id}")

        return success

    @read_only_guard()
    @measure("db_strategy_definition_list_seconds")
    async def list(self, query_params: StrategyDefinitionQuery) -> List[StrategyDefinitionOut]:
        """获取策略定义列表"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件
        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.status:
            conditions.append(f"status = ${param_count}")
            params.append(query_params.status)
            param_count += 1

        if query_params.strategy_type:
            conditions.append(f"strategy_type = ${param_count}")
            params.append(query_params.strategy_type)
            param_count += 1

        if query_params.category:
            conditions.append(f"category = ${param_count}")
            params.append(query_params.category)
            param_count += 1

        if query_params.author:
            conditions.append(f"author = ${param_count}")
            params.append(query_params.author)
            param_count += 1

        if query_params.strategy_name:
            conditions.append(f"strategy_name ILIKE ${param_count}")
            params.append(f"%{query_params.strategy_name}%")
            param_count += 1

        # 构建查询
        base_query = f"""
        SELECT * FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        ORDER BY usage_count DESC, created_at DESC
        """

        # 添加分页
        if query_params.limit:
            base_query += f" LIMIT ${param_count}"
            params.append(query_params.limit)
            param_count += 1

        if query_params.offset:
            base_query += f" OFFSET ${param_count}"
            params.append(query_params.offset)

        rows = await self.dao.fetch_all(base_query, *params)
        return [StrategyDefinitionOut.from_dict(dict(row)) for row in rows]

    @measure("db_strategy_definition_approve_seconds")
    async def approve(self, strategy_id: str, approved_by: str) -> Optional[StrategyDefinitionOut]:
        """审批策略定义"""
        query = f"""
        UPDATE {TABLE}
        SET status = 'APPROVED',
            approved_by = $1,
            approved_at = $2,
            updated_at = $2
        WHERE id = $3 AND status = 'PENDING_APPROVAL'
        RETURNING *
        """

        now = datetime.now()
        row = await self.dao.fetch_one(query, approved_by, now, strategy_id)

        if row:
            log.info(f"Approved strategy definition: {strategy_id}")
            return StrategyDefinitionOut.from_dict(dict(row))
        return None

    @measure("db_strategy_definition_increment_usage_seconds")
    async def increment_usage_count(self, strategy_id: str) -> bool:
        """增加使用次数"""
        query = f"""
        UPDATE {TABLE}
        SET usage_count = usage_count + 1,
            updated_at = $1
        WHERE id = $2
        """

        result = await self.dao.execute(query, datetime.now(), strategy_id)
        return result > 0

    @read_only_guard()
    @measure("db_strategy_definition_get_popular_seconds")
    async def get_popular_strategies(self, limit: int = 10) -> List[StrategyDefinitionOut]:
        """获取热门策略"""
        query = f"""
        SELECT * FROM {TABLE}
        WHERE is_active = true AND status = 'APPROVED'
        ORDER BY usage_count DESC, created_at DESC
        LIMIT $1
        """

        rows = await self.dao.fetch_all(query, limit)
        return [StrategyDefinitionOut.from_dict(dict(row)) for row in rows]

    @read_only_guard()
    @measure("db_strategy_definition_count_seconds")
    async def count(self, query_params: StrategyDefinitionQuery) -> int:
        """获取策略定义总数"""
        conditions = ["1=1"]
        params = []
        param_count = 1

        # 构建WHERE条件 (复用list方法的逻辑)
        if query_params.is_active is not None:
            conditions.append(f"is_active = ${param_count}")
            params.append(query_params.is_active)
            param_count += 1

        if query_params.status:
            conditions.append(f"status = ${param_count}")
            params.append(query_params.status)
            param_count += 1

        if query_params.strategy_type:
            conditions.append(f"strategy_type = ${param_count}")
            params.append(query_params.strategy_type)
            param_count += 1

        if query_params.category:
            conditions.append(f"category = ${param_count}")
            params.append(query_params.category)
            param_count += 1

        if query_params.author:
            conditions.append(f"author = ${param_count}")
            params.append(query_params.author)
            param_count += 1

        query = f"""
        SELECT COUNT(*) as total FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        row = await self.dao.fetch_one(query, *params)
        return row['total'] if row else 0