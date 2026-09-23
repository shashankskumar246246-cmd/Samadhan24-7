-- ============================================================================
-- SAMADHAN 24/7 (JHARKHAND INNOVATION PORTAL) - PRODUCTION DATABASE SCHEMA
-- PostgreSQL DDL for Automatic University + Industry Matching & Collaboration
-- ============================================================================

-- Drop tables if they already exist (in reverse dependency order)
DROP TABLE IF EXISTS collaborations CASCADE;
DROP TABLE IF EXISTS industry_matches CASCADE;
DROP TABLE IF EXISTS university_matches CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS problems CASCADE;
DROP TABLE IF EXISTS industries CASCADE;
DROP TABLE IF EXISTS universities CASCADE;

-- ----------------------------------------------------------------------------
-- 1. UNIVERSITIES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE universities (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    departments TEXT[] NOT NULL,
    academic_domains TEXT[] NOT NULL,
    faculty_expertise TEXT[] NOT NULL,
    research_areas TEXT[] NOT NULL,
    facilities TEXT[] NOT NULL,
    innovation_capabilities TEXT[] NOT NULL,
    previous_projects TEXT[] NOT NULL,
    student_skills TEXT[] NOT NULL,
    description TEXT,
    website VARCHAR(255),
    contact_email VARCHAR(255),
    emoji VARCHAR(10) DEFAULT '🎓',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_universities_district ON universities(district);

-- ----------------------------------------------------------------------------
-- 2. INDUSTRIES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE industries (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(255) NOT NULL,
    technologies TEXT[] NOT NULL,
    skills TEXT[] NOT NULL,
    products_services TEXT[] NOT NULL,
    csr_focus_areas TEXT[] NOT NULL,
    funding_capability VARCHAR(50) DEFAULT 'High', -- 'High', 'Medium', 'Grant-Only'
    mentoring_capability BOOLEAN DEFAULT TRUE,
    prototyping_capability BOOLEAN DEFAULT TRUE,
    deployment_capability BOOLEAN DEFAULT TRUE,
    location VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    previous_collaborations TEXT[] NOT NULL,
    description TEXT,
    contact_email VARCHAR(255),
    icon VARCHAR(10) DEFAULT '🏢',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_industries_sector ON industries(sector);
CREATE INDEX idx_industries_district ON industries(district);

-- ----------------------------------------------------------------------------
-- 3. PROBLEMS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE problems (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100),
    location VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) DEFAULT 'Jharkhand',
    village VARCHAR(100),
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    accuracy NUMERIC(8, 2),
    formatted_address TEXT,
    location_source VARCHAR(50),
    location_confirmed BOOLEAN DEFAULT FALSE,
    location_timestamp VARCHAR(50),
    -- Location Verification / Mismatch Detection (Feature 1)
    current_latitude NUMERIC(10, 6),
    current_longitude NUMERIC(10, 6),
    distance_km NUMERIC(8, 2),
    location_status VARCHAR(50) DEFAULT 'verified', -- 'verified', 'low_concern', 'moderate_concern', 'mismatch', 'unverified'
    suspicion_score NUMERIC(5, 2) DEFAULT 0.0,
    verification_status VARCHAR(50) DEFAULT 'Verified', -- 'Verified', 'Needs Verification', 'Under Review'
    -- Duplicate Report Detection & Community Support (Feature 2)
    duplicate_score NUMERIC(5, 2) DEFAULT 0.0,
    duplicate_of_report_id VARCHAR(64),
    duplicate_status VARCHAR(50) DEFAULT 'Original', -- 'Original', 'Reported Anyway', 'Duplicate Supported'
    support_count INT DEFAULT 1,
    priority VARCHAR(50) NOT NULL DEFAULT 'Medium', -- 'High', 'Medium', 'Low'
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',   -- 'Pending', 'In Progress', 'Solved'
    required_skills TEXT[] DEFAULT '{}',
    required_academic_domains TEXT[] DEFAULT '{}',
    required_technology TEXT[] DEFAULT '{}',
    required_resources TEXT[] DEFAULT '{}',
    estimated_impact VARCHAR(255),
    submitted_by VARCHAR(255),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_problems_category ON problems(category);
CREATE INDEX idx_problems_district ON problems(district);
CREATE INDEX idx_problems_priority ON problems(priority);
CREATE INDEX idx_problems_location_status ON problems(location_status);
CREATE INDEX idx_problems_verification ON problems(verification_status);

-- ----------------------------------------------------------------------------
-- 4. UNIVERSITY MATCHES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE university_matches (
    id SERIAL PRIMARY KEY,
    problem_id VARCHAR(64) NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    match_score NUMERIC(5, 2) NOT NULL, -- e.g. 94.50%
    domain_score NUMERIC(5, 2) NOT NULL,
    skill_score NUMERIC(5, 2) NOT NULL,
    research_score NUMERIC(5, 2) NOT NULL,
    location_score NUMERIC(5, 2) NOT NULL,
    facility_score NUMERIC(5, 2) NOT NULL,
    project_score NUMERIC(5, 2) NOT NULL,
    matching_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'Recommended', -- 'Recommended', 'Interested', 'Accepted', 'Declined'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, university_id)
);

CREATE INDEX idx_uni_matches_problem ON university_matches(problem_id);
CREATE INDEX idx_uni_matches_score ON university_matches(match_score DESC);

-- ----------------------------------------------------------------------------
-- 5. INDUSTRY MATCHES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE industry_matches (
    id SERIAL PRIMARY KEY,
    problem_id VARCHAR(64) NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    industry_id VARCHAR(64) NOT NULL REFERENCES industries(id) ON DELETE CASCADE,
    match_score NUMERIC(5, 2) NOT NULL,
    technology_score NUMERIC(5, 2) NOT NULL,
    domain_score NUMERIC(5, 2) NOT NULL,
    csr_score NUMERIC(5, 2) NOT NULL,
    resource_score NUMERIC(5, 2) NOT NULL,
    location_score NUMERIC(5, 2) NOT NULL,
    experience_score NUMERIC(5, 2) NOT NULL,
    matching_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'Recommended', -- 'Recommended', 'Interested', 'Accepted', 'Declined'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, industry_id)
);

CREATE INDEX idx_ind_matches_problem ON industry_matches(problem_id);
CREATE INDEX idx_ind_matches_score ON industry_matches(match_score DESC);

-- ----------------------------------------------------------------------------
-- 6. COLLABORATIONS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE collaborations (
    id VARCHAR(64) PRIMARY KEY,
    problem_id VARCHAR(64) NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    university_id VARCHAR(64) REFERENCES universities(id) ON DELETE SET NULL,
    industry_id VARCHAR(64) REFERENCES industries(id) ON DELETE SET NULL,
    project_title VARCHAR(255) NOT NULL,
    scope_summary TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Interested',
    -- Lifecycle stages:
    -- 'Recommended' -> 'Interested' -> 'Accepted' -> 'In Collaboration' -> 'Prototype' -> 'Testing' -> 'Deployed' -> 'Completed'
    progress_percentage INT DEFAULT 15,
    lead_organization VARCHAR(255),
    budget_inr NUMERIC(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collaborations_problem ON collaborations(problem_id);
CREATE INDEX idx_collaborations_status ON collaborations(status);

-- ----------------------------------------------------------------------------
-- 7. NOTIFICATIONS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    recipient_type VARCHAR(50) NOT NULL, -- 'University', 'Industry', 'Admin', 'Citizen'
    recipient_id VARCHAR(64),
    problem_id VARCHAR(64) REFERENCES problems(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_recipient ON notifications(recipient_type, recipient_id);
