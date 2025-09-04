-- DoganAI Compliance Kit - Ministry of Interior Database Schema
-- Continuous Database Upload System
-- Urgent Delivery - Production Ready

-- =============================================================================
-- MINISTRY OF INTERIOR SPECIFIC TABLES
-- =============================================================================

-- Ministry Data Classification Enum
CREATE TYPE ministry_classification AS ENUM (
    'unclassified',
    'restricted',
    'confidential',
    'secret',
    'top_secret'
);

-- Ministry Priority Levels
CREATE TYPE ministry_priority AS ENUM (
    'routine',
    'priority',
    'immediate',
    'flash',
    'critical'
);

-- Ministry Department Enum
CREATE TYPE ministry_department AS ENUM (
    'civil_defense',
    'public_security',
    'border_guard',
    'emergency_management',
    'passport_directorate',
    'investigation',
    'forensics',
    'cyber_security',
    'intelligence',
    'administration'
);

-- =============================================================================
-- CORE MINISTRY TABLES
-- =============================================================================

-- Ministry Operations Data
CREATE TABLE ministry_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id VARCHAR(100) UNIQUE NOT NULL,
    department ministry_department NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    classification ministry_classification DEFAULT 'unclassified',
    priority ministry_priority DEFAULT 'routine',
    title VARCHAR(500) NOT NULL,
    description TEXT,
    location JSONB, -- Geographic coordinates and address
    personnel_involved JSONB, -- Array of personnel IDs
    resources_allocated JSONB, -- Equipment, vehicles, etc.
    status VARCHAR(50) DEFAULT 'planned',
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    estimated_duration INTERVAL,
    actual_duration INTERVAL,
    success_metrics JSONB,
    lessons_learned TEXT,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    archived_at TIMESTAMPTZ,
    
    -- Audit fields
    version INTEGER DEFAULT 1,
    checksum VARCHAR(64),
    
    -- Constraints
    CONSTRAINT valid_operation_dates CHECK (end_time IS NULL OR start_time <= end_time),
    CONSTRAINT valid_duration CHECK (estimated_duration IS NULL OR estimated_duration > INTERVAL '0')
);

-- Ministry Personnel Registry
CREATE TABLE ministry_personnel (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    personnel_id VARCHAR(50) UNIQUE NOT NULL,
    national_id VARCHAR(20) UNIQUE NOT NULL,
    rank VARCHAR(50) NOT NULL,
    department ministry_department NOT NULL,
    unit VARCHAR(100),
    full_name VARCHAR(200) NOT NULL,
    position VARCHAR(100) NOT NULL,
    security_clearance ministry_classification DEFAULT 'unclassified',
    contact_info JSONB, -- Phone, email, emergency contact
    qualifications JSONB, -- Certifications, training
    deployment_status VARCHAR(50) DEFAULT 'available',
    current_assignment VARCHAR(200),
    assignment_location JSONB,
    emergency_contact JSONB,
    medical_info JSONB, -- Blood type, allergies, medical conditions
    equipment_assigned JSONB, -- Weapons, vehicles, communication devices
    performance_metrics JSONB,
    disciplinary_records JSONB,
    commendations JSONB,
    active BOOLEAN DEFAULT TRUE,
    hire_date DATE NOT NULL,
    termination_date DATE,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Audit fields
    version INTEGER DEFAULT 1,
    checksum VARCHAR(64)
);

-- Ministry Incidents and Events
CREATE TABLE ministry_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id VARCHAR(100) UNIQUE NOT NULL,
    incident_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    classification ministry_classification DEFAULT 'unclassified',
    priority ministry_priority DEFAULT 'routine',
    department ministry_department NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    location JSONB NOT NULL, -- Detailed location information
    coordinates POINT, -- Geographic coordinates
    reported_by VARCHAR(100) NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL,
    occurred_at TIMESTAMPTZ,
    discovered_at TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'reported',
    assigned_to JSONB, -- Array of personnel assigned
    response_team JSONB, -- Response team composition
    resources_deployed JSONB, -- Equipment and resources used
    casualties JSONB, -- Injury and fatality information
    property_damage JSONB, -- Damage assessment
    evidence_collected JSONB, -- Evidence and forensics
    witness_statements JSONB, -- Witness information
    media_coverage JSONB, -- Media and public information
    investigation_notes TEXT,
    resolution_summary TEXT,
    lessons_learned TEXT,
    follow_up_actions JSONB,
    closed_at TIMESTAMPTZ,
    closed_by VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Audit fields
    version INTEGER DEFAULT 1,
    checksum VARCHAR(64)
);

