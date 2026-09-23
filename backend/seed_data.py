import sqlite3
import json

conn = sqlite3.connect("backend/samadhan.db")
cur = conn.cursor()

cur.execute("DELETE FROM problems")

cur_problems = [
    # RANCHI (5 problems: Education, Healthcare, Environment, Water, Agriculture)
    ("SCP-1001", "Smart Digital STEM Labs for Peri-Urban Schools",
     "Government schools around Ranchi lack modern science labs and interactive digital kits. A low-cost vernacular digital lab with simulations is needed.",
     "Education", "Digital Classrooms", "Kanke Block, Ranchi", "Ranchi", "Jharkhand",
     23.435, 85.321, 23.431, 85.325, 0.6, "verified", 0.05, "Verified", 0.0, None, "Original", 3, "High", "In Progress"),

    ("SCP-1002", "Mobile Tele-Clinic & Diagnostics for Remote Tribal Hamlets",
     "Tribal hamlets on the outskirts of Ranchi require portable point-of-care diagnostics and telemedicine consultations with specialists.",
     "Healthcare", "Telemedicine", "Burmu Block, Ranchi", "Ranchi", "Jharkhand",
     23.582, 85.122, 23.585, 85.120, 0.4, "verified", 0.04, "Verified", 0.0, None, "Original", 4, "High", "Pending"),

    ("SCP-1003", "Decentralized Organic Waste Composting for Daily Vegetable Mandis",
     "Severe organic vegetable waste accumulation at wholesale mandis in Ranchi causing foul smell and drainage blockage. Requires bio-composting digester units.",
     "Environment", "Waste Management", "Pandra Market Yard, Ranchi", "Ranchi", "Jharkhand",
     23.385, 85.289, 23.381, 85.292, 0.5, "verified", 0.06, "Verified", 0.0, None, "Original", 2, "Medium", "Pending"),

    ("SCP-1004", "Groundwater Depletion & Sub-Surface Aquifer Recharging in Hatia Basin",
     "Hatia dam catchment has experienced drastic water table drops affecting 45,000 residents during summer months. Need IoT sensor recharge borewells.",
     "Water", "Water Recharge", "Hatia, Ranchi", "Ranchi", "Jharkhand",
     23.295, 85.312, 23.310, 85.305, 1.8, "low_concern", 0.18, "Needs Verification", 0.0, None, "Original", 5, "High", "Pending"),

    ("SCP-1005", "Solar Cold Storage & Polyhouse Micro-Drip for Peri-Urban Farmers",
     "Peri-urban smallholders in Ormanjhi need micro-climate polyhouses and off-grid solar cold storage to prevent tomato and vegetable spoilage.",
     "Agriculture", "Cold Storage", "Ormanjhi, Ranchi", "Ranchi", "Jharkhand",
     23.483, 85.478, 22.801, 86.202, 108.4, "Location Mismatch", 0.88, "Needs Verification", 0.0, None, "Original", 1, "High", "Needs Verification"),

    # GUMLA (5 problems: Water, Water dup, Agriculture, Healthcare, Education)
    ("SCP-1006", "Drinking Water Fluoride Contamination & Scarcity in Bishunpur",
     "Villagers in Bishunpur block, Gumla district face severe drinking water shortages. High fluoride and iron levels require community-scale filtration.",
     "Water", "Drinking Water", "Bishunpur Block, Gumla", "Gumla", "Jharkhand",
     23.376, 84.372, 23.374, 84.370, 0.3, "verified", 0.04, "Verified", 0.0, None, "Original", 8, "High", "In Progress"),

    ("SCP-1007", "Acute Drinking Water Scarcity in Ghaghra Panchayat",
     "Ghaghra panchayat villagers have contaminated tube wells with brown silt and fluoride. Seeking filtration kiosks and solar pump installation.",
     "Water", "Drinking Water", "Ghaghra Block, Gumla", "Gumla", "Jharkhand",
     23.398, 84.412, 23.395, 84.410, 0.4, "verified", 0.05, "Needs Verification", 0.84, "SCP-1006", "Reported Anyway", 2, "Medium", "Needs Verification"),

    ("SCP-1008", "Finger Millet (Ragi) Processing & Packaging Unit for Tribal SHGs",
     "Gumla is a leading producer of nutritious ragi millets, but lack of de-hulling and packaging machinery reduces farmer income by 50%.",
     "Agriculture", "Agri-Processing", "Raidih Block, Gumla", "Gumla", "Jharkhand",
     23.045, 84.412, 23.048, 84.410, 0.4, "verified", 0.04, "Verified", 0.0, None, "Original", 6, "Medium", "In Progress"),

    ("SCP-1009", "Child Malnutrition Screening & Poshan Telemedicine Kits",
     "Anganwadi centers in remote forested pockets of Gumla require digital MUAC biometric bands and telehealth link to pediatrician.",
     "Healthcare", "Maternal & Child Health", "Chainpur, Gumla", "Gumla", "Jharkhand",
     23.112, 84.234, 23.110, 84.236, 0.3, "verified", 0.05, "Verified", 0.0, None, "Original", 3, "High", "Pending"),

    ("SCP-1010", "Solar Powered Bilingual E-Classrooms in Forest Schools",
     "Off-grid tribal primary schools in Gumla require rugged solar tablets with Kurukh and Hindi foundational literacy modules.",
     "Education", "Digital Classrooms", "Palkot Block, Gumla", "Gumla", "Jharkhand",
     22.880, 84.645, 22.882, 84.640, 0.6, "verified", 0.06, "Verified", 0.0, None, "Original", 2, "Medium", "Pending"),

    # DHANBAD (5 problems: Environment, Environment Mismatch, Healthcare, Water, Education)
    ("SCP-1011", "Industrial Steel Slag Valorization & Eco-Brick Manufacturing",
     "Heavy metallurgical slag dumping causes environmental dusting and land loss in Dhanbad coal belt. Need geopolymer compression recipes.",
     "Environment", "Slag Recycling", "Jharia & Katras, Dhanbad", "Dhanbad", "Jharkhand",
     23.742, 86.415, 23.740, 86.412, 0.4, "verified", 0.04, "Verified", 0.0, None, "Original", 7, "Medium", "In Progress"),

    ("SCP-1012", "Continuous Drone Telemetry for Coal Mine Dust & Particulate Emissions",
     "Open-cast mines generate heavy PM2.5 and PM10 plumes. IoT telemetry and mist dispersal drones needed to monitor buffer zones.",
     "Environment", "Air Quality", "Katras Area, Dhanbad", "Dhanbad", "Jharkhand",
     23.812, 86.295, 23.360, 85.330, 142.6, "Location Mismatch", 0.92, "Needs Verification", 0.0, None, "Original", 1, "High", "Needs Verification"),

    ("SCP-1013", "Occupational Respiratory Health Surveillance & Mobile Spirometry Kiosk",
     "Coal mining and transport workers require regular pneumoconiosis and silicosis pulmonary function screening with AI chest X-ray evaluation.",
     "Healthcare", "Occupational Health", "Sindri Road, Dhanbad", "Dhanbad", "Jharkhand",
     23.655, 86.502, 23.652, 86.505, 0.4, "verified", 0.05, "Verified", 0.0, None, "Original", 5, "High", "Pending"),

    ("SCP-1014", "Coal Mine Pit Water Neutralization for Agricultural Irrigation",
     "Abandoned opencast quarry pits contain millions of gallons of acidic water. Low-cost lime dosing and bio-filtration can irrigate 400 hectares.",
     "Water", "Mine Water Treatment", "Nirsa Block, Dhanbad", "Dhanbad", "Jharkhand",
     23.785, 86.720, 23.782, 86.722, 0.4, "verified", 0.05, "Verified", 0.0, None, "Original", 3, "Medium", "Pending"),

    ("SCP-1015", "Vocational Mining Safety & Heavy Equipment VR Simulation Lab",
     "Youth in Dhanbad need immersive virtual reality simulators to learn heavy earth-moving machinery operation and underground safety protocols.",
     "Education", "Vocational Training", "Govindpur, Dhanbad", "Dhanbad", "Jharkhand",
     23.835, 86.520, 23.832, 86.524, 0.5, "verified", 0.05, "Verified", 0.0, None, "Original", 2, "Medium", "Pending"),

    # DEOGHAR (4 problems: Agriculture, Agriculture dup, Water, Healthcare)
    ("SCP-1016", "Smart Micro-Drip Irrigation & Soil Moisture Telemetry in Undulating Red Soil",
     "Farmers in Deoghar plateau region experience falling groundwater tables and crop losses. Need affordable IoT soil sensors and smart drip kits.",
     "Agriculture", "Drip Irrigation", "Mohanpur Block, Deoghar", "Deoghar", "Jharkhand",
     24.482, 86.702, 24.480, 86.700, 0.3, "verified", 0.04, "Verified", 0.0, None, "Original", 9, "High", "In Progress"),

    ("SCP-1017", "IoT Soil Health Sensor Nodes for Plateau Farmlands",
     "Precision farming IoT sensor deployment for monitoring NPK, pH, and soil moisture across undulating tribal farmlands.",
     "Agriculture", "Precision Farming", "Devipur Block, Deoghar", "Deoghar", "Jharkhand",
     24.440, 86.620, 24.442, 86.618, 0.3, "verified", 0.05, "Needs Verification", 0.81, "SCP-1016", "Reported Anyway", 2, "Medium", "Needs Verification"),

    ("SCP-1018", "Rainwater Harvesting & Talab Renovation for Drought Mitigation",
     "Seasonal drought in Sarath block leaves smallholders without irrigation. Community pond desilting and geotextile lining needed.",
     "Water", "Rainwater Harvesting", "Sarath Block, Deoghar", "Deoghar", "Jharkhand",
     24.235, 86.850, 24.238, 86.848, 0.4, "verified", 0.04, "Verified", 0.0, None, "Original", 4, "High", "Pending"),

    ("SCP-1019", "Pilgrimage Corridor Emergency First-Aid & Telemedicine Support",
     "During Shravani Mela, millions of pilgrims travel on foot through Deoghar. Portable emergency vital-sign telemedicine kits needed.",
     "Healthcare", "Emergency Health", "Baidyanath Dham, Deoghar", "Deoghar", "Jharkhand",
     24.492, 86.700, 24.490, 86.702, 0.3, "verified", 0.04, "Verified", 0.0, None, "Original", 4, "High", "In Progress"),

    # BOKARO (3 problems: Environment, Water, Education)
    ("SCP-1020", "Slag Waste Geopolymerization & Dust Emission Control",
     "Industrial buffer zones in Bokaro require slag dust suppression and geopolymer road paving blocks for rural roads.",
     "Environment", "Industrial Ecology", "Chas, Bokaro", "Bokaro", "Jharkhand",
     23.635, 86.180, 23.632, 86.182, 0.4, "verified", 0.05, "Verified", 0.0, None, "Original", 3, "Medium", "Pending"),

    ("SCP-1021", "Community Water Filtration Kiosks for Chas Outskirts",
     "Heavy industrial discharge near Chas has affected shallow tube-wells with turbidity and iron. Multi-stage filtration units needed.",
     "Water", "Water Purification", "Chas Sub-division, Bokaro", "Bokaro", "Jharkhand",
     23.640, 86.175, 23.638, 86.178, 0.3, "verified", 0.05, "Verified", 0.0, None, "Original", 3, "Medium", "Pending"),

    ("SCP-1022", "Robotics & Advanced Welding Training for Industrial Youth",
     "Local youth around Bokaro steel industrial cluster need certified automation and robotic welding skill centers.",
     "Education", "Vocational Training", "Sector 4, Bokaro Steel City", "Bokaro", "Jharkhand",
     23.665, 86.150, 23.662, 86.152, 0.4, "verified", 0.04, "Verified", 0.0, None, "Original", 2, "Medium", "Pending"),

    # DUMKA (2 problems: Education, Water)
    ("SCP-1023", "Bilingual STEM Curriculum Tablets in Santhali & Hindi",
     "Secondary schools in Shikaripara suffer from severe shortage of science educators. Offline bilingual digital learning tablets required.",
     "Education", "Digital Learning", "Shikaripara, Dumka", "Dumka", "Jharkhand",
     24.260, 87.520, 24.258, 87.522, 0.3, "verified", 0.04, "Verified", 0.0, None, "Original", 5, "High", "In Progress"),

    ("SCP-1024", "Check Dam & Water Table Recharging for Tribal Farmers",
     "Undulating hilly streams in Dumka dry up within 2 months of monsoon. Sand-filled geo-bag check dams can conserve water.",
     "Water", "Water Harvesting", "Jama Block, Dumka", "Dumka", "Jharkhand",
     24.350, 87.310, 24.348, 87.312, 0.3, "verified", 0.04, "Verified", 0.0, None, "Original", 4, "Medium", "Pending"),

    # LATEHAR (1 problem: Environment Mismatch)
    ("SCP-1025", "Decentralized Solar-Biomass Hybrid Microgrid for Forest Tribal Villages",
     "Villages deep inside Betla National Park corridor in Latehar cannot be connected to high-tension power grid. Need 25kW hybrid microgrid.",
     "Environment", "Clean Energy", "Mahuadanr, Latehar", "Latehar", "Jharkhand",
     23.745, 84.498, 23.360, 85.330, 94.2, "Location Mismatch", 0.79, "Needs Verification", 0.0, None, "Original", 4, "High", "Needs Verification"),

    # WEST SINGHBHUM (1 problem: Healthcare)
    ("SCP-1026", "Mobile Sickle-Cell & Malaria Diagnostic Kits for Dense Forest Hamlets",
     "Remote tribal forest villages in Goilkera are 35km away from healthcare centers. Portable blood testing kits and satellite link needed.",
     "Healthcare", "Diagnostics", "Goilkera, West Singhbhum", "West Singhbhum", "Jharkhand",
     22.512, 85.385, 22.510, 85.388, 0.4, "verified", 0.04, "Verified", 0.0, None, "Original", 6, "High", "In Progress")
]

for p in cur_problems:
    cur.execute("""
    INSERT INTO problems (
        id, title, description, category, sub_category, location, district, state,
        latitude, longitude, current_latitude, current_longitude, distance_km,
        location_status, suspicion_score, verification_status, duplicate_score,
        duplicate_of_report_id, duplicate_status, support_count, priority, status,
        required_skills, required_academic_domains, required_technology, required_resources,
        estimated_impact, submitted_by
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7],
        p[8], p[9], p[10], p[11], p[12],
        p[13], p[14], p[15], p[16],
        p[17], p[18], p[19], p[20], p[21],
        json.dumps(["IoT", "Data Analytics"]),
        json.dumps(["Engineering", "Environmental Sciences"]),
        json.dumps(["Sensors", "Telemetry"]),
        json.dumps(["Field Lab", "Testing Equipment"]),
        "Estimated ~10,000 local beneficiaries",
        "Local Community Council"
    ))

conn.commit()
cur.execute("SELECT COUNT(*) FROM problems")
print("Total problems after seeding:", cur.fetchone()[0])
conn.close()
