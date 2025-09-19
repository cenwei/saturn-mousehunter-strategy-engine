"""
Strategy Signal Repository
策略信号数据访问层
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from infrastructure.db.base_dao import AsyncDAO
from saturn_mousehunter_shared.log.logger import get_logger
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard

log = get_logger(__name__)

TABLE = "mh_strategy_signals"


class StrategySignalRepository:
    """策略信号仓储"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_strategy_signal_create_seconds")
    async def create_signal(
        self,
        strategy_instance_id: str,
        signal_type: str,
        symbol: str,
        timeframe: str,
        price: Optional[Decimal] = None,
        quantity: Optional[int] = None,
        confidence: Optional[Decimal] = None,
        metadata: Optional[Dict[str, Any]] = None,
        signal_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """创建策略信号"""
        signal_id = str(uuid.uuid4())
        signal_time = signal_time or datetime.now()
        metadata = metadata or {}

        query = f"""
        INSERT INTO {TABLE} (
            id, strategy_instance_id, signal_type, symbol, timeframe,
            price, quantity, confidence, metadata, signal_time, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING *
        """

        result = await self.dao.fetch_one(
            query,
            signal_id,
            strategy_instance_id,
            signal_type,
            symbol,
            timeframe,
            price,
            quantity,
            confidence,
            metadata,
            signal_time,
            'PENDING'
        )

        log.info(f"Created signal: {signal_id} for {symbol}")
        return dict(result) if result else {}

    @read_only_guard()
    @measure("db_strategy_signal_get_seconds")
    async def get_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取信号"""
        query = f"SELECT * FROM {TABLE} WHERE id = $1"
        result = await self.dao.fetch_one(query, signal_id)
        return dict(result) if result else None

    @read_only_guard()
    @measure("db_strategy_signal_list_by_instance_seconds")
    async def list_by_instance(
        self,
        strategy_instance_id: str,
        timeframe: Optional[str] = None,
        symbol: Optional[str] = None,
        signal_type: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取策略实例的信号列表"""
        conditions = ["strategy_instance_id = $1"]
        params = [strategy_instance_id]
        param_count = 2

        # 构建条件
        if timeframe:
            conditions.append(f"timeframe = ${param_count}")
            params.append(timeframe)
            param_count += 1

        if symbol:
            conditions.append(f"symbol = ${param_count}")
            params.append(symbol)
            param_count += 1

        if signal_type:
            conditions.append(f"signal_type = ${param_count}")
            params.append(signal_type)
            param_count += 1

        if status:
            conditions.append(f"status = ${param_count}")
            params.append(status)
            param_count += 1

        if start_time:
            conditions.append(f"signal_time >= ${param_count}")
            params.append(start_time)
            param_count += 1

        if end_time:
            conditions.append(f"signal_time <= ${param_count}")
            params.append(end_time)
            param_count += 1

        query = f"""
        SELECT * FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        ORDER BY signal_time DESC
        LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([limit, offset])

        results = await self.dao.fetch_all(query, *params)
        return [dict(row) for row in results]

    @read_only_guard()
    @measure("db_strategy_signal_list_by_symbol_seconds")
    async def list_by_symbol_and_timeframe(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        signal_types: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取特定标的和时间周期的信号"""
        conditions = ["symbol = $1", "timeframe = $2"]
        params = [symbol, timeframe]
        param_count = 3

        if start_time:
            conditions.append(f"signal_time >= ${param_count}")
            params.append(start_time)
            param_count += 1

        if end_time:
            conditions.append(f"signal_time <= ${param_count}")
            params.append(end_time)
            param_count += 1

        if signal_types:
            placeholders = ', '.join([f'${param_count + i}' for i in range(len(signal_types))])
            conditions.append(f"signal_type IN ({placeholders})")
            params.extend(signal_types)
            param_count += len(signal_types)

        query = f"""
        SELECT * FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        ORDER BY signal_time DESC
        LIMIT ${param_count}
        """
        params.append(limit)

        results = await self.dao.fetch_all(query, *params)
        return [dict(row) for row in results]

    @measure("db_strategy_signal_update_status_seconds")
    async def update_signal_status(
        self,
        signal_id: str,
        status: str,
        execution_time: Optional[datetime] = None
    ) -> bool:
        """更新信号状态"""
        if execution_time:
            query = f"""
            UPDATE {TABLE}
            SET status = $2, execution_time = $3
            WHERE id = $1
            """
            result = await self.dao.execute(query, signal_id, status, execution_time)
        else:
            query = f"""
            UPDATE {TABLE}
            SET status = $2
            WHERE id = $1
            """
            result = await self.dao.execute(query, signal_id, status)

        success = result > 0
        if success:
            log.info(f"Updated signal status: {signal_id} -> {status}")
        return success

    @measure("db_strategy_signal_batch_update_seconds")
    async def batch_update_expired_signals(self, expiry_hours: int = 24) -> int:
        """批量更新过期信号"""
        expiry_time = datetime.now() - timedelta(hours=expiry_hours)

        query = f"""
        UPDATE {TABLE}
        SET status = 'EXPIRED'
        WHERE status = 'PENDING' AND signal_time < $1
        """

        result = await self.dao.execute(query, expiry_time)
        if result > 0:
            log.info(f"Updated {result} expired signals")
        return result

    @read_only_guard()
    @measure("db_strategy_signal_get_performance_stats_seconds")
    async def get_performance_stats(
        self,
        strategy_instance_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取信号绩效统计"""
        conditions = ["strategy_instance_id = $1", "status = 'EXECUTED'"]
        params = [strategy_instance_id]
        param_count = 2

        if start_date:
            conditions.append(f"execution_time >= ${param_count}")
            params.append(start_date)
            param_count += 1

        if end_date:
            conditions.append(f"execution_time <= ${param_count}")
            params.append(end_date)
            param_count += 1

        query = f"""
        SELECT
            COUNT(*) as total_signals,
            COUNT(CASE WHEN signal_type IN ('BUY', 'LONG') THEN 1 END) as buy_signals,
            COUNT(CASE WHEN signal_type IN ('SELL', 'SHORT') THEN 1 END) as sell_signals,
            AVG(confidence) as avg_confidence,
            COUNT(DISTINCT symbol) as unique_symbols,
            COUNT(DISTINCT timeframe) as unique_timeframes
        FROM {TABLE}
        WHERE {' AND '.join(conditions)}
        """

        result = await self.dao.fetch_one(query, *params)
        return dict(result) if result else {}

    @read_only_guard()
    @measure("db_strategy_signal_get_latest_seconds")
    async def get_latest_signals(
        self,
        strategy_instance_id: Optional[str] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取最新信号"""
        conditions = []
        params = []
        param_count = 1

        if strategy_instance_id:
            conditions.append(f"strategy_instance_id = ${param_count}")
            params.append(strategy_instance_id)
            param_count += 1

        if symbol:
            conditions.append(f"symbol = ${param_count}")
            params.append(symbol)
            param_count += 1

        if timeframe:
            conditions.append(f"timeframe = ${param_count}")
            params.append(timeframe)
            param_count += 1

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT * FROM {TABLE}
        WHERE {where_clause}
        ORDER BY signal_time DESC
        LIMIT ${param_count}
        """
        params.append(limit)

        results = await self.dao.fetch_all(query, *params)
        return [dict(row) for row in results]

    @measure("db_strategy_signal_delete_old_seconds")
    async def delete_old_signals(self, days_old: int = 30) -> int:
        """删除旧信号数据"""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        query = f"""
        DELETE FROM {TABLE}
        WHERE signal_time < $1 AND status IN ('EXECUTED', 'EXPIRED', 'CANCELLED')
        """

        result = await self.dao.execute(query, cutoff_date)
        if result > 0:
            log.info(f"Deleted {result} old signals")
        return result