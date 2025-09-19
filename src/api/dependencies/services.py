"""
Service Dependencies
服务依赖注入
"""
from functools import lru_cache

from infrastructure.db.base_dao import AsyncDAO
from infrastructure.config.app_config import get_app_config
from infrastructure.repositories.strategy_definition_repo import StrategyDefinitionRepo
from infrastructure.repositories.strategy_signal_repo import StrategySignalRepository
from infrastructure.repositories.strategy_backtest_repo import StrategyBacktestRepository
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


def get_strategy_signal_repo() -> StrategySignalRepository:
    """获取策略信号Repository"""
    dao = get_dao()
    return StrategySignalRepository(dao)


def get_strategy_backtest_repo() -> StrategyBacktestRepository:
    """获取策略回测Repository"""
    dao = get_dao()
    return StrategyBacktestRepository(dao)


def get_strategy_definition_service() -> StrategyDefinitionService:
    """获取策略定义服务"""
    strategy_repo = get_strategy_definition_repo()
    return StrategyDefinitionService(strategy_repo)