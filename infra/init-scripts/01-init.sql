-- DoganAI Compliance Kit - Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create a log entry
INSERT INTO pg_stat_statements_info (dealloc) VALUES (0);
