-- Saturn MouseHunter 策略引擎数据库表结构

-- 1. 策略定义表
CREATE TABLE md_strategy_definitions (
    id VARCHAR(50) PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    strategy_config JSONB DEFAULT '{}',
    default_params JSONB DEFAULT '{}',
    param_bounds JSONB DEFAULT '{}',
    supported_markets TEXT[],
    supported_instruments TEXT[],
    time_frames TEXT[],
    trading_hours JSONB,
    max_position_size DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    stop_loss_pct DECIMAL(10,4),
    take_profit_pct DECIMAL(10,4),
    author VARCHAR(100) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(20) DEFAULT 'DRAFT',
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 策略版本表
CREATE TABLE md_strategy_versions (
    id VARCHAR(50) PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL REFERENCES md_strategy_definitions(id),
    version VARCHAR(20) NOT NULL,
    version_description TEXT,
    config_changes JSONB DEFAULT '{}',
    param_changes JSONB DEFAULT '{}',
    backtest_results JSONB,
    performance_metrics JSONB,
    change_log TEXT,
    is_major_version BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'DRAFT',
    is_active BOOLEAN DEFAULT false,
    is_published BOOLEAN DEFAULT false,
    published_by VARCHAR(100),
    published_at TIMESTAMPTZ,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(strategy_id, version)
);

-- 3. 策略实例表
CREATE TABLE md_strategy_instances (
    id VARCHAR(50) PRIMARY KEY,
    strategy_version_id VARCHAR(50) NOT NULL REFERENCES md_strategy_versions(id),
    instance_name VARCHAR(100) NOT NULL,
    description TEXT,
    custom_params JSONB DEFAULT '{}',
    market VARCHAR(10) NOT NULL,
    instruments TEXT[],
    time_frame VARCHAR(10) NOT NULL,
    auto_start BOOLEAN DEFAULT false,
    start_time TIME,
    stop_time TIME,
    position_size DECIMAL(10,4) DEFAULT 0.1,
    max_positions INTEGER DEFAULT 10,
    risk_level VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) DEFAULT 'DRAFT',
    is_running BOOLEAN DEFAULT false,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    total_signals INTEGER DEFAULT 0,
    active_positions INTEGER DEFAULT 0,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 交易信号表
CREATE TABLE md_trading_signals (
    id VARCHAR(50) PRIMARY KEY,
    strategy_instance_id VARCHAR(50) NOT NULL REFERENCES md_strategy_instances(id),
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(10) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    signal_strength VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    signal_price DECIMAL(20,6),
    target_price DECIMAL(20,6),
    stop_loss_price DECIMAL(20,6),
    take_profit_price DECIMAL(20,6),
    suggested_quantity INTEGER,
    position_ratio DECIMAL(5,4),
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ,
    signal_data JSONB DEFAULT '{}',
    indicators JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'PENDING',
    is_executed BOOLEAN DEFAULT false,
    executed_at TIMESTAMPTZ,
    executed_price DECIMAL(20,6),
    executed_quantity INTEGER,
    execution_notes TEXT,
    generated_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 信号队列配置表
CREATE TABLE md_signal_queue_configs (
    id VARCHAR(50) PRIMARY KEY,
    queue_name VARCHAR(100) NOT NULL,
    description TEXT,
    max_queue_size INTEGER DEFAULT 1000,
    priority_enabled BOOLEAN DEFAULT true,
    batch_size INTEGER DEFAULT 10,
    processing_interval INTEGER DEFAULT 60,
    retry_attempts INTEGER DEFAULT 3,
    retry_interval INTEGER DEFAULT 30,
    filter_rules JSONB DEFAULT '{}',
    duplicate_check BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    is_running BOOLEAN DEFAULT false,
    total_processed INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_processed_at TIMESTAMPTZ,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. 信号队列项表
CREATE TABLE md_signal_queue_items (
    id VARCHAR(50) PRIMARY KEY,
    queue_id VARCHAR(50) NOT NULL REFERENCES md_signal_queue_configs(id),
    signal_id VARCHAR(50) NOT NULL REFERENCES md_trading_signals(id),
    priority INTEGER DEFAULT 5,
    scheduled_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'PENDING',
    attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. 策略池表
CREATE TABLE md_strategy_pools (
    id VARCHAR(50) PRIMARY KEY,
    pool_name VARCHAR(100) NOT NULL,
    description TEXT,
    pool_type VARCHAR(50) NOT NULL,
    max_strategies INTEGER DEFAULT 50,
    auto_rebalance BOOLEAN DEFAULT false,
    rebalance_frequency VARCHAR(20),
    total_risk_limit DECIMAL(10,4) DEFAULT 1.0,
    single_strategy_limit DECIMAL(10,4) DEFAULT 0.2,
    correlation_limit DECIMAL(10,4) DEFAULT 0.8,
    allocation_method VARCHAR(20) DEFAULT 'EQUAL_WEIGHT',
    custom_weights JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    is_active BOOLEAN DEFAULT true,
    member_count INTEGER DEFAULT 0,
    total_allocation DECIMAL(10,4) DEFAULT 0,
    performance JSONB,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. 策略池成员表
CREATE TABLE md_strategy_pool_members (
    id VARCHAR(50) PRIMARY KEY,
    pool_id VARCHAR(50) NOT NULL REFERENCES md_strategy_pools(id),
    strategy_instance_id VARCHAR(50) NOT NULL REFERENCES md_strategy_instances(id),
    allocation_weight DECIMAL(10,4) DEFAULT 0.1,
    custom_params JSONB DEFAULT '{}',
    risk_weight DECIMAL(10,4) DEFAULT 1.0,
    max_drawdown_limit DECIMAL(10,4),
    auto_execute BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    is_active BOOLEAN DEFAULT true,
    performance JSONB,
    contribution DECIMAL(10,4),
    last_signal_at TIMESTAMPTZ,
    added_by VARCHAR(100) NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(pool_id, strategy_instance_id)
);

-- 9. 回测配置表
CREATE TABLE md_backtest_configs (
    id VARCHAR(50) PRIMARY KEY,
    config_name VARCHAR(100) NOT NULL,
    backtest_type VARCHAR(20) NOT NULL,
    description TEXT,
    strategy_ids TEXT[] NOT NULL,
    strategy_weights JSONB DEFAULT '{}',
    strategy_params JSONB DEFAULT '{}',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    warmup_period INTEGER DEFAULT 252,
    initial_capital DECIMAL(20,6) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    position_sizing_method VARCHAR(20) DEFAULT 'EQUAL_WEIGHT',
    execution_model VARCHAR(20) DEFAULT 'REALISTIC',
    commission_rate DECIMAL(10,6) DEFAULT 0.001,
    slippage_bps DECIMAL(10,2) DEFAULT 5,
    market_impact_model VARCHAR(50),
    rebalance_frequency VARCHAR(20) DEFAULT 'MONTHLY',
    rebalance_threshold DECIMAL(10,4),
    rebalance_tolerance DECIMAL(10,4) DEFAULT 0.05,
    max_position_size DECIMAL(10,4) DEFAULT 0.1,
    max_sector_exposure DECIMAL(10,4),
    stop_loss_pct DECIMAL(10,4),
    max_drawdown_limit DECIMAL(10,4),
    benchmark_type VARCHAR(20),
    benchmark_symbol VARCHAR(20),
    benchmark_weights JSONB,
    calculate_intraday BOOLEAN DEFAULT false,
    include_dividends BOOLEAN DEFAULT true,
    survivorship_bias BOOLEAN DEFAULT false,
    generate_trades BOOLEAN DEFAULT true,
    generate_holdings BOOLEAN DEFAULT true,
    generate_analytics BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'DRAFT',
    version VARCHAR(20) DEFAULT '1.0.0',
    is_template BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. 回测执行表
CREATE TABLE md_backtest_executions (
    id VARCHAR(50) PRIMARY KEY,
    config_id VARCHAR(50) NOT NULL REFERENCES md_backtest_configs(id),
    execution_name VARCHAR(100) NOT NULL,
    description TEXT,
    param_overrides JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 5,
    max_runtime_hours INTEGER DEFAULT 24,
    checkpoint_enabled BOOLEAN DEFAULT true,
    cpu_cores INTEGER DEFAULT 2,
    memory_gb INTEGER DEFAULT 4,
    storage_gb INTEGER DEFAULT 10,
    notification_enabled BOOLEAN DEFAULT true,
    notification_emails TEXT[],
    status VARCHAR(20) DEFAULT 'QUEUED',
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    queued_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_minutes INTEGER,
    processed_days INTEGER DEFAULT 0,
    total_days INTEGER,
    transactions_generated INTEGER DEFAULT 0,
    positions_held INTEGER DEFAULT 0,
    current_date DATE,
    current_nav DECIMAL(20,6),
    current_return DECIMAL(10,4),
    error_message TEXT,
    error_details JSONB,
    cpu_usage_avg DECIMAL(5,2),
    memory_usage_peak DECIMAL(5,2),
    storage_used DECIMAL(5,2),
    started_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_strategy_definitions_status ON md_strategy_definitions(status);
CREATE INDEX idx_strategy_definitions_type ON md_strategy_definitions(strategy_type);
CREATE INDEX idx_strategy_versions_strategy ON md_strategy_versions(strategy_id);
CREATE INDEX idx_strategy_instances_version ON md_strategy_instances(strategy_version_id);
CREATE INDEX idx_trading_signals_instance ON md_trading_signals(strategy_instance_id);
CREATE INDEX idx_trading_signals_symbol_date ON md_trading_signals(symbol, created_at);
CREATE INDEX idx_signal_queue_items_queue ON md_signal_queue_items(queue_id);
CREATE INDEX idx_strategy_pool_members_pool ON md_strategy_pool_members(pool_id);
CREATE INDEX idx_backtest_configs_type ON md_backtest_configs(backtest_type);
CREATE INDEX idx_backtest_executions_config ON md_backtest_executions(config_id);
CREATE INDEX idx_backtest_executions_status ON md_backtest_executions(status);
