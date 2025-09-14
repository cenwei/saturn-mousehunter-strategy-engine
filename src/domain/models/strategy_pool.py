"""
Strategy Pool Models
策略池模型 - 管理策略池和成员关系
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class StrategyPoolIn(BaseModel):
    """策略池输入模型"""
    pool_name: str = Field(..., description="策略池名称")
    description: Optional[str] = Field(None, description="描述")
    pool_type: str = Field(..., description="策略池类型")
    max_strategies: Optional[int] = Field(None, description="最大策略数")
    total_allocation: Decimal = Field(..., description="总分配比例")
    risk_level: str = Field(..., description="风险等级")
    rebalance_frequency: Optional[str] = Field(None, description="再平衡频率")
    auto_rebalance: bool = Field(default=False, description="自动再平衡")
    pool_config: Dict[str, Any] = Field(default_factory=dict, description="池配置")
    is_active: bool = Field(default=True, description="是否激活")
    created_by: str = Field(..., description="创建者")

    @validator('pool_type')
    def validate_pool_type(cls, v):
        allowed_types = ['DIVERSIFIED', 'SECTOR_FOCUSED', 'RISK_PARITY', 'MOMENTUM', 'VALUE']
        if v not in allowed_types:
            raise ValueError(f'Pool type must be one of {allowed_types}')
        return v

    @validator('risk_level')
    def validate_risk_level(cls, v):
        allowed_levels = ['LOW', 'MEDIUM', 'HIGH', 'ULTRA_HIGH']
        if v not in allowed_levels:
            raise ValueError(f'Risk level must be one of {allowed_levels}')
        return v

    class Config:
        from_attributes = True


class StrategyPoolOut(BaseModel):
    """策略池输出模型"""
    id: str
    pool_name: str
    description: Optional[str]
    pool_type: str
    max_strategies: Optional[int]
    total_allocation: Decimal
    risk_level: str
    rebalance_frequency: Optional[str]
    auto_rebalance: bool
    pool_config: Dict[str, Any]
    is_active: bool
    strategy_count: int
    last_rebalanced_at: Optional[datetime]
    performance_metrics: Optional[Dict[str, Any]]
    created_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyPoolOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class StrategyPoolUpdate(BaseModel):
    """策略池更新模型"""
    pool_name: Optional[str] = None
    description: Optional[str] = None
    pool_type: Optional[str] = None
    max_strategies: Optional[int] = None
    total_allocation: Optional[Decimal] = None
    risk_level: Optional[str] = None
    rebalance_frequency: Optional[str] = None
    auto_rebalance: Optional[bool] = None
    pool_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @validator('pool_type')
    def validate_pool_type(cls, v):
        if v is not None:
            allowed_types = ['DIVERSIFIED', 'SECTOR_FOCUSED', 'RISK_PARITY', 'MOMENTUM', 'VALUE']
            if v not in allowed_types:
                raise ValueError(f'Pool type must be one of {allowed_types}')
        return v

    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v is not None:
            allowed_levels = ['LOW', 'MEDIUM', 'HIGH', 'ULTRA_HIGH']
            if v not in allowed_levels:
                raise ValueError(f'Risk level must be one of {allowed_levels}')
        return v

    class Config:
        from_attributes = True


class StrategyPoolQuery(BaseModel):
    """策略池查询模型"""
    pool_name: Optional[str] = None
    pool_type: Optional[str] = None
    risk_level: Optional[str] = None
    is_active: Optional[bool] = None
    created_by: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True


class StrategyPoolMemberIn(BaseModel):
    """策略池成员输入模型"""
    pool_id: str = Field(..., description="策略池ID")
    strategy_id: str = Field(..., description="策略ID")
    allocation_pct: Decimal = Field(..., description="分配百分比")
    weight: Decimal = Field(default=Decimal("1.0"), description="权重")
    min_allocation: Optional[Decimal] = Field(None, description="最小分配")
    max_allocation: Optional[Decimal] = Field(None, description="最大分配")
    entry_date: Optional[datetime] = Field(None, description="入池日期")
    is_active: bool = Field(default=True, description="是否激活")
    member_config: Dict[str, Any] = Field(default_factory=dict, description="成员配置")
    added_by: str = Field(..., description="添加者")

    class Config:
        from_attributes = True


class StrategyPoolMemberOut(BaseModel):
    """策略池成员输出模型"""
    id: str
    pool_id: str
    strategy_id: str
    allocation_pct: Decimal
    weight: Decimal
    min_allocation: Optional[Decimal]
    max_allocation: Optional[Decimal]
    entry_date: Optional[datetime]
    is_active: bool
    member_config: Dict[str, Any]
    performance_metrics: Optional[Dict[str, Any]]
    added_by: str
    created_at: datetime
    updated_at: datetime

    # 关联信息
    pool_name: Optional[str] = None
    strategy_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyPoolMemberOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class StrategyPoolMemberUpdate(BaseModel):
    """策略池成员更新模型"""
    allocation_pct: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    min_allocation: Optional[Decimal] = None
    max_allocation: Optional[Decimal] = None
    entry_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    member_config: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class StrategyPoolMemberQuery(BaseModel):
    """策略池成员查询模型"""
    pool_id: Optional[str] = None
    strategy_id: Optional[str] = None
    is_active: Optional[bool] = None
    added_by: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True