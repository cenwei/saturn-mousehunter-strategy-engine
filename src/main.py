"""
Saturn MouseHunter Strategy Engine
策略引擎微服务主启动文件
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from saturn_mousehunter_shared.log.logger import get_logger
from infrastructure.config.app_config import get_app_config
from infrastructure.db.base_dao import AsyncDAO
from api.routes import strategy_definition
from api.routes import strategy_signals, strategy_backtests
from api.dependencies.services import get_dao
from api.middleware.auth import auth_service


# 获取配置和日志
config = get_app_config()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    log.info("Starting Strategy Engine service...")

    # 初始化数据库连接池
    dao = get_dao()
    await dao.initialize()
    log.info("Database connection pool initialized")

    yield

    # 关闭数据库连接池
    await dao.close()
    log.info("Strategy Engine service stopped")
    await auth_service.close()


# 创建FastAPI应用
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="Saturn MouseHunter 策略引擎微服务 - 负责策略定义、版本管理、实例运行、信号生成、池管理和回测系统",
    lifespan=lifespan,
    debug=config.debug
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=config.cors_allow_methods,
    allow_headers=config.cors_allow_headers,
)

# 注册路由
app.include_router(strategy_definition.router)
app.include_router(strategy_signals.router)
app.include_router(strategy_backtests.router)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return JSONResponse({
        "status": "healthy",
        "service": "strategy-engine",
        "version": config.app_version,
        "environment": config.environment
    })

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Saturn MouseHunter Strategy Engine",
        "version": config.app_version,
        "status": "running"
    }

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    log.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # 运行应用
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )