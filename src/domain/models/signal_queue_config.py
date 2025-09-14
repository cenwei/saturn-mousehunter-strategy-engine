"""
Signal Queue Config Models
信号队列配置模型 - 管理信号处理队列的配置
"""
from datetime import datetime
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, validator


class SignalQueueConfigIn(BaseModel):
    """信号队列配置输入模型"""
    queue_name: str = Field(..., description="队列名称")
    description: Optional[str] = Field(None, description="队列描述")
    max_queue_size: int = Field(default=1000, description="最大队列大小")
    priority_enabled: bool = Field(default=True, description="是否启用优先级")
    batch_size: int = Field(default=10, description="批处理大小")
    processing_interval: int = Field(default=60, description="处理间隔（秒）")
    retry_attempts: int = Field(default=3, description="重试次数")
    retry_interval: int = Field(default=30, description="重试间隔（秒）")
    filter_rules: Dict[str, Any] = Field(default_factory=dict, description="过滤规则")
    duplicate_check: bool = Field(default=True, description="是否检查重复")
    is_active: bool = Field(default=True, description="是否激活")
    is_running: bool = Field(default=False, description="是否运行中")
    created_by: str = Field(..., description="创建者")

    @validator('max_queue_size', 'batch_size', 'processing_interval', 'retry_attempts', 'retry_interval')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

    class Config:
        from_attributes = True


class SignalQueueConfigOut(BaseModel):
    """信号队列配置输出模型"""
    id: str
    queue_name: str
    description: Optional[str]
    max_queue_size: int
    priority_enabled: bool
    batch_size: int
    processing_interval: int
    retry_attempts: int
    retry_interval: int
    filter_rules: Dict[str, Any]
    duplicate_check: bool
    is_active: bool
    is_running: bool
    total_processed: int
    success_count: int
    error_count: int
    last_processed_at: Optional[datetime]
    created_by: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "SignalQueueConfigOut":
        """从字典创建实例"""
        return cls(**data)

    class Config:
        from_attributes = True


class SignalQueueConfigUpdate(BaseModel):
    """信号队列配置更新模型"""
    queue_name: Optional[str] = None
    description: Optional[str] = None
    max_queue_size: Optional[int] = None
    priority_enabled: Optional[bool] = None
    batch_size: Optional[int] = None
    processing_interval: Optional[int] = None
    retry_attempts: Optional[int] = None
    retry_interval: Optional[int] = None
    filter_rules: Optional[Dict[str, Any]] = None
    duplicate_check: Optional[bool] = None
    is_active: Optional[bool] = None
    is_running: Optional[bool] = None
    total_processed: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    last_processed_at: Optional[datetime] = None

    @validator('max_queue_size', 'batch_size', 'processing_interval', 'retry_attempts', 'retry_interval')
    def validate_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Value must be positive')
        return v

    class Config:
        from_attributes = True


class SignalQueueConfigQuery(BaseModel):
    """信号队列配置查询模型"""
    queue_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_running: Optional[bool] = None
    created_by: Optional[str] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True