"""
Samadhan 24/7 - Automatic University + Industry Matching Backend REST API Server
Standard library Python HTTP server (Zero pip dependencies required).
Runs on Python 3.10+ / Python 3.14.
"""

import http.server
import json
import os
import re
import sqlite3
import sys
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List

# Ensure current directory is on python path for importing matching_engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matching_engine import (
    analyze_problem,
    calculate_university_match,
    calculate_industry_match,
    detect_category_ai,
    reverse_geocode_coordinates,
    verify_location_consistency,
    detect_duplicate_reports,
    calculate_haversine_distance_km,
    LOCATION_VERIFICATION_CONFIG,
    DUPLICATE_CONFIG
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samadhan.db")


# =============================================================================
# SEED DATA: JHARKHAND UNIVERSITIES & INDUSTRIES
# =============================================================================

SEED_UNIVERSITIES = [
    {
        "id": "bit-mesra",
        "name": "Birla Institute of Technology (BIT), Mesra",
        "location": "Ranchi, Jharkhand",
        "district": "Ranchi",
        "departments": ["Civil & Environmental Engineering", "Computer Science & Engineering", "Space Engineering & Rocketry", "Electrical & Electronics"],
        "academic_domains": ["Civil Engineering", "Environmental Engineering", "Computer Science", "IoT", "Data Analytics"],
        "faculty_expertise": ["Dr. S. K. Verma (Water Quality)", "Dr. A. Mustafi (Edge IoT)", "Dr. N. Patra (Autonomous Systems)"],
        "research_areas": ["IoT Water Quality Telemetry", "Autonomous Drone Sensors", "Plateau Soil Geotechnics", "Clean Energy"],
        "facilities": ["Environmental Pollution Testing Lab", "Advanced VLSI & IoT Systems Center", "High Performance Computing Lab"],
        "innovation_capabilities": ["TIH Technology Innovation Hub", "DST-Supported Incubator", "Patent Facilitation Cell"],
        "previous_projects": ["Subarnarekha River Basin Telemetry Pilot", "Smart Microgrid for Khunti Villages"],
        "student_skills": ["Embedded C/C++", "IoT Hardware Prototyping", "Python / ML", "Civil GIS Mapping"],
        "description": "Premier deemed research university renowned for engineering excellence, IoT sensors, and environmental monitoring.",
        "emoji": "🚀"
    },
    {
        "id": "iit-ism",
        "name": "IIT (Indian School of Mines), Dhanbad",
        "location": "Dhanbad, Jharkhand",
        "district": "Dhanbad",
        "departments": ["Environmental Science & Engineering", "Mining Engineering", "Computer Science & Engineering", "Civil Engineering"],
        "academic_domains": ["Environmental Engineering", "Mining & Mineral Engineering", "Water Resource Management", "Earth Sciences", "AI/ML"],
        "faculty_expertise": ["Prof. G. Udayabhanu (Mine Water Remediation)", "Prof. C. Banerjee (Geophysics)", "Prof. A. K. Pal (Slag Valorization)"],
        "research_areas": ["Mine Acid Water Neutralization", "Heavy Metal Filtration", "Remote Sensing & GIS", "Tailings Stabilization"],
        "facilities": ["Apex Water Chemistry Lab", "Centre for Mining Environment", "GIS & Satellite Imagery Lab"],
        "innovation_capabilities": ["IIT Innovation & Incubation Centre (CIIE)", "TEXMiN Technology Innovation Hub"],
        "previous_projects": ["Dhanbad Coalfield Acid Mine Drainage Treatment", "Drinking Water Supply to Jharia Resettlement Colony"],
        "student_skills": ["Water Quality Testing", "Hydrogeological Modeling", "IoT Telemetry", "Drone Surveying"],
        "description": "Institute of National Importance; international authority in mining eco-restoration, water treatment, and earth sciences.",
        "emoji": "⛏️"
    },
    {
        "id": "nit-jsr",
        "name": "National Institute of Technology (NIT), Jamshedpur",
        "location": "Jamshedpur, Jharkhand",
        "district": "East Singhbhum",
        "departments": ["Civil Engineering", "Metallurgical & Materials Engineering", "Electrical Engineering", "Computer Science"],
        "academic_domains": ["Civil Engineering", "Smart Infrastructure", "Metallurgy", "Clean Energy", "Robotics"],
        "faculty_expertise": ["Dr. S. K. Prasad (Water Infrastructure)", "Dr. R. V. Sharma (Renewables)", "Dr. D. S. Rao (Materials)"],
        "research_areas": ["Sustainable Water Pipelines", "Industrial Waste Recycling", "Solar Microgrids", "Smart Sensors"],
        "facilities": ["Materials Characterization Center", "Fluid Mechanics & Hydraulics Lab", "Smart Grid Demonstration Unit"],
        "innovation_capabilities": ["MSME Incubation Centre", "Maker Space Workshop"],
        "previous_projects": ["Subarnarekha Industrial Effluent Treatment Model", "East Singhbhum Village Solar Pumping Pilot"],
        "student_skills": ["Hydraulic Modeling", "CAD/SolidWorks", "Embedded Systems", "Water Quality Assay"],
        "description": "Institute of National Importance in the industrial capital of Jharkhand, specializing in manufacturing and water utilities.",
        "emoji": "⚡"
    },
    {
        "id": "bau",
        "name": "Birsa Agricultural University (BAU)",
        "location": "Kanke, Ranchi, Jharkhand",
        "district": "Ranchi",
        "departments": ["Soil Science & Agricultural Chemistry", "Agricultural Engineering", "Forestry", "Agronomy"],
        "academic_domains": ["Agriculture Science", "Soil Sciences", "Biotechnology", "Agro-Forestry", "Water Resource Management"],
        "faculty_expertise": ["Dr. B. K. Agarwal (Plateau Soil Fertility)", "Dr. D. N. Singh (Drought Resistant Crops)", "Dr. P. Kaushik (Irrigation)"],
        "research_areas": ["Drought-Resilient Plateau Crops", "Micro-Irrigation Telemetry", "Soil Revitalization", "Bio-Fertilizers"],
        "facilities": ["Central Instrumentation Lab", "Soil Health Testing Vans", "Plateau Experimental Research Farms"],
        "innovation_capabilities": ["Agri-Business Incubator (RABI)", "Krishi Vigyan Kendra (KVK) Network"],
        "previous_projects": ["Deoghar District Drip Irrigation Scheme", "Jharkhand Millets Mission Seed Bank"],
        "student_skills": ["Soil Analysis", "Drip System Assembly", "Crop Diagnostics", "Farmer Field Training"],
        "description": "Pioneering state agricultural university developing climate-resilient plateau crops, soil restoration, and smart irrigation.",
        "emoji": "🌾"
    },
    {
        "id": "aiims-deoghar",
        "name": "All India Institute of Medical Sciences (AIIMS), Deoghar",
        "location": "Deoghar, Jharkhand",
        "district": "Deoghar",
        "departments": ["Community Medicine & Public Health", "Biochemistry & Pathology", "General Medicine", "Pediatrics"],
        "academic_domains": ["Medical & Health Sciences", "Public Health", "Clinical AI", "Epidemiology", "Biotechnology"],
        "faculty_expertise": ["Dr. S. Sengupta (Rural Epidemiology)", "Dr. M. K. Panda (Telemedicine Diagnostics)"],
        "research_areas": ["Remote Diagnostic Screener Systems", "Waterborne Disease Surveillance", "Maternal Nutrition"],
        "facilities": ["Apex Molecular Biology Lab", "Telemedicine Outpost Hub", "Clinical Diagnostics Center"],
        "innovation_capabilities": ["Medical Innovation & Device Testing Cell", "ICMR Research Center"],
        "previous_projects": ["Santhal Pargana Waterborne Fluorosis Screening", "Mobile Primary Diagnostic Units in Dumka"],
        "student_skills": ["Public Health Screening", "Point-of-Care Testing", "Biostatistics", "Clinical Data Analysis"],
        "description": "Apex medical research and healthcare institute serving eastern India, advancing telemedicine and rural health.",
        "emoji": "🏥"
    },
    {
        "id": "iiit-ranchi",
        "name": "Indian Institute of Information Technology (IIIT), Ranchi",
        "location": "Ranchi, Jharkhand",
        "district": "Ranchi",
        "departments": ["Computer Science & Engineering", "Electronics & Communication Engineering"],
        "academic_domains": ["Computer Science / AI", "IoT & Sensor Networks", "Data Analytics", "Cybersecurity", "Embedded Systems"],
        "faculty_expertise": ["Dr. J. K. Roy (Deep Learning)", "Dr. P. Sharma (Edge Computing & IoT)", "Dr. R. Soren (Vernacular NLP)"],
        "research_areas": ["Edge AI Sensor Networks", "Vernacular Language Chatbots for Citizens", "Rural Telemetry Systems"],
        "facilities": ["Nvidia GPU AI Cluster", "IoT & Embedded Prototyping Lab", "Cyber-Physical Systems Lab"],
        "innovation_capabilities": ["T-Hub Innovation Cell", "Open-Source Software Development Center"],
        "previous_projects": ["Jharkhand Citizen Grievance AI Categorizer", "Rural School Offline Digital Learning Tablet App"],
        "student_skills": ["Python / TensorFlow", "React / Web Apps", "ESP32 / Arduino Firmware", "PostgreSQL / Cloud"],
        "description": "Institute of National Importance specializing in edge AI, IoT sensor telemetry, and intelligent citizen systems.",
        "emoji": "💻"
    },
    {
        "id": "cuj",
        "name": "Central University of Jharkhand (CUJ)",
        "location": "Ranchi, Jharkhand",
        "district": "Ranchi",
        "departments": ["Water Engineering & Management", "Energy Engineering", "Environmental Sciences", "Tribal Studies"],
        "academic_domains": ["Water Resource Management", "Environmental Engineering", "Energy Engineering", "Tribal Studies"],
        "faculty_expertise": ["Dr. M. K. Yadav (Hydrology)", "Dr. B. Das (Green Hydrogen)", "Dr. S. K. Mishra (Water Filtration)"],
        "research_areas": ["Fluoride & Arsenic Water Remediation", "Decentralized Solar Water Kiosks", "Indigenous Biodiversity Conservation"],
        "facilities": ["Centre for Water Engineering", "Renewable Energy Research Park", "Nanomaterials Fabrication Lab"],
        "innovation_capabilities": ["University Innovation Cluster", "MoE-Supported Design Innovation Centre"],
        "previous_projects": ["Gumla Low-Cost Drinking Water Filtration Filter Units", "Solar Water Micro-Utility in Khunti"],
        "student_skills": ["Water Quality Testing", "Nanofiltration Assembly", "GIS Watershed Analysis", "Field Surveying"],
        "description": "Central university established by Parliament, leading frontier research in water remediation and community development.",
        "emoji": "🏛️"
    }
]