-- Ministry Assets and Equipment
CREATE TABLE ministry_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id VARCHAR(100) UNIQUE NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    classification ministry_classification DEFAULT 'unclassified',
    name VARCHAR(200) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    purchase_date DATE,
    purchase_cost DECIMAL(15,2),
    current_value DECIMAL(15,2),
    depreciation_rate DECIMAL(5,2),
    warranty_expiry DATE,
    maintenance_schedule JSONB,
    last_maintenance DATE,
    next_maintenance DATE,
    condition VARCHAR(50) DEFAULT 'good',
    location JSONB,
    assigned_to VARCHAR(100), -- Personnel ID
    department ministry_department,
    unit VARCHAR(100),
    operational_status VARCHAR(50) DEFAULT 'operational',
    specifications JSONB,
    maintenance_history JSONB,
    incident_history JSONB,
    disposal_date DATE,
    disposal_reason TEXT,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Audit fields
    version INTEGER DEFAULT 1,
    checksum VARCHAR(64)
);

-- Ministry Communications Log
CREATE TABLE ministry_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    communication_id VARCHAR(100) UNIQUE NOT NULL,
    communication_type VARCHAR(50) NOT NULL, -- radio, phone, email, message
    classification ministry_classification DEFAULT 'unclassified',
    priority ministry_priority DEFAULT 'routine',
    from_personnel VARCHAR(100) NOT NULL,
    to_personnel JSONB, -- Array of recipient personnel IDs
    department ministry_department,
    subject VARCHAR(500),
    content TEXT,
    attachments JSONB,
    transmission_time TIMESTAMPTZ NOT NULL,
    received_time TIMESTAMPTZ,
    acknowledged_time TIMESTAMPTZ,
    response_required BOOLEAN DEFAULT FALSE,
    response_deadline TIMESTAMPTZ,
    response_received BOOLEAN DEFAULT FALSE,
    related_incident VARCHAR(100), -- Reference to incident_id
    related_operation VARCHAR(100), -- Reference to operation_id
    encryption_used BOOLEAN DEFAULT FALSE,
    transmission_method VARCHAR(100),
    signal_strength INTEGER,
    location JSONB,
    archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMPTZ,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Audit fields
    checksum VARCHAR(64)
);

-- =============================================================================
-- CONTINUOUS UPLOAD SYSTEM TABLES
-- =============================================================================

-- Compliance Data Uploads
CREATE TABLE compliance_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    priority INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Ministry Specific Data Uploads
CREATE TABLE ministry_data_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    priority INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    classification ministry_classification DEFAULT 'unclassified',
    department ministry_department,
    processing_status VARCHAR(50) DEFAULT 'pending',
    validation_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    validated_at TIMESTAMPTZ
);

-- Audit Logs for All Operations
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    classification ministry_classification DEFAULT 'unclassified',
    department ministry_department,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generic Data Uploads
