-- Strategy Engine Database Schema
-- Tables with mh_strategy_* prefix

-- 策略定义表
CREATE TABLE IF NOT EXISTS mh_strategy_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_name VARCHAR(255) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL, -- TREND_FOLLOWING, MEAN_REVERSION, ARBITRAGE, etc.
    description TEXT,
    author VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'APPROVED', 'ARCHIVED', 'DEPRECATED')),
    version VARCHAR(20) DEFAULT '1.0.0',
    parameters JSONB DEFAULT '{}', -- 策略参数配置
    code_template TEXT, -- 策略代码模板
    risk_params JSONB DEFAULT '{}', -- 风控参数
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(strategy_name, version)
);

-- 策略版本表
CREATE TABLE IF NOT EXISTS mh_strategy_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID NOT NULL REFERENCES mh_strategy_definitions(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    code TEXT, -- 策略代码
    parameters JSONB DEFAULT '{}',
    changelog TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    UNIQUE(strategy_id, version)
);

-- 策略实例表
CREATE TABLE IF NOT EXISTS mh_strategy_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID NOT NULL REFERENCES mh_strategy_definitions(id) ON DELETE CASCADE,
    version_id UUID REFERENCES mh_strategy_versions(id) ON DELETE SET NULL,
    instance_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'STOPPED' CHECK (status IN ('RUNNING', 'STOPPED', 'PAUSED', 'ERROR')),
    runtime_params JSONB DEFAULT '{}',
    resource_allocation JSONB DEFAULT '{}', -- 资源分配
    last_signal_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    performance_metrics JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    UNIQUE(instance_name)
);

-- 信号管理表
CREATE TABLE IF NOT EXISTS mh_strategy_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_instance_id UUID NOT NULL REFERENCES mh_strategy_instances(id) ON DELETE CASCADE,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('BUY', 'SELL', 'HOLD', 'LONG', 'SHORT', 'CLOSE')),
    symbol VARCHAR(20) NOT NULL, -- 股票代码
    timeframe VARCHAR(10) NOT NULL, -- 时间周期: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
    price DECIMAL(15,4), -- 信号价格
    quantity INTEGER, -- 数量
    confidence DECIMAL(5,4), -- 信号置信度 0-1
    metadata JSONB DEFAULT '{}', -- 信号元数据
    signal_time TIMESTAMP WITH TIME ZONE NOT NULL, -- 信号生成时间
    execution_time TIMESTAMP WITH TIME ZONE, -- 执行时间
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'EXECUTED', 'CANCELLED', 'EXPIRED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_signals_symbol_time (symbol, signal_time),
    INDEX idx_signals_timeframe (timeframe),
    INDEX idx_signals_status (status),
    INDEX idx_signals_instance_time (strategy_instance_id, signal_time)
);

-- 策略池表
CREATE TABLE IF NOT EXISTS mh_strategy_pools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    pool_type VARCHAR(50) DEFAULT 'MIXED', -- MIXED, CONSERVATIVE, AGGRESSIVE, HEDGE
    max_strategies INTEGER DEFAULT 20,
    allocation_method VARCHAR(50) DEFAULT 'EQUAL_WEIGHT', -- EQUAL_WEIGHT, RISK_WEIGHTED, PERFORMANCE_WEIGHTED
    risk_budget DECIMAL(5,4) DEFAULT 0.05, -- 风险预算
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

-- 策略池成员表
CREATE TABLE IF NOT EXISTS mh_strategy_pool_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id UUID NOT NULL REFERENCES mh_strategy_pools(id) ON DELETE CASCADE,
    strategy_instance_id UUID NOT NULL REFERENCES mh_strategy_instances(id) ON DELETE CASCADE,
    weight DECIMAL(5,4) DEFAULT 0.0, -- 权重 0-1
    allocation_capital DECIMAL(15,2), -- 分配资金
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    performance_contribution JSONB DEFAULT '{}',
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    added_by VARCHAR(255),
    UNIQUE(pool_id, strategy_instance_id)
);

-- 回测任务表
CREATE TABLE IF NOT EXISTS mh_strategy_backtests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_name VARCHAR(255) NOT NULL,
    strategy_id UUID NOT NULL REFERENCES mh_strategy_definitions(id) ON DELETE CASCADE,
    version_id UUID REFERENCES mh_strategy_versions(id) ON DELETE SET NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15,2) DEFAULT 100000.00,
    parameters JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    progress INTEGER DEFAULT 0, -- 进度百分比
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255)
);

-- 回测结果表
CREATE TABLE IF NOT EXISTS mh_strategy_backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID NOT NULL REFERENCES mh_strategy_backtests(id) ON DELETE CASCADE,
    total_return DECIMAL(10,4), -- 总收益率
    annualized_return DECIMAL(10,4), -- 年化收益率
    volatility DECIMAL(10,4), -- 波动率
    sharpe_ratio DECIMAL(10,4), -- 夏普比率
    max_drawdown DECIMAL(10,4), -- 最大回撤
    win_rate DECIMAL(5,4), -- 胜率
    total_trades INTEGER, -- 总交易次数
    profitable_trades INTEGER, -- 盈利交易次数
    avg_trade_return DECIMAL(10,4), -- 平均交易收益
    detailed_metrics JSONB DEFAULT '{}', -- 详细指标
    equity_curve JSONB DEFAULT '[]', -- 净值曲线数据
    trade_history JSONB DEFAULT '[]', -- 交易历史
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_strategy_definitions_author ON mh_strategy_definitions(author);
CREATE INDEX IF NOT EXISTS idx_strategy_definitions_type ON mh_strategy_definitions(strategy_type);
CREATE INDEX IF NOT EXISTS idx_strategy_definitions_status ON mh_strategy_definitions(status);
CREATE INDEX IF NOT EXISTS idx_strategy_instances_status ON mh_strategy_instances(status);
CREATE INDEX IF NOT EXISTS idx_strategy_backtests_status ON mh_strategy_backtests(status);
CREATE INDEX IF NOT EXISTS idx_strategy_backtests_dates ON mh_strategy_backtests(start_date, end_date);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_strategy_definitions_updated_at
    BEFORE UPDATE ON mh_strategy_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_strategy_instances_updated_at
    BEFORE UPDATE ON mh_strategy_instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_strategy_pools_updated_at
    BEFORE UPDATE ON mh_strategy_pools
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();