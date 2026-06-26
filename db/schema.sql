-- Postgres DB Schema
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    title TEXT NOT NULL,
    description TEXT,
    seniority TEXT,
    domain_tags TEXT[],
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_requirements (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    skill_id TEXT,
    name TEXT,
    weight FLOAT,
    critical BOOLEAN,
    rationale TEXT,
    aliases JSONB
);

CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    name TEXT,
    email TEXT,
    links JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidate_files (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    job_id INTEGER REFERENCES jobs(id),
    path TEXT,
    mime TEXT,
    lang TEXT,
    status TEXT,
    size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidate_profiles (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    job_id INTEGER REFERENCES jobs(id),
    profile JSONB
);

CREATE TABLE fit_reports (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    candidate_id INTEGER REFERENCES candidates(id),
    report JSONB,
    score FLOAT,
    label TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_nodes (
    id TEXT PRIMARY KEY,
    label TEXT,
    aliases JSONB,
    domains JSONB,
    embedding BYTEA
);

CREATE TABLE audit (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    actor_id INTEGER REFERENCES users(id),
    action TEXT,
    entity TEXT,
    metadata JSONB,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
