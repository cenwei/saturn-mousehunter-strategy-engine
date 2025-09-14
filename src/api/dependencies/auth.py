"""
Authentication Dependencies
认证相关依赖
"""
import jwt
from datetime import datetime
from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.config.app_config import get_app_config

log = get_logger(__name__)
security = HTTPBearer()


class AuthError(HTTPException):
    """认证错误"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """获取当前用户信息"""
    token = credentials.credentials

    try:
        # 获取配置
        config = get_app_config()

        # 解码JWT令牌
        payload = jwt.decode(
            token,
            config.jwt_secret_key,
            algorithms=[config.jwt_algorithm]
        )

        # 检查过期时间
        exp = payload.get("exp")
        if exp is None:
            raise AuthError("Token has no expiration time")

        if datetime.utcnow().timestamp() > exp:
            raise AuthError("Token has expired")

        # 提取用户信息
        user_id = payload.get("sub")  # subject
        username = payload.get("username")
        user_type = payload.get("user_type")  # admin_user 或 tenant_user
        tenant_id = payload.get("tenant_id")
        permissions = payload.get("permissions", [])

        if not user_id:
            raise AuthError("Invalid token: missing user ID")

        # 构造用户信息
        current_user = {
            "user_id": user_id,
            "username": username,
            "user_type": user_type,
            "tenant_id": tenant_id,
            "permissions": permissions,
            "is_admin": user_type == "admin_user",
            "token": token
        }

        return current_user

    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError as e:
        log.warning(f"Invalid token: {e}")
        raise AuthError("Invalid token")
    except Exception as e:
        log.error(f"Authentication error: {e}")
        raise AuthError("Authentication failed")


async def get_current_admin_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """获取当前管理员用户（需要管理员权限）"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_permissions(required_permissions: list):
    """权限检查装饰器工厂"""
    def permission_checker(
        current_user: Dict = Depends(get_current_user)
    ) -> Dict:
        user_permissions = current_user.get("permissions", [])

        # 管理员拥有所有权限
        if current_user.get("is_admin", False):
            return current_user

        # 检查是否拥有所需权限
        for required_perm in required_permissions:
            if required_perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {required_perm}"
                )

        return current_user

    return permission_checker


def require_tenant_access(current_user: Dict = Depends(get_current_user)) -> Dict:
    """租户访问权限检查"""
    # 管理员可以访问所有租户数据
    if current_user.get("is_admin", False):
        return current_user

    # 租户用户只能访问自己租户的数据
    if not current_user.get("tenant_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenant access"
        )

    return current_user


# 常用权限检查函数
get_strategy_read_user = require_permissions(["strategy:read"])
get_strategy_write_user = require_permissions(["strategy:read", "strategy:write"])
get_signal_read_user = require_permissions(["signal:read"])
get_signal_write_user = require_permissions(["signal:read", "signal:write"])
get_backtest_read_user = require_permissions(["backtest:read"])
get_backtest_write_user = require_permissions(["backtest:read", "backtest:write"])