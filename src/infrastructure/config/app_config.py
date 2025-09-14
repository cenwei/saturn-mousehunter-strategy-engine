"""
Application Configuration
策略引擎应用配置
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class AppConfig(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "Saturn MouseHunter Strategy Engine"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="STRATEGY_ENVIRONMENT")
    debug: bool = Field(default=False, env="STRATEGY_DEBUG")

    # 服务配置
    host: str = Field(default="0.0.0.0", env="STRATEGY_HOST")
    port: int = Field(default=8002, env="STRATEGY_PORT")

    # 数据库配置
    database_url: str = Field(..., env="STRATEGY_DATABASE_URL")

    # JWT配置（从认证服务获取）
    jwt_secret_key: str = Field(..., env="STRATEGY_JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="STRATEGY_JWT_ALGORITHM")

    # 日志配置
    log_level: str = Field(default="INFO", env="STRATEGY_LOG_LEVEL")
    log_format: str = Field(default="json", env="STRATEGY_LOG_FORMAT")

    # CORS配置
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="STRATEGY_CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="STRATEGY_CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list = Field(default=["*"], env="STRATEGY_CORS_ALLOW_METHODS")
    cors_allow_headers: list = Field(default=["*"], env="STRATEGY_CORS_ALLOW_HEADERS")

    # Redis配置（可选，用于缓存和消息队列）
    redis_url: Optional[str] = Field(None, env="STRATEGY_REDIS_URL")

    # 业务配置
    max_strategies_per_user: int = Field(default=100, env="STRATEGY_MAX_STRATEGIES_PER_USER")
    max_signals_per_strategy: int = Field(default=10000, env="STRATEGY_MAX_SIGNALS_PER_STRATEGY")
    signal_expiry_hours: int = Field(default=24, env="STRATEGY_SIGNAL_EXPIRY_HOURS")

    # 回测配置
    max_backtest_days: int = Field(default=3650, env="STRATEGY_MAX_BACKTEST_DAYS")  # 10年
    max_concurrent_backtests: int = Field(default=5, env="STRATEGY_MAX_CONCURRENT_BACKTESTS")

    # 监控配置
    enable_metrics: bool = Field(default=True, env="STRATEGY_ENABLE_METRICS")
    metrics_port: int = Field(default=9002, env="STRATEGY_METRICS_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_app_config() -> AppConfig:
    """获取应用配置（单例）"""
    return AppConfig()