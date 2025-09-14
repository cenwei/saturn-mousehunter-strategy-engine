"""
Strategy Instance Models
策略实例模型 - 管理策略的具体实例配置和运行状态
"""
from datetime import datetime, time
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class StrategyInstanceIn(BaseModel):
    """策略实例输入模型"""
    strategy_version_id: str = Field(..., description="策略版本ID")
    instance_name: str = Field(..., description="实例名称")
    description: Optional[str] = Field(None, description="实例描述")
    custom_params: Dict[str, Any] = Field(default_factory=dict, description="自定义参数")
    market: str = Field(..., description="市场")
    instruments: List[str] = Field(default_factory=list, description="交易工具")
    time_frame: str = Field(..., description="时间框架")
    auto_start: bool = Field(default=False, description="自动启动")
    start_time: Optional[time] = Field(None, description="开始时间")
    stop_time: Optional[time] = Field(None, description="停止时间")
    position_size: Decimal = Field(default=Decimal("0.1"), description="仓位大小")
    max_positions: int = Field(default=10, description="最大持仓数")
    risk_level: str = Field(default="MEDIUM", description="风险级别")
    status: str = Field(default="DRAFT", description="状态")
    is_running: bool = Field(default=False, description="是否运行中")
    created_by: str = Field(..., description="创建者")

    @validator('market')
    def validate_market(cls, v):
        allowed_markets = ['STOCK', 'FOREX', 'CRYPTO', 'COMMODITY', 'BOND']
        if v not in allowed_markets:
            raise ValueError(f'Market must be one of {allowed_markets}')
        return v

    @validator('time_frame')
    def validate_time_frame(cls, v):
        allowed_frames = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
        if v not in allowed_frames:
            raise ValueError(f'Time frame must be one of {allowed_frames}')
        return v

    @validator('risk_level')
    def validate_risk_level(cls, v):
        allowed_levels = ['LOW', 'MEDIUM', 'HIGH', 'EXTREME']
        if v not in allowed_levels:
            raise ValueError(f'Risk level must be one of {allowed_levels}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['DRAFT', 'READY', 'RUNNING', 'PAUSED', 'STOPPED', 'ERROR']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class StrategyInstanceOut(BaseModel):
    """策略实例输出模型"""
    id: str
    strategy_version_id: str
    instance_name: str
    description: Optional[str]
    custom_params: Dict[str, Any]
    market: str
    instruments: List[str]
    time_frame: str
    auto_start: bool
    start_time: Optional[time]
    stop_time: Optional[time]
    position_size: Decimal
    max_positions: int
    risk_level: str
    status: str
    is_running: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    total_signals: int
    active_positions: int
    created_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyInstanceOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class StrategyInstanceUpdate(BaseModel):
    """策略实例更新模型"""
    instance_name: Optional[str] = None
    description: Optional[str] = None
    custom_params: Optional[Dict[str, Any]] = None
    market: Optional[str] = None
    instruments: Optional[List[str]] = None
    time_frame: Optional[str] = None
    auto_start: Optional[bool] = None
    start_time: Optional[time] = None
    stop_time: Optional[time] = None
    position_size: Optional[Decimal] = None
    max_positions: Optional[int] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    is_running: Optional[bool] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    total_signals: Optional[int] = None
    active_positions: Optional[int] = None

    @validator('market')
    def validate_market(cls, v):
        if v is not None:
            allowed_markets = ['STOCK', 'FOREX', 'CRYPTO', 'COMMODITY', 'BOND']
            if v not in allowed_markets:
                raise ValueError(f'Market must be one of {allowed_markets}')
        return v

    @validator('time_frame')
    def validate_time_frame(cls, v):
        if v is not None:
            allowed_frames = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
            if v not in allowed_frames:
                raise ValueError(f'Time frame must be one of {allowed_frames}')
        return v

    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v is not None:
            allowed_levels = ['LOW', 'MEDIUM', 'HIGH', 'EXTREME']
            if v not in allowed_levels:
                raise ValueError(f'Risk level must be one of {allowed_levels}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['DRAFT', 'READY', 'RUNNING', 'PAUSED', 'STOPPED', 'ERROR']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class StrategyInstanceQuery(BaseModel):
    """策略实例查询模型"""
    strategy_version_id: Optional[str] = None
    instance_name: Optional[str] = None
    market: Optional[str] = None
    time_frame: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    is_running: Optional[bool] = None
    created_by: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True