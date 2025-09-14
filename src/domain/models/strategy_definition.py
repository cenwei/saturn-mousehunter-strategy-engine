"""
Strategy Definition Models
策略定义模型 - 定义策略的基础信息和配置
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class StrategyDefinitionIn(BaseModel):
    """策略定义输入模型"""
    strategy_name: str = Field(..., description="策略名称")
    strategy_type: str = Field(..., description="策略类型")
    category: str = Field(..., description="策略分类")
    description: Optional[str] = Field(None, description="策略描述")
    strategy_config: Dict[str, Any] = Field(default_factory=dict, description="策略配置")
    default_params: Dict[str, Any] = Field(default_factory=dict, description="默认参数")
    param_bounds: Dict[str, Any] = Field(default_factory=dict, description="参数边界")
    supported_markets: List[str] = Field(default_factory=list, description="支持的市场")
    supported_instruments: List[str] = Field(default_factory=list, description="支持的工具")
    time_frames: List[str] = Field(default_factory=list, description="时间框架")
    trading_hours: Optional[Dict[str, Any]] = Field(None, description="交易时间")
    max_position_size: Optional[Decimal] = Field(None, description="最大仓位大小")
    max_drawdown: Optional[Decimal] = Field(None, description="最大回撤")
    stop_loss_pct: Optional[Decimal] = Field(None, description="止损百分比")
    take_profit_pct: Optional[Decimal] = Field(None, description="止盈百分比")
    author: str = Field(..., description="作者")
    version: str = Field(default="1.0.0", description="版本")
    status: str = Field(default="DRAFT", description="状态")
    is_active: bool = Field(default=True, description="是否激活")
    created_by: str = Field(..., description="创建者")

    @validator('strategy_type')
    def validate_strategy_type(cls, v):
        allowed_types = ['MOMENTUM', 'MEAN_REVERSION', 'TREND_FOLLOWING', 'ARBITRAGE', 'MARKET_MAKING', 'STATISTICAL']
        if v not in allowed_types:
            raise ValueError(f'Strategy type must be one of {allowed_types}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'DEPRECATED']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class StrategyDefinitionOut(BaseModel):
    """策略定义输出模型"""
    id: str
    strategy_name: str
    strategy_type: str
    category: str
    description: Optional[str]
    strategy_config: Dict[str, Any]
    default_params: Dict[str, Any]
    param_bounds: Dict[str, Any]
    supported_markets: List[str]
    supported_instruments: List[str]
    time_frames: List[str]
    trading_hours: Optional[Dict[str, Any]]
    max_position_size: Optional[Decimal]
    max_drawdown: Optional[Decimal]
    stop_loss_pct: Optional[Decimal]
    take_profit_pct: Optional[Decimal]
    author: str
    version: str
    status: str
    is_active: bool
    usage_count: int
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyDefinitionOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class StrategyDefinitionUpdate(BaseModel):
    """策略定义更新模型"""
    strategy_name: Optional[str] = None
    strategy_type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    strategy_config: Optional[Dict[str, Any]] = None
    default_params: Optional[Dict[str, Any]] = None
    param_bounds: Optional[Dict[str, Any]] = None
    supported_markets: Optional[List[str]] = None
    supported_instruments: Optional[List[str]] = None
    time_frames: Optional[List[str]] = None
    trading_hours: Optional[Dict[str, Any]] = None
    max_position_size: Optional[Decimal] = None
    max_drawdown: Optional[Decimal] = None
    stop_loss_pct: Optional[Decimal] = None
    take_profit_pct: Optional[Decimal] = None
    author: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('strategy_type')
    def validate_strategy_type(cls, v):
        if v is not None:
            allowed_types = ['MOMENTUM', 'MEAN_REVERSION', 'TREND_FOLLOWING', 'ARBITRAGE', 'MARKET_MAKING', 'STATISTICAL']
            if v not in allowed_types:
                raise ValueError(f'Strategy type must be one of {allowed_types}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'DEPRECATED']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class StrategyDefinitionQuery(BaseModel):
    """策略定义查询模型"""
    strategy_name: Optional[str] = None
    strategy_type: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True