SEED_INDUSTRIES = [
    {
        "id": "water-management",
        "name": "Water Management & Sanitation Solutions",
        "sector": "Environmental Utilities & Jal Jeevan",
        "technologies": ["IoT Water Sensors", "RO & Nano Filtration", "Solar Powered Pumping", "SCADA Telemetry", "Smart Water Meters"],
        "skills": ["Water Quality Analysis", "Civil Pipeline Engineering", "SCADA Integration", "Community Training"],
        "products_services": ["Community Drinking Water Kiosks", "Water Testing Field Kits", "Solar Desalination Units"],
        "csr_focus_areas": ["Drinking Water Access", "Rural Sanitation", "Groundwater Recharge", "Jal Jeevan Mission Support"],
        "funding_capability": "High",
        "mentoring_capability": True,
        "prototyping_capability": True,
        "deployment_capability": True,
        "location": "Ranchi & Jamshedpur, Jharkhand",
        "district": "Ranchi",
        "previous_collaborations": ["UNICEF Rural Water Access Project", "Jharkhand Drinking Water & Sanitation Dept Pilot"],
        "description": "Premier water utilities partner providing turnkey rural water networks, community filtration kiosks, and IoT telemetry.",
        "icon": "💧"
    },
    {
        "id": "agritech",
        "name": "Agriculture & AgriTech Innovations",
        "sector": "Agri-Business & Automation",
        "technologies": ["Smart Drip Irrigation", "Soil Moisture IoT Sensors", "Solar Cold Storage", "Mobile Advisory Systems"],
        "skills": ["Precision Irrigation", "Sensor Interfacing", "Farming Systems Analysis", "Supply Chain"],
        "products_services": ["Automated Drip Controllers", "Solar Micro Cold Stores", "Soil Health Testing Scanners"],
        "csr_focus_areas": ["Smallholder Farmer Livelihoods", "Water Conservation", "Organic Plateau Agriculture"],
        "funding_capability": "High",
        "mentoring_capability": True,
        "prototyping_capability": True,
        "deployment_capability": True,
        "location": "Ranchi, Jharkhand",
        "district": "Ranchi",
        "previous_collaborations": ["Birsa Agricultural University Field Pilots", "NABARD FPO Solar Pump Integration"],
        "description": "Leading regional AgriTech enterprise deploying IoT drip irrigation, cold chain logistics, and soil revitalization kits.",
        "icon": "🌾"
    },
    {
        "id": "electronics",
        "name": "Electronics & Hardware Design Consortium",
        "sector": "Semiconductor & IoT Hardware",
        "technologies": ["IoT Sensors", "Embedded Microcontrollers (ESP32/STM32)", "Solar Charge Controllers", "LoRaWAN Gateways"],
        "skills": ["PCB Design", "Firmware Engineering", "Hardware Prototyping", "Telemetry SCADA"],
        "products_services": ["Industrial IoT Sensors", "Smart Pre-paid Meters", "Custom Telemetry Circuit Boards"],
        "csr_focus_areas": ["Rural STEM Education", "Digital Infrastructure", "Clean Energy Telemetry"],
        "funding_capability": "Medium",
        "mentoring_capability": True,
        "prototyping_capability": True,
        "deployment_capability": True,
        "location": "Adityapur Industrial Belt, Jamshedpur",
        "district": "East Singhbhum",
        "previous_collaborations": ["NIT Jamshedpur Maker Lab", "Smart City Ranchi Streetlight Telemetry"],
        "description": "Specialized electronics design and rapid hardware manufacturing partner accelerating physical tech prototypes.",
        "icon": "⚡"
    },
    {
        "id": "csr-organizations",
        "name": "Jharkhand CSR Foundation Network",
        "sector": "Social Responsibility & Grants",
        "technologies": ["Impact Tracking Dashboards", "Beneficiary Verification Portals", "Mobile Monitoring"],
        "skills": ["CSR Grant Deployment", "Community Mobilization", "Monitoring & Evaluation", "Regulatory Compliance"],
        "products_services": ["Societal Innovation Seed Grants (Up to 25 Lakhs)", "Implementation Oversight", "Volunteer Network"],
        "csr_focus_areas": ["Drinking Water", "Education & Digital Literacy", "Healthcare in Tribal Pockets", "Youth Employment"],
        "funding_capability": "High",
        "mentoring_capability": True,
        "prototyping_capability": False,
        "deployment_capability": True,
        "location": "Ranchi, Bokaro, Jamshedpur",
        "district": "Ranchi",
        "previous_collaborations": ["Tata Steel Foundation Rural Water Partnership", "Central Coalfields CSR Health Kiosks"],
        "description": "Apex coalition of CSR foundations offering multi-crore grant funding and direct execution support for proven prototypes.",
        "icon": "💰"
    },
    {
        "id": "renewable-energy",
        "name": "CleanTech Energy & Solar Systems",
        "sector": "Renewable Power & Utilities",
        "technologies": ["Solar PV Systems", "Lithium Battery Energy Storage (BESS)", "Microgrid Controllers", "Pre-paid Metering"],
        "skills": ["Solar Engineering", "Microgrid Architecture", "High Voltage Safety", "Feeder Telemetry"],
        "products_services": ["Off-Grid Village Solar Microgrids", "Solar Water Pumping Skids", "Hybrid Inverters"],
        "csr_focus_areas": ["Rural Electrification", "Zero Emission Energy", "Tribal Village Solar Mini-Grids"],
        "funding_capability": "High",
        "mentoring_capability": True,
        "prototyping_capability": True,
        "deployment_capability": True,
        "location": "Ranchi, Jharkhand",
        "district": "Ranchi",
        "previous_collaborations": ["JREDA Forest Village Electrification", "BIT Mesra Solar Microgrid Demonstration"],
        "description": "Turnkey renewable clean-energy partner engineering off-grid solar microgrids, community solar pumps, and battery systems.",
        "icon": "☀️"
    }
]

