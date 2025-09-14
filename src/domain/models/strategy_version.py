"""
Strategy Version Models
策略版本模型 - 管理策略的不同版本
"""
from datetime import datetime
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, validator


class StrategyVersionIn(BaseModel):
    """策略版本输入模型"""
    strategy_id: str = Field(..., description="策略ID")
    version: str = Field(..., description="版本号")
    version_description: Optional[str] = Field(None, description="版本描述")
    config_changes: Dict[str, Any] = Field(default_factory=dict, description="配置变更")
    param_changes: Dict[str, Any] = Field(default_factory=dict, description="参数变更")
    backtest_results: Optional[Dict[str, Any]] = Field(None, description="回测结果")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="性能指标")
    change_log: Optional[str] = Field(None, description="变更日志")
    is_major_version: bool = Field(default=False, description="是否主版本")
    status: str = Field(default="DRAFT", description="状态")
    is_active: bool = Field(default=False, description="是否激活")
    is_published: bool = Field(default=False, description="是否发布")
    created_by: str = Field(..., description="创建者")

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['DRAFT', 'TESTING', 'APPROVED', 'PUBLISHED', 'DEPRECATED']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class StrategyVersionOut(BaseModel):
    """策略版本输出模型"""
    id: str
    strategy_id: str
    version: str
    version_description: Optional[str]
    config_changes: Dict[str, Any]
    param_changes: Dict[str, Any]
    backtest_results: Optional[Dict[str, Any]]
    performance_metrics: Optional[Dict[str, Any]]
    change_log: Optional[str]
    is_major_version: bool
    status: str
    is_active: bool
    is_published: bool
    published_by: Optional[str]
    published_at: Optional[datetime]
    created_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyVersionOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class StrategyVersionUpdate(BaseModel):
    """策略版本更新模型"""
    version_description: Optional[str] = None
    config_changes: Optional[Dict[str, Any]] = None
    param_changes: Optional[Dict[str, Any]] = None
    backtest_results: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    change_log: Optional[str] = None
    is_major_version: Optional[bool] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['DRAFT', 'TESTING', 'APPROVED', 'PUBLISHED', 'DEPRECATED']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    class Config:
        from_attributes = True


class StrategyVersionQuery(BaseModel):
    """策略版本查询模型"""
    strategy_id: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    is_major_version: Optional[bool] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True