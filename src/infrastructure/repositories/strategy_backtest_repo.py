"""
Strategy Backtest Repository
策略回测数据访问层
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from infrastructure.db.base_dao import AsyncDAO
from saturn_mousehunter_shared.log.logger import get_logger
from saturn_mousehunter_shared.aop.decorators import measure, read_only_guard

log = get_logger(__name__)

BACKTEST_TABLE = "mh_strategy_backtests"
RESULT_TABLE = "mh_strategy_backtest_results"


class StrategyBacktestRepository:
    """策略回测仓储"""

    def __init__(self, dao: AsyncDAO):
        self.dao = dao

    @measure("db_strategy_backtest_create_seconds")
    async def create_backtest(
        self,
        backtest_name: str,
        strategy_id: str,
        version_id: Optional[str],
        start_date: date,
        end_date: date,
        initial_capital: Decimal = Decimal('100000.00'),
        parameters: Optional[Dict[str, Any]] = None,
        created_by: str = 'system'
    ) -> Dict[str, Any]:
        """创建回测任务"""
        backtest_id = str(uuid.uuid4())
        parameters = parameters or {}

        query = f"""
        INSERT INTO {BACKTEST_TABLE} (
            id, backtest_name, strategy_id, version_id, start_date, end_date,
            initial_capital, parameters, status, progress, created_by
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING *
        """

        result = await self.dao.fetch_one(
            query,
            backtest_id,
            backtest_name,
            strategy_id,
            version_id,
            start_date,
            end_date,
            initial_capital,
            parameters,
            'PENDING',
            0,
            created_by
        )

        log.info(f"Created backtest: {backtest_id}")
        return dict(result) if result else {}

    @read_only_guard()
    @measure("db_strategy_backtest_get_seconds")
    async def get_by_id(self, backtest_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取回测任务"""
        query = f"SELECT * FROM {BACKTEST_TABLE} WHERE id = $1"
        result = await self.dao.fetch_one(query, backtest_id)
        return dict(result) if result else None

    @read_only_guard()
    @measure("db_strategy_backtest_list_seconds")
    async def list_backtests(
        self,
        strategy_id: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取回测任务列表"""
        conditions = []
        params = []
        param_count = 1

        if strategy_id:
            conditions.append(f"strategy_id = ${param_count}")
            params.append(strategy_id)
            param_count += 1

        if status:
            conditions.append(f"status = ${param_count}")
            params.append(status)
            param_count += 1

        if created_by:
            conditions.append(f"created_by = ${param_count}")
            params.append(created_by)
            param_count += 1

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT * FROM {BACKTEST_TABLE}
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([limit, offset])

        results = await self.dao.fetch_all(query, *params)
        return [dict(row) for row in results]

    @measure("db_strategy_backtest_update_status_seconds")
    async def update_backtest_status(
        self,
        backtest_id: str,
        status: str,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> bool:
        """更新回测任务状态"""
        set_clauses = ["status = $2"]
        params = [backtest_id, status]
        param_count = 3

        if progress is not None:
            set_clauses.append(f"progress = ${param_count}")
            params.append(progress)
            param_count += 1

        if error_message is not None:
            set_clauses.append(f"error_message = ${param_count}")
            params.append(error_message)
            param_count += 1

        if started_at is not None:
            set_clauses.append(f"started_at = ${param_count}")
            params.append(started_at)
            param_count += 1

        if completed_at is not None:
            set_clauses.append(f"completed_at = ${param_count}")
            params.append(completed_at)
            param_count += 1

        query = f"""
        UPDATE {BACKTEST_TABLE}
        SET {', '.join(set_clauses)}
        WHERE id = $1
        """

        result = await self.dao.execute(query, *params)
        success = result > 0
        if success:
            log.info(f"Updated backtest status: {backtest_id} -> {status}")
        return success

    @measure("db_strategy_backtest_save_results_seconds")
    async def save_backtest_results(
        self,
        backtest_id: str,
        total_return: Optional[Decimal] = None,
        annualized_return: Optional[Decimal] = None,
        volatility: Optional[Decimal] = None,
        sharpe_ratio: Optional[Decimal] = None,
        max_drawdown: Optional[Decimal] = None,
        win_rate: Optional[Decimal] = None,
        total_trades: Optional[int] = None,
        profitable_trades: Optional[int] = None,
        avg_trade_return: Optional[Decimal] = None,
        detailed_metrics: Optional[Dict[str, Any]] = None,
        equity_curve: Optional[List[Dict[str, Any]]] = None,
        trade_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """保存回测结果"""
        result_id = str(uuid.uuid4())
        detailed_metrics = detailed_metrics or {}
        equity_curve = equity_curve or []
        trade_history = trade_history or []

        query = f"""
        INSERT INTO {RESULT_TABLE} (
            id, backtest_id, total_return, annualized_return, volatility,
            sharpe_ratio, max_drawdown, win_rate, total_trades,
            profitable_trades, avg_trade_return, detailed_metrics,
            equity_curve, trade_history
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
        )
        RETURNING *
        """

        result = await self.dao.fetch_one(
            query,
            result_id,
            backtest_id,
            total_return,
            annualized_return,
            volatility,
            sharpe_ratio,
            max_drawdown,
            win_rate,
            total_trades,
            profitable_trades,
            avg_trade_return,
            detailed_metrics,
            equity_curve,
            trade_history
        )

        log.info(f"Saved backtest results: {result_id}")
        return dict(result) if result else {}

    @read_only_guard()
    @measure("db_strategy_backtest_get_results_seconds")
    async def get_backtest_results(self, backtest_id: str) -> Optional[Dict[str, Any]]:
        """获取回测结果"""
        query = f"SELECT * FROM {RESULT_TABLE} WHERE backtest_id = $1"
        result = await self.dao.fetch_one(query, backtest_id)
        return dict(result) if result else None

    @read_only_guard()
    @measure("db_strategy_backtest_get_with_results_seconds")
    async def get_backtest_with_results(self, backtest_id: str) -> Optional[Dict[str, Any]]:
        """获取回测任务和结果的完整信息"""
        query = f"""
        SELECT
            b.*,
            r.total_return, r.annualized_return, r.volatility, r.sharpe_ratio,
            r.max_drawdown, r.win_rate, r.total_trades, r.profitable_trades,
            r.avg_trade_return, r.detailed_metrics, r.equity_curve, r.trade_history
        FROM {BACKTEST_TABLE} b
        LEFT JOIN {RESULT_TABLE} r ON b.id = r.backtest_id
        WHERE b.id = $1
        """

        result = await self.dao.fetch_one(query, backtest_id)
        return dict(result) if result else None

    @read_only_guard()
    @measure("db_strategy_backtest_list_with_results_seconds")
    async def list_backtests_with_results(
        self,
        strategy_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取带结果的回测任务列表"""
        conditions = []
        params = []
        param_count = 1

        if strategy_id:
            conditions.append(f"b.strategy_id = ${param_count}")
            params.append(strategy_id)
            param_count += 1

        if status:
            conditions.append(f"b.status = ${param_count}")
            params.append(status)
            param_count += 1

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT
            b.*,
            r.total_return, r.annualized_return, r.volatility, r.sharpe_ratio,
            r.max_drawdown, r.win_rate, r.total_trades, r.profitable_trades
        FROM {BACKTEST_TABLE} b
        LEFT JOIN {RESULT_TABLE} r ON b.id = r.backtest_id
        WHERE {where_clause}
        ORDER BY b.created_at DESC
        LIMIT ${param_count}
        """
        params.append(limit)

        results = await self.dao.fetch_all(query, *params)
        return [dict(row) for row in results]

    @read_only_guard()
    @measure("db_strategy_backtest_get_performance_comparison_seconds")
    async def get_strategy_performance_comparison(
        self,
        strategy_id: str,
        metric: str = 'total_return',
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取策略的历史回测绩效对比"""
        query = f"""
        SELECT
            b.backtest_name, b.start_date, b.end_date, b.initial_capital,
            r.{metric} as metric_value,
            r.total_return, r.annualized_return, r.sharpe_ratio, r.max_drawdown
        FROM {BACKTEST_TABLE} b
        JOIN {RESULT_TABLE} r ON b.id = r.backtest_id
        WHERE b.strategy_id = $1 AND b.status = 'COMPLETED'
        ORDER BY r.{metric} DESC NULLS LAST
        LIMIT $2
        """

        results = await self.dao.fetch_all(query, strategy_id, limit)
        return [dict(row) for row in results]

    @measure("db_strategy_backtest_delete_seconds")
    async def delete_backtest(self, backtest_id: str) -> bool:
        """删除回测任务（同时删除相关结果）"""
        async with self.dao.transaction() as conn:
            # 先删除结果
            await conn.execute(f"DELETE FROM {RESULT_TABLE} WHERE backtest_id = $1", backtest_id)

            # 再删除任务
            result = await conn.execute(f"DELETE FROM {BACKTEST_TABLE} WHERE id = $1", backtest_id)

            success = result > 0
            if success:
                log.info(f"Deleted backtest: {backtest_id}")
            return success

    @measure("db_strategy_backtest_cleanup_old_seconds")
    async def cleanup_old_backtests(self, days_old: int = 90) -> int:
        """清理旧的回测数据"""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        async with self.dao.transaction() as conn:
            # 获取要删除的回测ID
            old_backtests = await conn.fetch(
                f"SELECT id FROM {BACKTEST_TABLE} WHERE created_at < $1",
                cutoff_date
            )

            backtest_ids = [row['id'] for row in old_backtests]

            if not backtest_ids:
                return 0

            # 删除结果
            placeholders = ', '.join(['$' + str(i+2) for i in range(len(backtest_ids))])
            await conn.execute(
                f"DELETE FROM {RESULT_TABLE} WHERE backtest_id IN ({placeholders})",
                cutoff_date, *backtest_ids
            )

            # 删除任务
            result = await conn.execute(
                f"DELETE FROM {BACKTEST_TABLE} WHERE created_at < $1",
                cutoff_date
            )

            if result > 0:
                log.info(f"Cleaned up {result} old backtests")
            return result