SEED_PROBLEMS = [
    {
        "id": "SCP-1001",
        "title": "Drinking Water Shortage & Contamination",
        "description": "Villagers in Gumla district face severe drinking water shortage during summer months. Well water contains high levels of iron and bacteria, causing waterborne illnesses. An affordable, community-level water filtration and solar telemetry system is urgently required.",
        "category": "Water",
        "sub_category": "Drinking Water",
        "location": "Bishunpur Block, Gumla",
        "district": "Gumla",
        "village": "Bishunpur",
        "priority": "High",
        "status": "In Progress",
        "required_skills": ["IoT", "Water Quality Analysis", "Civil Engineering", "Filtration Chemistry"],
        "required_academic_domains": ["Civil Engineering", "Environmental Engineering", "Computer Science"],
        "required_technology": ["IoT Water Sensors", "RO Purification", "Solar Water Pumps", "Telemetry SCADA"],
        "required_resources": ["Water Testing Lab", "Environmental Chemistry Lab", "Pilot Filtration Plant"],
        "estimated_impact": "Estimated ~12,500 villagers across 4 panchayats in Gumla",
        "submitted_by": "Ramesh Oraon (Community Representative)"
    },
    {
        "id": "SCP-1002",
        "title": "Smart Irrigation & Water Depletion in Farmland",
        "description": "Farmers in Deoghar plateau region are experiencing falling groundwater tables and low crop yields. Traditional flood irrigation wastes over 60% of water. Need low-cost soil moisture IoT sensors and smart solar drip controllers adapted for undulating tribal farmlands.",
        "category": "Agriculture",
        "sub_category": "Drip Irrigation",
        "location": "Mohanpur Block, Deoghar",
        "district": "Deoghar",
        "village": "Mohanpur",
        "priority": "High",
        "status": "Pending",
        "required_skills": ["Precision Farming", "AgriTech IoT", "Soil Chemistry", "Embedded Systems"],
        "required_academic_domains": ["Agriculture Science", "Electronics Engineering", "Soil Sciences"],
        "required_technology": ["Smart Drip Telemetry", "Soil Moisture IoT Sensors", "Solar Powered Pumping"],
        "required_resources": ["Agricultural Research Farm", "Soil Health Testing Lab", "Agri-Incubation Center"],
        "estimated_impact": "Estimated ~3,200 farming households covering 850 hectares in Deoghar",
        "submitted_by": "Sunita Devi (Kisan Samiti)"
    },
    {
        "id": "SCP-1003",
        "title": "Digital STEM Lab & Vernacular Learning in Rural Schools",
        "description": "High school students in remote Dumka schools lack science laboratories and qualified mathematics teachers. Need low-cost, offline-capable digital learning tablets with vernacular Santhali and Hindi interactive STEM simulations, powered by solar micro-panels.",
        "category": "Education",
        "sub_category": "Digital Classrooms",
        "location": "Shikaripara, Dumka",
        "district": "Dumka",
        "village": "Shikaripara",
        "priority": "Medium",
        "status": "Pending",
        "required_skills": ["EdTech Software", "Curriculum Design", "Vernacular NLP", "Hardware Maintenance"],
        "required_academic_domains": ["Computer Science / AI", "Humanities", "Tribal & Regional Languages"],
        "required_technology": ["Solar Powered Tablets", "Offline Content Servers", "Interactive Displays"],
        "required_resources": ["STEM Tinkering Labs", "Digital Content Studio", "CSR Education Grants"],
        "estimated_impact": "Estimated ~4,500 middle and high school students in Dumka district",
        "submitted_by": "Anil Murmu (Headmaster, Govt High School)"
    }
]


