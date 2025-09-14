"""
Trading Signal Service
交易信号业务逻辑服务
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from saturn_mousehunter_shared.foundation.ids import make_ulid
from saturn_mousehunter_shared.aop.decorators import measure
from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.repositories import TradingSignalRepo, SignalQueueConfigRepo, SignalQueueItemRepo
from domain.models import (
    TradingSignalIn, TradingSignalOut, TradingSignalUpdate, TradingSignalQuery,
    SignalQueueItemIn, SignalQueueItemOut
)

log = get_logger(__name__)


class TradingSignalService:
    """交易信号服务"""

    def __init__(
        self,
        signal_repo: TradingSignalRepo,
        queue_config_repo: SignalQueueConfigRepo,
        queue_item_repo: SignalQueueItemRepo
    ):
        self.signal_repo = signal_repo
        self.queue_config_repo = queue_config_repo
        self.queue_item_repo = queue_item_repo

    @measure("trading_signal_create_seconds")
    async def create_signal(self, signal_data: TradingSignalIn) -> TradingSignalOut:
        """创建交易信号"""
        # 验证信号数据
        await self._validate_signal_data(signal_data)

        # 创建信号
        signal = await self.signal_repo.create(signal_data)

        # 如果配置了队列，自动加入队列
        await self._auto_enqueue_signal(signal)

        log.info(f"Created trading signal: {signal.symbol} {signal.signal_type}")
        return signal

    @measure("trading_signal_get_seconds")
    async def get_signal(self, signal_id: str) -> Optional[TradingSignalOut]:
        """获取交易信号"""
        return await self.signal_repo.get_by_id(signal_id)

    @measure("trading_signal_update_seconds")
    async def update_signal(self, signal_id: str, update_data: TradingSignalUpdate) -> Optional[TradingSignalOut]:
        """更新交易信号"""
        signal = await self.signal_repo.update(signal_id, update_data)
        if signal:
            log.info(f"Updated trading signal: {signal_id}")
        return signal

    @measure("trading_signal_list_seconds")
    async def list_signals(self, query_params: TradingSignalQuery) -> List[TradingSignalOut]:
        """获取交易信号列表"""
        return await self.signal_repo.list(query_params)

    @measure("trading_signal_count_seconds")
    async def count_signals(self, query_params: TradingSignalQuery) -> int:
        """统计交易信号数量"""
        return await self.signal_repo.count(query_params)

    @measure("trading_signal_get_by_strategy_seconds")
    async def get_signals_by_strategy(self, strategy_id: str, limit: int = 100) -> List[TradingSignalOut]:
        """获取策略的交易信号"""
        return await self.signal_repo.get_signals_by_strategy(strategy_id, limit)

    @measure("trading_signal_get_active_seconds")
    async def get_active_signals(self, symbol: Optional[str] = None) -> List[TradingSignalOut]:
        """获取活跃的交易信号"""
        return await self.signal_repo.get_active_signals(symbol)

    @measure("trading_signal_execute_seconds")
    async def execute_signal(self, signal_id: str, execution_price: Decimal, execution_time: datetime) -> bool:
        """执行交易信号"""
        # 更新信号状态为已执行
        update_data = TradingSignalUpdate(
            status='EXECUTED',
            execution_price=execution_price,
            executed_at=execution_time
        )

        signal = await self.signal_repo.update(signal_id, update_data)
        if signal:
            log.info(f"Executed trading signal: {signal_id} at {execution_price}")
            return True
        return False

    @measure("trading_signal_cancel_seconds")
    async def cancel_signal(self, signal_id: str, reason: str) -> bool:
        """取消交易信号"""
        update_data = TradingSignalUpdate(
            status='CANCELLED',
            cancellation_reason=reason
        )

        signal = await self.signal_repo.update(signal_id, update_data)
        if signal:
            log.info(f"Cancelled trading signal: {signal_id}, reason: {reason}")
            return True
        return False

    @measure("trading_signal_expire_seconds")
    async def expire_old_signals(self, hours_ago: int = 24) -> int:
        """使过期信号失效"""
        cutoff_time = datetime.now() - timedelta(hours=hours_ago)

        # 获取过期的未执行信号
        query_params = TradingSignalQuery(
            status='PENDING',
            limit=1000
        )
        signals = await self.signal_repo.list(query_params)

        expired_count = 0
        for signal in signals:
            if signal.created_at < cutoff_time:
                await self.cancel_signal(signal.id, "Expired")
                expired_count += 1

        log.info(f"Expired {expired_count} old signals")
        return expired_count

    @measure("trading_signal_get_performance_seconds")
    async def get_signal_performance(self, strategy_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """获取信号表现统计"""
        start_date = datetime.now() - timedelta(days=days)

        query_params = TradingSignalQuery(
            strategy_id=strategy_id,
            limit=10000
        )
        signals = await self.signal_repo.list(query_params)

        # 过滤时间范围内的信号
        recent_signals = [s for s in signals if s.created_at >= start_date]

        total_signals = len(recent_signals)
        if total_signals == 0:
            return {
                "total_signals": 0,
                "executed_signals": 0,
                "cancelled_signals": 0,
                "pending_signals": 0,
                "execution_rate": 0,
                "avg_execution_time": 0,
                "win_rate": 0,
                "avg_return": 0
            }

        executed_signals = [s for s in recent_signals if s.status == 'EXECUTED']
        cancelled_signals = [s for s in recent_signals if s.status == 'CANCELLED']
        pending_signals = [s for s in recent_signals if s.status == 'PENDING']

        # 计算执行率
        execution_rate = len(executed_signals) / total_signals if total_signals > 0 else 0

        # 计算平均执行时间
        avg_execution_time = 0
        if executed_signals:
            execution_times = []
            for signal in executed_signals:
                if signal.executed_at:
                    exec_time = (signal.executed_at - signal.created_at).total_seconds() / 60  # 分钟
                    execution_times.append(exec_time)
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # 计算收益相关指标
        profitable_signals = [s for s in executed_signals if s.expected_return and s.expected_return > 0]
        win_rate = len(profitable_signals) / len(executed_signals) if executed_signals else 0

        avg_return = 0
        if executed_signals:
            returns = [s.expected_return for s in executed_signals if s.expected_return]
            avg_return = sum(returns) / len(returns) if returns else 0

        return {
            "total_signals": total_signals,
            "executed_signals": len(executed_signals),
            "cancelled_signals": len(cancelled_signals),
            "pending_signals": len(pending_signals),
            "execution_rate": round(execution_rate, 4),
            "avg_execution_time": round(avg_execution_time, 2),
            "win_rate": round(win_rate, 4),
            "avg_return": float(avg_return)
        }

    async def _validate_signal_data(self, signal_data: TradingSignalIn) -> None:
        """验证信号数据"""
        # 验证价格数据
        if signal_data.target_price and signal_data.target_price <= 0:
            raise ValueError("Target price must be positive")

        if signal_data.stop_loss and signal_data.stop_loss <= 0:
            raise ValueError("Stop loss must be positive")

        if signal_data.take_profit and signal_data.take_profit <= 0:
            raise ValueError("Take profit must be positive")

        # 验证数量
        if signal_data.quantity <= 0:
            raise ValueError("Quantity must be positive")

        # 验证信号强度
        if signal_data.signal_strength < 0 or signal_data.signal_strength > 10:
            raise ValueError("Signal strength must be between 0 and 10")

    async def _auto_enqueue_signal(self, signal: TradingSignalOut) -> None:
        """自动将信号加入队列"""
        try:
            # 查找该策略的队列配置
            queue_configs = await self.queue_config_repo.get_configs_by_strategy(signal.strategy_id)

            for config in queue_configs:
                if config.is_active and config.auto_enqueue:
                    # 创建队列项
                    queue_item_data = SignalQueueItemIn(
                        queue_id=config.id,
                        signal_id=signal.id,
                        priority=signal.priority,
                        scheduled_time=datetime.now(),
                        queue_data={}
                    )

                    await self.queue_item_repo.create(queue_item_data)
                    log.info(f"Auto-enqueued signal {signal.id} to queue {config.id}")

        except Exception as e:
            log.error(f"Failed to auto-enqueue signal {signal.id}: {e}")
            # 不抛出异常，避免影响信号创建