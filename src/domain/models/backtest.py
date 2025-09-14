"""
Backtest Models
回测模型 - 回测配置和执行结果
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class BacktestConfigIn(BaseModel):
    """回测配置输入模型"""
    config_name: str = Field(..., description="配置名称")
    strategy_id: str = Field(..., description="策略ID")
    description: Optional[str] = Field(None, description="描述")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    initial_capital: Decimal = Field(..., description="初始资金")
    benchmark: Optional[str] = Field(None, description="基准")
    instruments: List[str] = Field(..., description="交易工具")
    commission_rate: Decimal = Field(default=Decimal("0.001"), description="手续费率")
    slippage: Decimal = Field(default=Decimal("0.0001"), description="滑点")
    max_positions: int = Field(default=10, description="最大持仓数")
    rebalance_frequency: str = Field(default="DAILY", description="再平衡频率")
    risk_free_rate: Decimal = Field(default=Decimal("0.03"), description="无风险利率")
    strategy_params: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
    market_data_source: str = Field(default="DEFAULT", description="市场数据源")
    backtest_config: Dict[str, Any] = Field(default_factory=dict, description="回测配置")
    is_active: bool = Field(default=True, description="是否激活")
    created_by: str = Field(..., description="创建者")

    @validator('rebalance_frequency')
    def validate_rebalance_frequency(cls, v):
        allowed_freq = ['INTRADAY', 'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']
        if v not in allowed_freq:
            raise ValueError(f'Rebalance frequency must be one of {allowed_freq}')
        return v

    class Config:
        from_attributes = True


class BacktestConfigOut(BaseModel):
    """回测配置输出模型"""
    id: str
    config_name: str
    strategy_id: str
    description: Optional[str]
    start_date: date
    end_date: date
    initial_capital: Decimal
    benchmark: Optional[str]
    instruments: List[str]
    commission_rate: Decimal
    slippage: Decimal
    max_positions: int
    rebalance_frequency: str
    risk_free_rate: Decimal
    strategy_params: Dict[str, Any]
    market_data_source: str
    backtest_config: Dict[str, Any]
    is_active: bool
    execution_count: int
    last_execution_at: Optional[datetime]
    created_by: str
    created_at: datetime
    updated_at: datetime

    # 关联信息
    strategy_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "BacktestConfigOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class BacktestConfigUpdate(BaseModel):
    """回测配置更新模型"""
    config_name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    initial_capital: Optional[Decimal] = None
    benchmark: Optional[str] = None
    instruments: Optional[List[str]] = None
    commission_rate: Optional[Decimal] = None
    slippage: Optional[Decimal] = None
    max_positions: Optional[int] = None
    rebalance_frequency: Optional[str] = None
    risk_free_rate: Optional[Decimal] = None
    strategy_params: Optional[Dict[str, Any]] = None
    market_data_source: Optional[str] = None
    backtest_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @validator('rebalance_frequency')
    def validate_rebalance_frequency(cls, v):
        if v is not None:
            allowed_freq = ['INTRADAY', 'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']
            if v not in allowed_freq:
                raise ValueError(f'Rebalance frequency must be one of {allowed_freq}')
        return v

    class Config:
        from_attributes = True


class BacktestConfigQuery(BaseModel):
    """回测配置查询模型"""
    config_name: Optional[str] = None
    strategy_id: Optional[str] = None
    created_by: Optional[str] = None
    is_active: Optional[bool] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True


class BacktestExecutionIn(BaseModel):
    """回测执行输入模型"""
    config_id: str = Field(..., description="配置ID")
    execution_name: str = Field(..., description="执行名称")
    description: Optional[str] = Field(None, description="描述")
    execution_params: Dict[str, Any] = Field(default_factory=dict, description="执行参数")
    priority: int = Field(default=5, description="优先级")
    started_by: str = Field(..., description="启动者")

    class Config:
        from_attributes = True


class BacktestExecutionOut(BaseModel):
    """回测执行输出模型"""
    id: str
    config_id: str
    execution_name: str
    description: Optional[str]
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    execution_params: Dict[str, Any]
    priority: int

    # 执行信息
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    progress_pct: Decimal

    # 结果统计
    total_return: Optional[Decimal]
    annual_return: Optional[Decimal]
    max_drawdown: Optional[Decimal]
    sharpe_ratio: Optional[Decimal]
    win_rate: Optional[Decimal]
    profit_factor: Optional[Decimal]

    # 详细结果
    performance_metrics: Dict[str, Any]
    trade_summary: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    execution_log: List[Dict[str, Any]]

    started_by: str
    created_at: datetime
    updated_at: datetime

    # 关联信息
    config_name: Optional[str] = None
    strategy_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "BacktestExecutionOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class BacktestExecutionUpdate(BaseModel):
    """回测执行更新模型"""
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress_pct: Optional[Decimal] = None
    total_return: Optional[Decimal] = None
    annual_return: Optional[Decimal] = None
    max_drawdown: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    win_rate: Optional[Decimal] = None
    profit_factor: Optional[Decimal] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    trade_summary: Optional[Dict[str, Any]] = None
    risk_metrics: Optional[Dict[str, Any]] = None
    execution_log: Optional[List[Dict[str, Any]]] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class BacktestExecutionQuery(BaseModel):
    """回测执行查询模型"""
    config_id: Optional[str] = None
    execution_name: Optional[str] = None
    status: Optional[str] = None
    started_by: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True