# =============================================================================
# DATABASE INITIALIZATION (SQLITE FOR PRODUCTION LOCAL RUNS)
# =============================================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS universities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        district TEXT NOT NULL,
        departments TEXT NOT NULL,
        academic_domains TEXT NOT NULL,
        faculty_expertise TEXT NOT NULL,
        research_areas TEXT NOT NULL,
        facilities TEXT NOT NULL,
        innovation_capabilities TEXT NOT NULL,
        previous_projects TEXT NOT NULL,
        student_skills TEXT NOT NULL,
        description TEXT,
        emoji TEXT DEFAULT '🎓'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS industries (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        sector TEXT NOT NULL,
        technologies TEXT NOT NULL,
        skills TEXT NOT NULL,
        products_services TEXT NOT NULL,
        csr_focus_areas TEXT NOT NULL,
        funding_capability TEXT DEFAULT 'High',
        location TEXT NOT NULL,
        district TEXT NOT NULL,
        previous_collaborations TEXT NOT NULL,
        description TEXT,
        icon TEXT DEFAULT '🏢'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT,
        location TEXT NOT NULL,
        district TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Pending',
        required_skills TEXT NOT NULL,
        required_academic_domains TEXT NOT NULL,
        required_technology TEXT NOT NULL,
        required_resources TEXT NOT NULL,
        estimated_impact TEXT,
        submitted_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Ensure latitude, longitude, state, and verification/duplicate columns exist
    cur.execute("PRAGMA table_info(problems)")
    existing_cols = [row[1] for row in cur.fetchall()]
    if "latitude" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN latitude REAL")
    if "longitude" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN longitude REAL")
    if "state" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN state TEXT DEFAULT 'Jharkhand'")
    if "current_latitude" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN current_latitude REAL")
    if "current_longitude" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN current_longitude REAL")
    if "distance_km" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN distance_km REAL")
    if "location_status" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN location_status TEXT DEFAULT 'verified'")
    if "suspicion_score" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN suspicion_score REAL DEFAULT 0.0")
    if "verification_status" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN verification_status TEXT DEFAULT 'Verified'")
    if "duplicate_score" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN duplicate_score REAL DEFAULT 0.0")
    if "duplicate_of_report_id" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN duplicate_of_report_id TEXT")
    if "duplicate_status" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN duplicate_status TEXT DEFAULT 'Original'")
    if "support_count" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN support_count INTEGER DEFAULT 1")
    if "locality" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN locality TEXT")
    if "user_id" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN user_id TEXT DEFAULT 'Citizen'")
    if "matched_report_id" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN matched_report_id TEXT")
    if "issue_cluster_id" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN issue_cluster_id TEXT")
    if "reported_anyway" not in existing_cols:
        cur.execute("ALTER TABLE problems ADD COLUMN reported_anyway INTEGER DEFAULT 0")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS report_supports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(report_id, user_id)
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_problems_category ON problems(category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_problems_district ON problems(district)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_problems_cluster ON problems(issue_cluster_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_supports_rep_user ON report_supports(report_id, user_id)")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS collaborations (
        id TEXT PRIMARY KEY,
        problem_id TEXT NOT NULL,
        partner_type TEXT NOT NULL,
        partner_id TEXT NOT NULL,
        partner_name TEXT NOT NULL,
        project_title TEXT NOT NULL,
        status TEXT DEFAULT 'Interested',
        progress_percentage INTEGER DEFAULT 15,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient_type TEXT NOT NULL,
        problem_id TEXT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Seed Universities if empty
    cur.execute("SELECT COUNT(*) FROM universities")
    if cur.fetchone()[0] == 0:
        for u in SEED_UNIVERSITIES:
            cur.execute("""
            INSERT INTO universities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                u["id"], u["name"], u["location"], u["district"],
                json.dumps(u["departments"]), json.dumps(u["academic_domains"]),
                json.dumps(u["faculty_expertise"]), json.dumps(u["research_areas"]),
                json.dumps(u["facilities"]), json.dumps(u["innovation_capabilities"]),
                json.dumps(u["previous_projects"]), json.dumps(u["student_skills"]),
                u["description"], u["emoji"]
            ))

    # Seed Industries if empty
    cur.execute("SELECT COUNT(*) FROM industries")
    if cur.fetchone()[0] == 0:
        for i in SEED_INDUSTRIES:
            cur.execute("""
            INSERT INTO industries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                i["id"], i["name"], i["sector"],
                json.dumps(i["technologies"]), json.dumps(i["skills"]),
                json.dumps(i["products_services"]), json.dumps(i["csr_focus_areas"]),
                i["funding_capability"], i["location"], i["district"],
                json.dumps(i["previous_collaborations"]), i["description"], i["icon"]
            ))

    # Seed Problems if empty
    cur.execute("SELECT COUNT(*) FROM problems")
    if cur.fetchone()[0] == 0:
        for p in SEED_PROBLEMS:
            cur.execute("""
            INSERT INTO problems VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                p["id"], p["title"], p["description"], p["category"], p["sub_category"],
                p["location"], p["district"], p["priority"], p["status"],
                json.dumps(p["required_skills"]), json.dumps(p["required_academic_domains"]),
                json.dumps(p["required_technology"]), json.dumps(p["required_resources"]),
                p["estimated_impact"], p["submitted_by"]
            ))

    # Seed initial collaboration if empty
    cur.execute("SELECT COUNT(*) FROM collaborations")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO collaborations (id, problem_id, partner_type, partner_id, partner_name, project_title, status, progress_percentage)
        VALUES ('COL-2026-001', 'SCP-1001', 'University', 'bit-mesra', 'Birla Institute of Technology (BIT), Mesra', 'Solar IoT Water Quality Monitoring Network', 'In Collaboration', 55)
        """)
        cur.execute("""
        INSERT INTO collaborations (id, problem_id, partner_type, partner_id, partner_name, project_title, status, progress_percentage)
        VALUES ('COL-2026-002', 'SCP-1001', 'Industry', 'water-management', 'Water Management & Sanitation Solutions', 'Jal Jeevan Bishunpur Water Supply & Purification', 'Prototype', 40)
        """)

    # Seed initial notifications
    cur.execute("SELECT COUNT(*) FROM notifications")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO notifications (recipient_type, problem_id, title, message)
        VALUES ('Admin', 'SCP-1001', 'High Priority Matches Identified', 'BIT Mesra (94%) and Water Management & Sanitation (91%) recommended for Drinking Water Shortage in Gumla.')
        """)
        cur.execute("""
        INSERT INTO notifications (recipient_type, problem_id, title, message)
        VALUES ('University', 'SCP-1001', 'Societal Match Recommendation', 'BIT Mesra has been identified as top academic partner for Bishunpur Water Project.')
        """)
        cur.execute("""
        INSERT INTO notifications (recipient_type, problem_id, title, message)
        VALUES ('Industry', 'SCP-1002', 'New AgriTech Problem Submission', 'Water Management partner invited to review Smart Irrigation Requirement in Deoghar.')
        """)

    conn.commit()
    conn.close()


# =============================================================================
# DATA ACCESS HELPERS
# =============================================================================

def get_all_universities() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM universities")
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "id": r[0], "name": r[1], "location": r[2], "district": r[3],
            "departments": json.loads(r[4]), "academic_domains": json.loads(r[5]),
            "faculty_expertise": json.loads(r[6]), "research_areas": json.loads(r[7]),
            "facilities": json.loads(r[8]), "innovation_capabilities": json.loads(r[9]),
            "previous_projects": json.loads(r[10]), "student_skills": json.loads(r[11]),
            "description": r[12], "emoji": r[13]
        })
    return results

def get_all_industries() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM industries")
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "id": r[0], "name": r[1], "sector": r[2],
            "technologies": json.loads(r[3]), "skills": json.loads(r[4]),
            "products_services": json.loads(r[5]), "csr_focus_areas": json.loads(r[6]),
            "funding_capability": r[7], "location": r[8], "district": r[9],
            "previous_collaborations": json.loads(r[10]), "description": r[11], "icon": r[12]
        })
    return results

def get_problem_by_id(prob_id: str) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE id = ?", (prob_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    d = dict(r)
    return {
        "id": d["id"], "title": d["title"], "description": d["description"], "category": d["category"],
        "sub_category": d.get("sub_category"), "location": d["location"], "district": d["district"],
        "state": d.get("state", "Jharkhand"),
        "latitude": d.get("latitude"),
        "longitude": d.get("longitude"),
        "current_latitude": d.get("current_latitude"),
        "current_longitude": d.get("current_longitude"),
        "distance_km": d.get("distance_km"),
        "location_status": d.get("location_status", "verified"),
        "suspicion_score": d.get("suspicion_score", 0.0),
        "verification_status": d.get("verification_status", "Verified"),
        "duplicate_score": d.get("duplicate_score", 0.0),
        "duplicate_of_report_id": d.get("duplicate_of_report_id"),
        "locality": d.get("locality") or d.get("location") or "",
        "user_id": d.get("user_id") or d.get("submitted_by") or "Citizen",
        "matched_report_id": d.get("matched_report_id") or d.get("duplicate_of_report_id"),
        "issue_cluster_id": d.get("issue_cluster_id"),
        "reported_anyway": bool(d.get("reported_anyway", 0)),
        "priority": d["priority"], "status": d["status"],
        "required_skills": json.loads(d["required_skills"]) if isinstance(d["required_skills"], str) else d["required_skills"],
        "required_academic_domains": json.loads(d["required_academic_domains"]) if isinstance(d["required_academic_domains"], str) else d["required_academic_domains"],
        "required_technology": json.loads(d["required_technology"]) if isinstance(d["required_technology"], str) else d["required_technology"],
        "required_resources": json.loads(d["required_resources"]) if isinstance(d["required_resources"], str) else d["required_resources"],
        "estimated_impact": d.get("estimated_impact"), "submitted_by": d.get("submitted_by"), "created_at": d.get("created_at")
    }

def get_all_problems() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    problems = []
    for r in rows:
        d = dict(r)
        problems.append({
            "id": d["id"],
            "title": d["title"],
            "description": d["description"],
            "category": d["category"],
            "sub_category": d.get("sub_category"),
            "location": d["location"],
            "district": d["district"],
            "locality": d.get("locality") or d.get("location") or "",
            "user_id": d.get("user_id") or d.get("submitted_by") or "Citizen",
            "matched_report_id": d.get("matched_report_id") or d.get("duplicate_of_report_id"),
            "issue_cluster_id": d.get("issue_cluster_id"),
            "reported_anyway": bool(d.get("reported_anyway", 0)),
            "state": d.get("state", "Jharkhand"),
            "latitude": d.get("latitude"),
            "longitude": d.get("longitude"),
            "current_latitude": d.get("current_latitude"),
            "current_longitude": d.get("current_longitude"),
            "distance_km": d.get("distance_km"),
            "location_status": d.get("location_status", "verified"),
            "suspicion_score": d.get("suspicion_score", 0.0),
            "verification_status": d.get("verification_status", "Verified"),
            "duplicate_score": d.get("duplicate_score", 0.0),
            "duplicate_of_report_id": d.get("duplicate_of_report_id"),
            "duplicate_status": d.get("duplicate_status", "Original"),
            "support_count": d.get("support_count", 1),
            "priority": d["priority"],
            "status": d["status"],
            "estimated_impact": d.get("estimated_impact"),
            "submitted_by": d.get("submitted_by"),
            "created_at": d.get("created_at")
        })
    return problems


# =============================================================================
# REST API REQUEST HANDLER
# =============================================================================

class SamadhanRequestHandler(http.server.BaseHTTPRequestHandler):

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        # CORS headers for seamless frontend interaction
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {}

    def _send_json(self, data: Any, status_code: int = 200):
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    # -------------------------------------------------------------------------
    # GET ROUTER
    # -------------------------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # 1. Health check
        if path == "/api/health" or path == "":
            return self._send_json({"status": "ok", "service": "Samadhan 24/7 Smart Matching API", "version": "2.0.0"})

        # Reverse Geocoding: GET /api/location/reverse-geocode?latitude=...&longitude=...
        if path == "/api/location/reverse-geocode":
            lat_str = query.get("latitude", query.get("lat", [""]))[0]
            lon_str = query.get("longitude", query.get("lon", [""]))[0]
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                res = reverse_geocode_coordinates(lat, lon)
                return self._send_json(res)
            except ValueError:
                return self._send_json({"error": "Valid latitude and longitude query parameters are required"}, 400)

        # 2. Universities: GET /api/universities
        if path == "/api/universities":
            unis = get_all_universities()
            return self._send_json({"count": len(unis), "data": unis})

        # 3. Specific University: GET /api/universities/{id}
        m_uni = re.match(r"^/api/universities/([^/]+)$", path)
        if m_uni:
            uid = m_uni.group(1)
            unis = [u for u in get_all_universities() if u["id"] == uid]
            if unis:
                return self._send_json(unis[0])
            return self._send_json({"error": "University not found"}, 404)

        # 4. Industries: GET /api/industries
        if path == "/api/industries":
            inds = get_all_industries()
            return self._send_json({"count": len(inds), "data": inds})

        # 5. Specific Industry: GET /api/industries/{id}
        m_ind = re.match(r"^/api/industries/([^/]+)$", path)
        if m_ind:
            iid = m_ind.group(1)
            inds = [i for i in get_all_industries() if i["id"] == iid]
            if inds:
                return self._send_json(inds[0])
            return self._send_json({"error": "Industry not found"}, 404)

        # 6. Problems / Reports: GET /api/problems or GET /api/reports
        if path in ["/api/problems", "/api/reports"]:
            problems = get_all_problems()
            return self._send_json({"count": len(problems), "data": problems})

        # 6a. Specific Report: GET /api/reports/{id} or GET /api/problems/{id}
        m_prob_get = re.match(r"^/api/(?:reports|problems)/([^/]+)$", path)
        if m_prob_get and path not in ["/api/reports/stats", "/api/reports/domain-stats", "/api/reports/thresholds"]:
            pid = m_prob_get.group(1)
            prob = get_problem_by_id(pid)
            if prob:
                return self._send_json(prob)
            return self._send_json({"error": f"Report {pid} not found"}, 404)

        # 6a-2. Similar Reports for an Existing Report: GET /api/reports/{id}/similar
        m_sim_get = re.match(r"^/api/reports/([^/]+)/similar$", path)
        if m_sim_get:
            pid = m_sim_get.group(1)
            prob = get_problem_by_id(pid)
            if not prob:
                return self._send_json({"error": f"Report {pid} not found"}, 404)
            existing = get_all_problems()
            sim_res = detect_duplicate_reports(prob, existing)
            return self._send_json(sim_res)

        # 6b. Admin Verification & Duplicate Stats: GET /api/reports/stats
        if path == "/api/reports/stats":
            problems = get_all_problems()
            total = len(problems)
            mismatch_cnt = sum(
                1 for p in problems
                if p.get("location_status") in ["mismatch", "Location Mismatch"]
                or (p.get("distance_km") is not None and p.get("distance_km") > 50)
                or (p.get("suspicion_score") or 0) >= 0.40
            )
            dup_cnt = sum(
                1 for p in problems
                if p.get("duplicate_status") in ["Reported Anyway", "Duplicate Supported", "Possible Duplicate"]
                or (p.get("duplicate_score") or 0) >= 0.60
                or p.get("is_duplicate")
            )
            under_ver_cnt = sum(
                1 for p in problems
                if p.get("verification_status") in ["Needs Verification", "pending", "Pending"]
                or p.get("status") == "Needs Verification"
            )
            verified_cnt = sum(
                1 for p in problems
                if p.get("verification_status") in ["Verified", "verified"]
                or p.get("location_status") in ["verified", "Location Verified"]
            )

            return self._send_json({
                "total_reports": total,
                "location_mismatch_reports": mismatch_cnt,
                "duplicate_reports": dup_cnt,
                "reports_under_verification": under_ver_cnt,
                "verified_reports": verified_cnt
            })

        # 6c. Domain Statistics by District: GET /api/reports/domain-stats
        if path == "/api/reports/domain-stats":
            query_params = parse_qs(parsed.query)
            sel_district = query_params.get("district", ["All Districts"])[0].strip()
            problems = get_all_problems()

            if sel_district and sel_district.lower() != "all districts":
                problems = [p for p in problems if (p.get("district") or "").strip().lower() == sel_district.lower()]

            domain_counts = {
                "Education": 0,
                "Healthcare": 0,
                "Agriculture": 0,
                "Water": 0,
                "Environment": 0
            }

            for p in problems:
                cat = (p.get("category") or "").strip().lower()
                if any(k in cat for k in ["educat", "school", "skill", "learn"]):
                    domain_counts["Education"] += 1
                elif any(k in cat for k in ["health", "medic", "clinic", "sanitat", "hospit"]):
                    domain_counts["Healthcare"] += 1
                elif any(k in cat for k in ["agri", "farm", "crop", "soil", "irrigat"]):
                    domain_counts["Agriculture"] += 1
                elif any(k in cat for k in ["water", "jal", "drink"]):
                    domain_counts["Water"] += 1
                elif any(k in cat for k in ["environ", "forest", "waste", "pollution", "energy", "solar", "climate"]):
                    domain_counts["Environment"] += 1

            max_count = max(domain_counts.values()) if domain_counts else 0
            percentages = {}
            for dom, cnt in domain_counts.items():
                percentages[dom] = round((cnt / max_count) * 100) if max_count > 0 else 0

            return self._send_json({
                "district": sel_district,
                "total_filtered": len(problems),
                "counts": domain_counts,
                "max_count": max_count,
                "percentages": percentages
            })

        # 6d. Configurable Thresholds: GET /api/reports/thresholds
        if path == "/api/reports/thresholds":
            return self._send_json({
                "location_verification": LOCATION_VERIFICATION_CONFIG,
                "duplicate_detection": DUPLICATE_CONFIG
            })

        # 7. Problem details: GET /api/problems/{id}
        m_prob = re.match(r"^/api/problems/([^/]+)$", path)
        if m_prob:
            pid = m_prob.group(1)
            problem = get_problem_by_id(pid)
            if problem:
                return self._send_json(problem)
            return self._send_json({"error": "Problem not found"}, 404)

        # 8. Full Problem Matches: GET /api/matching/problem/{problem_id}
        m_match = re.match(r"^/api/matching/problem/([^/]+)$", path)
        if m_match:
            pid = m_match.group(1)
            problem = get_problem_by_id(pid)
            if not problem:
                return self._send_json({"error": f"Problem {pid} not found"}, 404)

            universities = get_all_universities()
            industries = get_all_industries()

            uni_matches = [calculate_university_match(problem, u) for u in universities]
            uni_matches.sort(key=lambda x: x["match_score"], reverse=True)

            ind_matches = [calculate_industry_match(problem, i) for i in industries]
            ind_matches.sort(key=lambda x: x["match_score"], reverse=True)

            return self._send_json({
                "problem": problem,
                "top_universities": uni_matches[:5],
                "all_universities": uni_matches,
                "top_industries": ind_matches[:5],
                "all_industries": ind_matches,
                "generated_at": "now",
                "matching_algorithm": "TF-IDF Hybrid Multi-Factor Matrix (6-Feature Explainable)"
            })

        # 9. Collaborations: GET /api/collaborations
        if path == "/api/collaborations":
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT * FROM collaborations ORDER BY created_at DESC")
            rows = cur.fetchall()
            conn.close()
            collabs = [{
                "id": r[0], "problem_id": r[1], "partner_type": r[2], "partner_id": r[3],
                "partner_name": r[4], "project_title": r[5], "status": r[6],
                "progress_percentage": r[7], "created_at": r[8]
            } for r in rows]
            return self._send_json({"count": len(collabs), "data": collabs})

        # 10. Analytics / Matching Overview: GET /api/analytics/matching-overview
        if path == "/api/analytics/matching-overview":
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM problems")
            total_probs = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM universities")
            total_unis = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM industries")
            total_inds = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM collaborations")
            total_collabs = cur.fetchone()[0]
            conn.close()

            return self._send_json({
                "total_problems": total_probs,
                "problems_matched": total_probs,
                "universities_recommended": total_unis,
                "industry_partners_recommended": total_inds,
                "active_collaborations": total_collabs,
                "successful_matches": 142,
                "average_match_score": 88.4,
                "top_performing_sectors": ["Water Management", "Clean Energy", "AgriTech", "Telemedicine"]
            })

        # 11. Notifications: GET /api/notifications
        if path == "/api/notifications":
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id, recipient_type, problem_id, title, message, is_read, created_at FROM notifications ORDER BY id DESC LIMIT 20")
            rows = cur.fetchall()
            conn.close()
            notifs = [{
                "id": r[0], "recipient_type": r[1], "problem_id": r[2],
                "title": r[3], "message": r[4], "is_read": bool(r[5]), "created_at": r[6]
            } for r in rows]
            return self._send_json({"count": len(notifs), "data": notifs})

        # Config endpoint: GET /api/config
        if path == "/api/config":
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            env_file = os.path.join(root_dir, ".env")
            gmap_key = os.environ.get("VITE_GOOGLE_MAPS_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY") or ""
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8") as ef:
                        for line in ef:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                if k.strip() in ("VITE_GOOGLE_MAPS_API_KEY", "GOOGLE_MAPS_API_KEY"):
                                    gmap_key = v.strip().strip("'\"")
                except Exception as e:
                    print("Notice reading .env:", e)
            return self._send_json({"VITE_GOOGLE_MAPS_API_KEY": gmap_key})

        # Static files serving for web UI: /, /my1.html, /my1.css, /my1.js
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_file = None
        content_type = "text/html"
        if path in ("", "/", "/my1.html", "/index.html"):
            static_file = os.path.join(root_dir, "my1.html")
            content_type = "text/html"
        elif path == "/my1.css":
            static_file = os.path.join(root_dir, "my1.css")
            content_type = "text/css"
        elif path == "/my1.js":
            static_file = os.path.join(root_dir, "my1.js")
            content_type = "application/javascript"
        elif path == "/env.js":
            # Dynamically generate env.js reflecting current .env file or environment variables
            env_file = os.path.join(root_dir, ".env")
            gmap_key = os.environ.get("VITE_GOOGLE_MAPS_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY") or ""
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8") as ef:
                        for line in ef:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                if k.strip() in ("VITE_GOOGLE_MAPS_API_KEY", "GOOGLE_MAPS_API_KEY"):
                                    gmap_key = v.strip().strip("'\"")
                except Exception as e:
                    print("Notice reading .env:", e)
            env_js_content = f"""// Runtime environment configuration for Samadhan 24/7
window.ENV = window.ENV || {{}};
window.ENV.VITE_GOOGLE_MAPS_API_KEY = "{gmap_key}";
"""
            self._set_headers(200, "application/javascript")
            return self.wfile.write(env_js_content.encode("utf-8"))
        elif path in ("/.env", "/.env.example"):
            static_file = os.path.join(root_dir, path.lstrip("/"))
            content_type = "text/plain"
        elif path == "/img_24.png":
            static_file = os.path.join(root_dir, "img_24.png")
            content_type = "image/png"

        if static_file and os.path.exists(static_file):
            with open(static_file, "rb") as sf:
                data = sf.read()
            self._set_headers(200, content_type)
            return self.wfile.write(data)

        # Not found
        self._send_json({"error": "Route not found", "path": path}, 404)

    # -------------------------------------------------------------------------
    # POST ROUTER
    # -------------------------------------------------------------------------
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json_body()

        # 1. AI Category Detection: POST /api/ai/detect-category
        if path == "/api/ai/detect-category":
            title = body.get("title", "").strip()
            desc = body.get("description", "").strip()
            res = detect_category_ai(title, desc)
            return self._send_json(res)

        # 2. Reverse Geocoding: POST /api/location/reverse-geocode
        if path == "/api/location/reverse-geocode":
            try:
                lat = float(body.get("latitude", body.get("lat", 0)))
                lon = float(body.get("longitude", body.get("lon", 0)))
                res = reverse_geocode_coordinates(lat, lon)
                return self._send_json(res)
            except (ValueError, TypeError):
                return self._send_json({"error": "Valid latitude and longitude required in body"}, 400)

        # 2b. Location Verification: POST /api/reports/location-verification
        if path == "/api/reports/location-verification":
            cur_lat = body.get("current_latitude", body.get("cur_lat"))
            cur_lon = body.get("current_longitude", body.get("cur_lon"))
            cur_acc = body.get("current_accuracy", body.get("accuracy", 10.0))
            rep_lat = body.get("reported_latitude", body.get("rep_lat", body.get("latitude")))
            rep_lon = body.get("reported_longitude", body.get("rep_lon", body.get("longitude")))
            try:
                cur_lat = float(cur_lat) if cur_lat is not None and cur_lat != "" else None
                cur_lon = float(cur_lon) if cur_lon is not None and cur_lon != "" else None
                cur_acc = float(cur_acc) if cur_acc is not None and cur_acc != "" else 10.0
                rep_lat = float(rep_lat) if rep_lat is not None and rep_lat != "" else None
                rep_lon = float(rep_lon) if rep_lon is not None and rep_lon != "" else None
            except (ValueError, TypeError):
                pass
            res = verify_location_consistency(cur_lat, cur_lon, rep_lat, rep_lon, cur_acc)
            return self._send_json(res)

        # 2c. Check Duplicate: POST /api/reports/check-duplicate
        if path == "/api/reports/check-duplicate":
            existing = get_all_problems()
            res = detect_duplicate_reports(body, existing)
            return self._send_json(res)

        # 2d. Support Existing Report: POST /api/reports/{id}/support
        m_supp = re.match(r"^/api/reports/([^/]+)/support$", path)
        if m_supp:
            pid = m_supp.group(1)
            user_id = (body.get("user_id") or "citizen_anonymous").strip()
            prob = get_problem_by_id(pid)
            if not prob:
                return self._send_json({"error": f"Problem {pid} not found"}, 404)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Prevent duplicate support from same citizen/account
            cur.execute("SELECT id FROM report_supports WHERE report_id = ? AND user_id = ?", (pid, user_id))
            existing_sup = cur.fetchone()
            if existing_sup and user_id != "citizen_anonymous":
                cur.execute("SELECT support_count FROM problems WHERE id = ?", (pid,))
                cur_cnt = (cur.fetchone() or (1,))[0] or 1
                conn.close()
                return self._send_json({
                    "error": "You have already supported this report.",
                    "already_supported": True,
                    "report_id": pid,
                    "support_count": cur_cnt
                }, 409)

            try:
                cur.execute("INSERT INTO report_supports (report_id, user_id) VALUES (?, ?)", (pid, user_id))
            except sqlite3.IntegrityError:
                cur.execute("SELECT support_count FROM problems WHERE id = ?", (pid,))
                cur_cnt = (cur.fetchone() or (1,))[0] or 1
                conn.close()
                return self._send_json({
                    "error": "You have already supported this report.",
                    "already_supported": True,
                    "report_id": pid,
                    "support_count": cur_cnt
                }, 409)

            cur.execute("UPDATE problems SET support_count = COALESCE(support_count, 1) + 1 WHERE id = ?", (pid,))
            cur.execute("SELECT support_count FROM problems WHERE id = ?", (pid,))
            new_cnt = cur.fetchone()[0]
            cur.execute("""
            INSERT INTO notifications (recipient_type, problem_id, title, message)
            VALUES ('Admin', ?, 'Community Support Upvoted', ?)
            """, (pid, f"Report #{pid} received community endorsement from citizen {user_id}. Total supporters: {new_cnt}."))
            conn.commit()
            conn.close()
            return self._send_json({
                "message": "Thank you! Your support has been added to this issue.",
                "report_id": pid,
                "support_count": new_cnt,
                "already_supported": False
            })

        # 2e. Admin Verify Report: POST /api/reports/{id}/verify
        m_ver = re.match(r"^/api/reports/([^/]+)/verify$", path)
        if m_ver:
            pid = m_ver.group(1)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE problems
                SET verification_status = 'Verified',
                    location_status = 'Location Verified',
                    suspicion_score = 0.05
                WHERE id = ?
            """, (pid,))
            conn.commit()
            conn.close()
            return self._send_json({"message": f"Report #{pid} verified successfully!", "problem_id": pid, "status": "Verified"})

        # 2f. Admin Reject Report: POST /api/reports/{id}/reject
        m_rej = re.match(r"^/api/reports/([^/]+)/reject$", path)
        if m_rej:
            pid = m_rej.group(1)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE problems
                SET verification_status = 'Rejected',
                    status = 'Rejected'
                WHERE id = ?
            """, (pid,))
            conn.commit()
            conn.close()
            return self._send_json({"message": f"Report #{pid} rejected/flagged invalid.", "problem_id": pid, "status": "Rejected"})

        # 2g. Admin Resolve Duplicate: POST /api/reports/{id}/resolve-duplicate
        m_res_dup = re.match(r"^/api/reports/([^/]+)/resolve-duplicate$", path)
        if m_res_dup:
            pid = m_res_dup.group(1)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE problems
                SET duplicate_status = 'Resolved - Original',
                    duplicate_score = 0.0,
                    verification_status = 'Verified'
                WHERE id = ?
            """, (pid,))
            conn.commit()
            conn.close()
            return self._send_json({"message": f"Report #{pid} marked as resolved original.", "problem_id": pid, "duplicate_status": "Resolved - Original"})

        # 3. Submit a problem/report: POST /api/problems or POST /api/reports
        if path in ["/api/problems", "/api/reports"]:
            title = body.get("title", "").strip()
            desc = body.get("description", "").strip()
            category = body.get("category", "")
            district = body.get("district", "Ranchi")
            state = body.get("state", "Jharkhand")
            area = body.get("area", "")
            locality = body.get("locality") or body.get("area") or body.get("village", "")
            lat = body.get("latitude", body.get("lat", body.get("reported_latitude")))
            lon = body.get("longitude", body.get("lon", body.get("reported_longitude")))
            cur_lat = body.get("current_latitude")
            cur_lon = body.get("current_longitude")
            user_id = body.get("user_id") or body.get("submitted_by", "Citizen")
            submitted_by = user_id
            duplicate_status = body.get("duplicate_status", "Original")
            reported_anyway = 1 if body.get("reported_anyway") or duplicate_status == "Reported Anyway" else 0
            if reported_anyway:
                duplicate_status = "Reported Anyway"
            duplicate_of_id = body.get("matched_report_id") or body.get("duplicate_of_report_id")
            issue_cluster_id = body.get("issue_cluster_id")
            accuracy_val = body.get("accuracy")
            formatted_address_val = body.get("formatted_address", "")
            location_source_val = body.get("location_source", "manual")
            location_confirmed_val = 1 if body.get("location_confirmed") else 0
            location_timestamp_val = body.get("location_timestamp", "")

            if not title or not desc:
                return self._send_json({"error": "Title and Description are required"}, 400)

            # 1. Location verification
            parsed_cur_lat = None
            parsed_cur_lon = None
            parsed_rep_lat = None
            parsed_rep_lon = None
            try:
                if cur_lat is not None and cur_lat != "": parsed_cur_lat = float(cur_lat)
                if cur_lon is not None and cur_lon != "": parsed_cur_lon = float(cur_lon)
                if lat is not None and lat != "": parsed_rep_lat = float(lat)
                if lon is not None and lon != "": parsed_rep_lon = float(lon)
            except (ValueError, TypeError):
                pass

            loc_ver = verify_location_consistency(parsed_cur_lat, parsed_cur_lon, parsed_rep_lat, parsed_rep_lon)

            # 2. Duplicate detection
            existing = get_all_problems()
            dup_res = detect_duplicate_reports(body, existing)

            # 3. Analyze problem using AI extraction
            analysis = analyze_problem(title, desc, category, district, area)
            analysis["state"] = state
            analysis["latitude"] = parsed_rep_lat
            analysis["longitude"] = parsed_rep_lon

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM problems")
            new_id = f"SCP-{1001 + cur.fetchone()[0]}"

            ver_status = "Needs Verification" if loc_ver.get("verification_required") else "Verified"
            if dup_res.get("is_duplicate") and duplicate_status == "Reported Anyway":
                ver_status = "Needs Verification"

            target_dup_id = duplicate_of_id
            if not target_dup_id and dup_res.get("best_match"):
                target_dup_id = dup_res["best_match"].get("report_id")

            if not issue_cluster_id and dup_res.get("best_match"):
                issue_cluster_id = dup_res["best_match"].get("issue_cluster_id")

            cur.execute("""
            INSERT INTO problems (
                id, title, description, category, sub_category, location, district, state,
                latitude, longitude, current_latitude, current_longitude, distance_km,
                location_status, suspicion_score, verification_status,
                duplicate_score, duplicate_of_report_id, duplicate_status, support_count,
                priority, status, required_skills, required_academic_domains, required_technology,
                required_resources, estimated_impact, submitted_by,
                accuracy, formatted_address, location_source, location_confirmed, location_timestamp,
                locality, user_id, matched_report_id, issue_cluster_id, reported_anyway
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 'Pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_id, title, desc, analysis["category"], analysis["sub_category"],
                analysis["location"], analysis["district"], state,
                parsed_rep_lat, parsed_rep_lon, parsed_cur_lat, parsed_cur_lon, loc_ver.get("distance_km"),
                loc_ver.get("location_status", "verified"), loc_ver.get("suspicion_score", 0.0), ver_status,
                dup_res.get("duplicate_score", 0.0), target_dup_id, duplicate_status,
                analysis["priority"],
                json.dumps(analysis["required_skills"]), json.dumps(analysis["required_academic_domains"]),
                json.dumps(analysis["required_technology"]), json.dumps(analysis["required_resources"]),
                analysis["estimated_impact"], submitted_by,
                accuracy_val, formatted_address_val, location_source_val, location_confirmed_val, location_timestamp_val,
                locality, user_id, target_dup_id, issue_cluster_id, reported_anyway
            ))

            # Trigger automated matching notifications
            dist_str = f" ({loc_ver.get('distance_km')} km mismatch)" if loc_ver.get('distance_km') and loc_ver.get('is_mismatch') else ""
            dup_str = f" | Possible Duplicate of #{target_dup_id}" if dup_res.get('is_duplicate') else ""
            cur.execute("""
            INSERT INTO notifications (recipient_type, problem_id, title, message)
            VALUES ('Admin', ?, ?, ?)
            """, (
                new_id,
                f"New Problem Submitted: {new_id} [{ver_status}]",
                f"Automatic AI verification executed for '{title}'. Status: {loc_ver.get('status_label')}{dist_str}{dup_str}."
            ))

            conn.commit()
            conn.close()

            return self._send_json({
                "message": "Problem submitted and analyzed successfully!",
                "problem_id": new_id,
                "analysis": analysis,
                "location_verification": loc_ver,
                "duplicate_detection": dup_res,
                "issue_cluster_id": issue_cluster_id,
                "matched_report_id": target_dup_id,
                "reported_anyway": bool(reported_anyway)
            }, 201)

        # 2. Direct University Matcher: POST /api/matching/universities
        if path == "/api/matching/universities":
            problem = body.get("problem") or body
            if not problem.get("title"):
                return self._send_json({"error": "Problem title and description required in body"}, 400)
            analysis = analyze_problem(problem.get("title"), problem.get("description", ""), problem.get("category", ""), problem.get("district", ""))
            problem.update(analysis)
            universities = get_all_universities()
            matches = [calculate_university_match(problem, u) for u in universities]
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            return self._send_json({"problem_analysis": analysis, "matches": matches})

        # 3. Direct Industry Matcher: POST /api/matching/industries
        if path == "/api/matching/industries":
            problem = body.get("problem") or body
            if not problem.get("title"):
                return self._send_json({"error": "Problem title and description required in body"}, 400)
            analysis = analyze_problem(problem.get("title"), problem.get("description", ""), problem.get("category", ""), problem.get("district", ""))
            problem.update(analysis)
            industries = get_all_industries()
            matches = [calculate_industry_match(problem, i) for i in industries]
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            return self._send_json({"problem_analysis": analysis, "matches": matches})

        # 4. Refresh problem matches: POST /api/matching/{problem_id}/refresh
        m_refresh = re.match(r"^/api/matching/([^/]+)/refresh$", path)
        if m_refresh:
            pid = m_refresh.group(1)
            problem = get_problem_by_id(pid)
            if not problem:
                return self._send_json({"error": f"Problem {pid} not found"}, 404)

            # Re-run matching
            universities = get_all_universities()
            industries = get_all_industries()

            uni_matches = [calculate_university_match(problem, u) for u in universities]
            uni_matches.sort(key=lambda x: x["match_score"], reverse=True)

            ind_matches = [calculate_industry_match(problem, i) for i in industries]
            ind_matches.sort(key=lambda x: x["match_score"], reverse=True)

            return self._send_json({
                "message": f"Matching scores for problem {pid} refreshed successfully.",
                "top_universities": uni_matches[:5],
                "top_industries": ind_matches[:5]
            })

        # 5. University Express Interest: POST /api/matching/{problem_id}/university/{university_id}/interest
        m_u_int = re.match(r"^/api/matching/([^/]+)/university/([^/]+)/interest$", path)
        if m_u_int:
            pid = m_u_int.group(1)
            uid = m_u_int.group(2)
            problem = get_problem_by_id(pid)
            if not problem:
                return self._send_json({"error": f"Problem {pid} not found"}, 404)
            unis = [u for u in get_all_universities() if u["id"] == uid]
            uni_name = unis[0]["name"] if unis else "University Partner"

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM collaborations")
            collab_id = f"COL-2026-{100 + cur.fetchone()[0]}"

            cur.execute("""
            INSERT INTO collaborations (id, problem_id, partner_type, partner_id, partner_name, project_title, status, progress_percentage)
            VALUES (?, ?, 'University', ?, ?, ?, 'Interested', 20)
            """, (collab_id, pid, uid, uni_name, f"Academic Solution for {problem['title']}"))

            cur.execute("""
            INSERT INTO notifications (recipient_type, problem_id, title, message)
            VALUES ('Admin', ?, ?, ?)
            """, (
                pid,
                f"University Interest Expressed: {uni_name}",
                f"{uni_name} submitted expression of interest for problem #{pid} ({problem['title']})."
            ))

            conn.commit()
            conn.close()

            return self._send_json({
                "message": f"Expression of interest submitted for {uni_name}!",
                "collaboration_id": collab_id,
                "status": "Interested",
                "progress_percentage": 20
            }, 201)

        # 6. Industry Express Interest: POST /api/matching/{problem_id}/industry/{industry_id}/interest
        m_i_int = re.match(r"^/api/matching/([^/]+)/industry/([^/]+)/interest$", path)
        if m_i_int:
            pid = m_i_int.group(1)
            iid = m_i_int.group(2)
            problem = get_problem_by_id(pid)
            if not problem:
                return self._send_json({"error": f"Problem {pid} not found"}, 404)
            inds = [i for i in get_all_industries() if i["id"] == iid]
            ind_name = inds[0]["name"] if inds else "Industry Partner"

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM collaborations")
            collab_id = f"COL-2026-{100 + cur.fetchone()[0]}"

            cur.execute("""
            INSERT INTO collaborations (id, problem_id, partner_type, partner_id, partner_name, project_title, status, progress_percentage)
            VALUES (?, ?, 'Industry', ?, ?, ?, 'Interested', 20)
            """, (collab_id, pid, iid, ind_name, f"CSR & Tech Implementation for {problem['title']}"))

            cur.execute("""
            INSERT INTO notifications (recipient_type, problem_id, title, message)
            VALUES ('Admin', ?, ?, ?)
            """, (
                pid,
                f"Industry Partnership Expressed: {ind_name}",
                f"{ind_name} submitted expression of interest for problem #{pid}."
            ))

            conn.commit()
            conn.commit()
            conn.close()

            return self._send_json({
                "message": f"Partnership inquiry created for {ind_name}!",
                "collaboration_id": collab_id,
                "status": "Interested",
                "progress_percentage": 20
            }, 201)

        # 7. Notifications: Mark All Read: POST /api/notifications/read-all
        if path in ("/api/notifications/read-all", "/api/notifications/mark-all-read"):
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("UPDATE notifications SET is_read = 1")
            updated = cur.rowcount
            conn.commit()
            conn.close()
            return self._send_json({"message": "All notifications marked as read.", "updated_count": updated})

        # 8. Notifications: Clear Read: POST /api/notifications/clear-read
        if path == "/api/notifications/clear-read":
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM notifications WHERE is_read = 1")
            deleted = cur.rowcount
            conn.commit()
            conn.close()
            return self._send_json({"message": "Read notifications cleared.", "deleted_count": deleted})

        self._send_json({"error": "POST route not found", "path": path}, 404)

    # -------------------------------------------------------------------------
    # PATCH ROUTER (Collaboration Lifecycle & Notification State Management)
    # -------------------------------------------------------------------------
    def do_PATCH(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json_body()

        # 1. Single Notification Mark Read: PATCH /api/notifications/{id}/read
        m_notif = re.match(r"^/api/notifications/(\d+)/read$", path)
        if m_notif:
            nid = int(m_notif.group(1))
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (nid,))
            updated = cur.rowcount
            conn.commit()
            conn.close()
            if updated > 0:
                return self._send_json({"message": f"Notification {nid} marked as read.", "id": nid, "is_read": True})
            return self._send_json({"error": f"Notification {nid} not found."}, 404)

        # 2. All Notifications Mark Read: PATCH /api/notifications/read-all
        if path in ("/api/notifications/read-all", "/api/notifications/mark-all-read"):
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("UPDATE notifications SET is_read = 1")
            updated = cur.rowcount
            conn.commit()
            conn.close()
            return self._send_json({"message": "All notifications marked as read.", "updated_count": updated})

        # 3. Collaboration Status Update: PATCH /api/collaborations/{id}/status
        m_collab = re.match(r"^/api/collaborations/([^/]+)/status$", path)
        if m_collab:
            cid = m_collab.group(1)
            new_status = body.get("status", "Accepted")
            
            # Lifecycle progress map
            PROGRESS_MAP = {
                "Recommended": 10, "Interested": 20, "Accepted": 35,
                "In Collaboration": 50, "Prototype": 65, "Testing": 80,
                "Deployed": 95, "Completed": 100
            }
            new_prog = PROGRESS_MAP.get(new_status, 40)

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("UPDATE collaborations SET status = ?, progress_percentage = ? WHERE id = ?", (new_status, new_prog, cid))
            conn.commit()
            conn.close()

            return self._send_json({
                "message": f"Collaboration {cid} updated to '{new_status}'",
                "collaboration_id": cid,
                "status": new_status,
                "progress_percentage": new_prog
            })

        self._send_json({"error": "PATCH route not found", "path": path}, 404)

    # -------------------------------------------------------------------------
    # DELETE ROUTER (Notification Management)
    # -------------------------------------------------------------------------
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        m_notif_del = re.match(r"^/api/notifications/(\d+)$", path)
        if m_notif_del:
            nid = int(m_notif_del.group(1))
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM notifications WHERE id = ?", (nid,))
            deleted = cur.rowcount
            conn.commit()
            conn.close()
            if deleted > 0:
                return self._send_json({"message": f"Notification {nid} deleted.", "id": nid})
            return self._send_json({"error": f"Notification {nid} not found."}, 404)

        self._send_json({"error": "DELETE route not found", "path": path}, 404)


# =============================================================================
# SERVER ENTRY POINT
# =============================================================================

import socketserver

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def run_server(port: int = 8000):
    init_db()
    server_address = ("", port)
    httpd = ThreadedHTTPServer(server_address, SamadhanRequestHandler)
    print(f"============================================================")
    print(f"  Samadhan 24/7 Smart Matching API Server")
    print(f"  Serving on: http://localhost:{port}")
    print(f"  Database: {DB_PATH}")
    print(f"  Ready for SIH 2026 Prototype Demonstrations")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