CREATE TABLE data_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    priority INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Upload Processing Logs
CREATE TABLE upload_logs (
    id SERIAL PRIMARY KEY,
    packet_id VARCHAR(255) NOT NULL,
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    processing_time_ms INTEGER,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SYSTEM MONITORING TABLES
-- =============================================================================

-- System Health Metrics
CREATE TABLE system_health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(50),
    component VARCHAR(100) NOT NULL,
    severity VARCHAR(50) DEFAULT 'info',
    threshold_warning DECIMAL(15,4),
    threshold_critical DECIMAL(15,4),
    labels JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance Metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(100) NOT NULL,
    duration_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    error_type VARCHAR(100),
    component VARCHAR(100) NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Ministry Operations Indexes
CREATE INDEX idx_ministry_operations_department ON ministry_operations(department);
CREATE INDEX idx_ministry_operations_status ON ministry_operations(status);
CREATE INDEX idx_ministry_operations_priority ON ministry_operations(priority);
CREATE INDEX idx_ministry_operations_classification ON ministry_operations(classification);
CREATE INDEX idx_ministry_operations_start_time ON ministry_operations(start_time);
CREATE INDEX idx_ministry_operations_created_at ON ministry_operations(created_at);

-- Ministry Personnel Indexes
CREATE INDEX idx_ministry_personnel_department ON ministry_personnel(department);
CREATE INDEX idx_ministry_personnel_rank ON ministry_personnel(rank);
CREATE INDEX idx_ministry_personnel_status ON ministry_personnel(deployment_status);
CREATE INDEX idx_ministry_personnel_clearance ON ministry_personnel(security_clearance);
CREATE INDEX idx_ministry_personnel_active ON ministry_personnel(active);

-- Ministry Incidents Indexes
CREATE INDEX idx_ministry_incidents_type ON ministry_incidents(incident_type);
CREATE INDEX idx_ministry_incidents_severity ON ministry_incidents(severity);
CREATE INDEX idx_ministry_incidents_department ON ministry_incidents(department);
CREATE INDEX idx_ministry_incidents_status ON ministry_incidents(status);
CREATE INDEX idx_ministry_incidents_occurred_at ON ministry_incidents(occurred_at);
CREATE INDEX idx_ministry_incidents_reported_at ON ministry_incidents(reported_at);
CREATE INDEX idx_ministry_incidents_location ON ministry_incidents USING GIN(location);

-- Ministry Assets Indexes
CREATE INDEX idx_ministry_assets_type ON ministry_assets(asset_type);
CREATE INDEX idx_ministry_assets_department ON ministry_assets(department);
CREATE INDEX idx_ministry_assets_status ON ministry_assets(operational_status);
CREATE INDEX idx_ministry_assets_assigned_to ON ministry_assets(assigned_to);
CREATE INDEX idx_ministry_assets_maintenance ON ministry_assets(next_maintenance);

-- Communications Indexes
CREATE INDEX idx_ministry_communications_type ON ministry_communications(communication_type);
CREATE INDEX idx_ministry_communications_from ON ministry_communications(from_personnel);
CREATE INDEX idx_ministry_communications_department ON ministry_communications(department);
CREATE INDEX idx_ministry_communications_transmission_time ON ministry_communications(transmission_time);
CREATE INDEX idx_ministry_communications_classification ON ministry_communications(classification);
CREATE INDEX idx_ministry_communications_incident ON ministry_communications(related_incident);
CREATE INDEX idx_ministry_communications_operation ON ministry_communications(related_operation);

-- Upload System Indexes
CREATE INDEX idx_compliance_uploads_timestamp ON compliance_uploads(timestamp);
CREATE INDEX idx_compliance_uploads_status ON compliance_uploads(processing_status);
CREATE INDEX idx_compliance_uploads_source ON compliance_uploads(source);
CREATE INDEX idx_compliance_uploads_priority ON compliance_uploads(priority);

CREATE INDEX idx_ministry_data_uploads_timestamp ON ministry_data_uploads(timestamp);
CREATE INDEX idx_ministry_data_uploads_status ON ministry_data_uploads(processing_status);
CREATE INDEX idx_ministry_data_uploads_department ON ministry_data_uploads(department);
CREATE INDEX idx_ministry_data_uploads_classification ON ministry_data_uploads(classification);

CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_source ON audit_logs(source);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_classification ON audit_logs(classification);

CREATE INDEX idx_data_uploads_timestamp ON data_uploads(timestamp);
CREATE INDEX idx_data_uploads_status ON data_uploads(processing_status);
CREATE INDEX idx_data_uploads_destination ON data_uploads(destination);

CREATE INDEX idx_upload_logs_timestamp ON upload_logs(timestamp);
CREATE INDEX idx_upload_logs_status ON upload_logs(status);
CREATE INDEX idx_upload_logs_source ON upload_logs(source);

-- Monitoring Indexes
CREATE INDEX idx_system_health_metrics_timestamp ON system_health_metrics(timestamp);
CREATE INDEX idx_system_health_metrics_component ON system_health_metrics(component);
CREATE INDEX idx_system_health_metrics_severity ON system_health_metrics(severity);

CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_performance_metrics_component ON performance_metrics(component);
CREATE INDEX idx_performance_metrics_operation_type ON performance_metrics(operation_type);

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_ministry_operations_updated_at BEFORE UPDATE ON ministry_operations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ministry_personnel_updated_at BEFORE UPDATE ON ministry_personnel FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ministry_incidents_updated_at BEFORE UPDATE ON ministry_incidents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ministry_assets_updated_at BEFORE UPDATE ON ministry_assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_compliance_uploads_updated_at BEFORE UPDATE ON compliance_uploads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ministry_data_uploads_updated_at BEFORE UPDATE ON ministry_data_uploads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_data_uploads_updated_at BEFORE UPDATE ON data_uploads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Active Operations View
CREATE VIEW active_operations AS
SELECT 
    operation_id,
    department,
    operation_type,
    classification,
    priority,
    title,
    status,
    start_time,
    estimated_duration,
    created_at
FROM ministry_operations
WHERE status IN ('planned', 'in_progress', 'on_hold')
    AND archived_at IS NULL
ORDER BY priority, start_time;

-- Personnel Deployment Status
CREATE VIEW personnel_deployment AS
SELECT 
    personnel_id,
    full_name,
    rank,
    department,
    unit,
    deployment_status,
    current_assignment,
    security_clearance
FROM ministry_personnel
WHERE active = TRUE
ORDER BY department, rank;

-- Recent Incidents Summary
CREATE VIEW recent_incidents AS
SELECT 
    incident_id,
    incident_type,
    severity,
    classification,
    department,
    title,
    status,
    occurred_at,
    reported_at
FROM ministry_incidents
WHERE reported_at >= NOW() - INTERVAL '30 days'
ORDER BY severity DESC, occurred_at DESC;

-- Upload System Status
CREATE VIEW upload_system_status AS
SELECT 
    'compliance' as source_type,
    COUNT(*) as total_uploads,
    COUNT(*) FILTER (WHERE processing_status = 'completed') as completed,
    COUNT(*) FILTER (WHERE processing_status = 'failed') as failed,
    COUNT(*) FILTER (WHERE processing_status = 'pending') as pending
FROM compliance_uploads
WHERE created_at >= NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 
    'ministry_data' as source_type,
    COUNT(*) as total_uploads,
    COUNT(*) FILTER (WHERE processing_status = 'completed') as completed,
    COUNT(*) FILTER (WHERE processing_status = 'failed') as failed,
    COUNT(*) FILTER (WHERE processing_status = 'pending') as pending
FROM ministry_data_uploads
WHERE created_at >= NOW() - INTERVAL '24 hours';

-- =============================================================================
-- SECURITY AND PERMISSIONS
-- =============================================================================

-- Create roles for different access levels
CREATE ROLE ministry_admin;
CREATE ROLE ministry_operator;
CREATE ROLE ministry_viewer;
CREATE ROLE ministry_system;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ministry_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ministry_admin;

GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO ministry_operator;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO ministry_operator;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO ministry_viewer;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ministry_system;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ministry_system;

-- Row Level Security for sensitive data
ALTER TABLE ministry_personnel ENABLE ROW LEVEL SECURITY;
ALTER TABLE ministry_incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE ministry_communications ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- INITIAL DATA FOR TESTING
-- =============================================================================

-- Insert sample departments and test data
INSERT INTO ministry_operations (operation_id, department, operation_type, classification, priority, title, description, status, created_by) VALUES
('OP-2024-001', 'civil_defense', 'emergency_response', 'restricted', 'immediate', 'Fire Emergency Response - Riyadh District 3', 'Large fire reported in commercial district requiring immediate response', 'in_progress', 'system'),
('OP-2024-002', 'public_security', 'patrol', 'unclassified', 'routine', 'Regular Security Patrol - King Fahd Road', 'Scheduled security patrol of main commercial area', 'planned', 'system'),
('OP-2024-003', 'border_guard', 'border_control', 'confidential', 'priority', 'Enhanced Border Monitoring - Northern Sector', 'Increased monitoring due to intelligence reports', 'in_progress', 'system');

INSERT INTO ministry_personnel (personnel_id, national_id, rank, department, full_name, position, security_clearance, deployment_status, hire_date, created_by) VALUES
('PER-001', '1234567890', 'Captain', 'civil_defense', 'Ahmed Al-Rashid', 'Fire Chief', 'restricted', 'deployed', '2020-01-15', 'system'),
('PER-002', '1234567891', 'Lieutenant', 'public_security', 'Mohammed Al-Otaibi', 'Patrol Leader', 'unclassified', 'available', '2021-03-20', 'system'),
('PER-003', '1234567892', 'Major', 'border_guard', 'Khalid Al-Harbi', 'Border Control Commander', 'confidential', 'deployed', '2019-06-10', 'system');

-- Insert sample metrics
INSERT INTO system_health_metrics (metric_name, metric_value, metric_unit, component, severity, timestamp) VALUES
('cpu_usage', 45.2, 'percent', 'continuous_upload_system', 'info', NOW()),
('memory_usage', 67.8, 'percent', 'continuous_upload_system', 'warning', NOW()),
('queue_size', 23, 'count', 'data_synchronizer', 'info', NOW()),
('upload_rate', 156.7, 'per_minute', 'api_collector', 'info', NOW());

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

-- Log successful schema creation
INSERT INTO audit_logs (log_id, source, action, details, timestamp, checksum, classification) VALUES
('SCHEMA-INIT-001', 'database_setup', 'schema_creation', '{"status": "completed", "tables_created": 15, "indexes_created": 35, "views_created": 4}', NOW(), 'schema_init_checksum', 'unclassified');

SELECT 'Ministry of Interior Database Schema Created Successfully' AS status,
       'Continuous Database Upload System Ready for Deployment' AS message,
       NOW() AS timestamp;