"""
Trading Signal Models
交易信号模型 - 管理策略生成的交易信号
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, validator


class TradingSignalIn(BaseModel):
    """交易信号输入模型"""
    strategy_instance_id: str = Field(..., description="策略实例ID")
    symbol: str = Field(..., description="交易品种")
    market: str = Field(..., description="市场")
    signal_type: str = Field(..., description="信号类型")
    signal_strength: str = Field(..., description="信号强度")
    confidence: Decimal = Field(..., description="置信度", ge=0, le=1)
    signal_price: Optional[Decimal] = Field(None, description="信号价格")
    target_price: Optional[Decimal] = Field(None, description="目标价格")
    stop_loss_price: Optional[Decimal] = Field(None, description="止损价格")
    take_profit_price: Optional[Decimal] = Field(None, description="止盈价格")
    suggested_quantity: Optional[int] = Field(None, description="建议数量")
    position_ratio: Optional[Decimal] = Field(None, description="仓位比例")
    valid_from: datetime = Field(..., description="有效开始时间")
    valid_to: Optional[datetime] = Field(None, description="有效结束时间")
    signal_data: Dict[str, Any] = Field(default_factory=dict, description="信号数据")
    indicators: Dict[str, Any] = Field(default_factory=dict, description="技术指标")
    status: str = Field(default="PENDING", description="状态")
    generated_by: str = Field(..., description="生成者")

    @validator('signal_type')
    def validate_signal_type(cls, v):
        allowed_types = ['BUY', 'SELL', 'HOLD', 'CLOSE_LONG', 'CLOSE_SHORT']
        if v not in allowed_types:
            raise ValueError(f'Signal type must be one of {allowed_types}')
        return v

    @validator('signal_strength')
    def validate_signal_strength(cls, v):
        allowed_strengths = ['WEAK', 'MODERATE', 'STRONG', 'VERY_STRONG']
        if v not in allowed_strengths:
            raise ValueError(f'Signal strength must be one of {allowed_strengths}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['PENDING', 'ACTIVE', 'EXECUTED', 'CANCELLED', 'EXPIRED']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class TradingSignalOut(BaseModel):
    """交易信号输出模型"""
    id: str
    strategy_instance_id: str
    symbol: str
    market: str
    signal_type: str
    signal_strength: str
    confidence: Decimal
    signal_price: Optional[Decimal]
    target_price: Optional[Decimal]
    stop_loss_price: Optional[Decimal]
    take_profit_price: Optional[Decimal]
    suggested_quantity: Optional[int]
    position_ratio: Optional[Decimal]
    valid_from: datetime
    valid_to: Optional[datetime]
    signal_data: Dict[str, Any]
    indicators: Dict[str, Any]
    status: str
    is_executed: bool
    executed_at: Optional[datetime]
    executed_price: Optional[Decimal]
    executed_quantity: Optional[int]
    execution_notes: Optional[str]
    generated_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "TradingSignalOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class TradingSignalUpdate(BaseModel):
    """交易信号更新模型"""
    signal_price: Optional[Decimal] = None
    target_price: Optional[Decimal] = None
    stop_loss_price: Optional[Decimal] = None
    take_profit_price: Optional[Decimal] = None
    suggested_quantity: Optional[int] = None
    position_ratio: Optional[Decimal] = None
    valid_to: Optional[datetime] = None
    signal_data: Optional[Dict[str, Any]] = None
    indicators: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_executed: Optional[bool] = None
    executed_at: Optional[datetime] = None
    executed_price: Optional[Decimal] = None
    executed_quantity: Optional[int] = None
    execution_notes: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['PENDING', 'ACTIVE', 'EXECUTED', 'CANCELLED', 'EXPIRED']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class TradingSignalQuery(BaseModel):
    """交易信号查询模型"""
    strategy_instance_id: Optional[str] = None
    symbol: Optional[str] = None
    market: Optional[str] = None
    signal_type: Optional[str] = None
    signal_strength: Optional[str] = None
    status: Optional[str] = None
    is_executed: Optional[bool] = None
    generated_by: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True