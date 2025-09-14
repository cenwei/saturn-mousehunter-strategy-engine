"""
Service Dependencies
服务依赖注入
"""
from functools import lru_cache

from infrastructure.db.base_dao import AsyncDAO
from infrastructure.config.app_config import get_app_config
from infrastructure.repositories import (
    StrategyDefinitionRepo, StrategyVersionRepo, StrategyInstanceRepo,
    TradingSignalRepo, SignalQueueConfigRepo, SignalQueueItemRepo,
    StrategyPoolRepo, StrategyPoolMemberRepo,
    BacktestConfigRepo, BacktestExecutionRepo
)
from application.services.strategy_definition_service import StrategyDefinitionService
from application.services.trading_signal_service import TradingSignalService


@lru_cache()
def get_dao() -> AsyncDAO:
    """获取数据库访问对象"""
    config = get_app_config()
    return AsyncDAO(config.database_url)


def get_strategy_definition_repo() -> StrategyDefinitionRepo:
    """获取策略定义Repository"""
    dao = get_dao()
    return StrategyDefinitionRepo(dao)


def get_strategy_version_repo() -> StrategyVersionRepo:
    """获取策略版本Repository"""
    dao = get_dao()
    return StrategyVersionRepo(dao)


def get_strategy_instance_repo() -> StrategyInstanceRepo:
    """获取策略实例Repository"""
    dao = get_dao()
    return StrategyInstanceRepo(dao)


def get_trading_signal_repo() -> TradingSignalRepo:
    """获取交易信号Repository"""
    dao = get_dao()
    return TradingSignalRepo(dao)


def get_signal_queue_config_repo() -> SignalQueueConfigRepo:
    """获取信号队列配置Repository"""
    dao = get_dao()
    return SignalQueueConfigRepo(dao)


def get_signal_queue_item_repo() -> SignalQueueItemRepo:
    """获取信号队列项Repository"""
    dao = get_dao()
    return SignalQueueItemRepo(dao)


def get_strategy_pool_repo() -> StrategyPoolRepo:
    """获取策略池Repository"""
    dao = get_dao()
    return StrategyPoolRepo(dao)


def get_strategy_pool_member_repo() -> StrategyPoolMemberRepo:
    """获取策略池成员Repository"""
    dao = get_dao()
    return StrategyPoolMemberRepo(dao)


def get_backtest_config_repo() -> BacktestConfigRepo:
    """获取回测配置Repository"""
    dao = get_dao()
    return BacktestConfigRepo(dao)


def get_backtest_execution_repo() -> BacktestExecutionRepo:
    """获取回测执行Repository"""
    dao = get_dao()
    return BacktestExecutionRepo(dao)


def get_strategy_definition_service() -> StrategyDefinitionService:
    """获取策略定义服务"""
    strategy_repo = get_strategy_definition_repo()
    return StrategyDefinitionService(strategy_repo)


def get_trading_signal_service() -> TradingSignalService:
    """获取交易信号服务"""
    signal_repo = get_trading_signal_repo()
    queue_config_repo = get_signal_queue_config_repo()
    queue_item_repo = get_signal_queue_item_repo()
    return TradingSignalService(signal_repo, queue_config_repo, queue_item_repo)