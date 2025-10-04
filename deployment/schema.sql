-- deployment/schema.sql
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    company VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    source VARCHAR(100),
    engagement_score INTEGER,
    category VARCHAR(50),
    status VARCHAR(50) DEFAULT 'new',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    status VARCHAR(50),
    target_audience JSONB,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    campaign_id INTEGER,
    agent_id VARCHAR(100),
    interaction_type VARCHAR(50),
    content TEXT,
    outcome VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS long_term_memory (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(255),
    entity_type VARCHAR(50),
    memory_type VARCHAR(50),
    data JSONB,
    importance_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    accessed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_category ON leads(category);
CREATE INDEX idx_interactions_lead_id ON interactions(lead_id);
CREATE INDEX idx_memory_entity ON long_term_memory(entity_id, entity_type);