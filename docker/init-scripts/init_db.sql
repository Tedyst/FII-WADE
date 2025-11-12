-- Initialize WADE Vulnerability DDS database schema

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(255) NOT NULL,
    callback_url TEXT,
    connection_type VARCHAR(20) NOT NULL CHECK (connection_type IN ('webhook', 'sse', 'ws')),
    filters JSONB DEFAULT '{}',
    secret VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT valid_callback CHECK (
        (connection_type = 'webhook' AND callback_url IS NOT NULL) OR
        (connection_type IN ('sse', 'ws'))
    )
);

CREATE INDEX idx_subscriptions_topic ON subscriptions(topic);
CREATE INDEX idx_subscriptions_active ON subscriptions(is_active) WHERE is_active = true;
CREATE INDEX idx_subscriptions_expires ON subscriptions(expires_at) WHERE expires_at IS NOT NULL;

-- WebSub subscription tracking
CREATE TABLE IF NOT EXISTS websub_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    callback_url TEXT NOT NULL,
    topic TEXT NOT NULL,
    mode VARCHAR(20) NOT NULL,
    lease_seconds INTEGER,
    secret VARCHAR(255),
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(callback_url, topic)
);

CREATE INDEX idx_websub_topic ON websub_subscriptions(topic);
CREATE INDEX idx_websub_verified ON websub_subscriptions(verified);
