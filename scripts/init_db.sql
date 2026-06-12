-- WorkSphere HR - PostgreSQL Initialization
-- This runs once when the container first starts

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create read-only user for reporting
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'worksphere_readonly') THEN
        CREATE ROLE worksphere_readonly LOGIN PASSWORD 'readonly123';
        GRANT CONNECT ON DATABASE worksphere_hr TO worksphere_readonly;
        GRANT USAGE ON SCHEMA public TO worksphere_readonly;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO worksphere_readonly;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO worksphere_readonly;
    END IF;
END
$$;
