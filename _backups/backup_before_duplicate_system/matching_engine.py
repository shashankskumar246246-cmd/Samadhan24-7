"""
Samadhan 24/7 - Automatic University + Industry Smart Matching Engine
Production AI/NLP & Multi-Factor Scoring Algorithm
"""

import math
import re
from typing import Dict, List, Any, Tuple


# =============================================================================
# DOMAIN TAXONOMY & KEYWORD MAPPINGS FOR JHARKHAND SOCIETAL PROBLEMS
# =============================================================================

TAXONOMY = {
    "Water": {
        "subcategories": ["Drinking Water", "Water Quality", "Groundwater Depletion", "Piped Water", "Irrigation Canals", "Mine Water Treatment"],
        "skills": ["IoT", "Water Quality Analysis", "Civil Engineering", "Hydrogeology", "SCADA", "Sensor Interfacing", "Filtration Chemistry", "Data Analytics"],
        "domains": ["Civil Engineering", "Environmental Engineering", "Computer Science", "Chemistry", "Water Resource Management", "Earth Sciences"],
        "technology": ["IoT Water Sensors", "RO Purification", "Solar Water Pumps", "Telemetry SCADA", "GIS Mapping", "Smart Meters"],
        "resources": ["Water Testing Lab", "Environmental Chemistry Lab", "Pilot Filtration Plant", "CSR Infrastructure Grants", "Field Technicians"]
    },
    "Agriculture": {
        "subcategories": ["Drip Irrigation", "Soil Fertility", "Plateau Crops", "Cold Storage", "Pest Detection", "Farmer Market Access"],
        "skills": ["Precision Farming", "AgriTech IoT", "Soil Chemistry", "Crop Pathology", "Drone Remote Sensing", "Embedded Systems", "Agro-Forestry"],
        "domains": ["Agriculture Science", "Soil Sciences", "Biotechnology", "Electronics Engineering", "Agro-Economics", "Robotics"],
        "technology": ["Smart Drip Telemetry", "Drone Multispectral Imaging", "Solar Cold Storage", "Mobile Advisory Apps", "Automated Greenhouses"],
        "resources": ["Agricultural Research Farm", "Soil Analysis Lab", "Drone Fleet", "Agri-Incubation Center", "FPO Network"]
    },
    "Healthcare": {
        "subcategories": ["Primary Care Access", "Telemedicine", "Maternal Health", "Malnutrition", "Rural Diagnostics", "Mobile Medical Units"],
        "skills": ["Tele-health Diagnostics", "Biomedical Engineering", "Public Health", "Clinical AI", "Embedded Medical Sensors", "Epidemiology"],
        "domains": ["Medical & Health Sciences", "Public Health", "Biotechnology", "Computer Science", "Pharmaceutical Sciences"],
        "technology": ["Telemedicine Kiosks", "Point-of-Care Blood Testing", "Portable ECG/Ultrasound", "Health Cloud Records", "AI Diagnostic Screeners"],
        "resources": ["Apex Hospital Beds", "Clinical Diagnostics Lab", "Biomedical Prototyping Lab", "Ambulance Network", "CSR Healthcare Grants"]
    },
    "Education": {
        "subcategories": ["Teacher Shortage", "Digital Classrooms", "STEM Education", "Vernacular Learning", "Vocational Training", "Tribal Literacy"],
        "skills": ["EdTech Software", "Curriculum Design", "Vernacular NLP", "Interactive Pedagogy", "Offline Digital Content", "Hardware Maintenance"],
        "domains": ["Computer Science / AI", "Humanities", "Tribal & Regional Languages", "Education Technology", "Social Sciences"],
        "technology": ["Solar Powered Tablets", "Offline Content Servers", "Smart Class Interactive Displays", "Speech Recognition for Tribal Dialects"],
        "resources": ["STEM Tinkering Labs", "Digital Content Studio", "Teacher Training Facility", "CSR Education Grants"]
    },
    "Environment": {
        "subcategories": ["Industrial Slag Recycling", "Mine Land Reclamation", "Air & Water Pollution", "Solid Waste Management", "Plastic Upcycling", "Forest Conservation"],
        "skills": ["Waste Valorization", "Environmental Chemistry", "Mine Tailings Stabilization", "Ecology & Forestry", "Air Quality Monitoring"],
        "domains": ["Environmental Science", "Mining & Mineral Engineering", "Metallurgy & Materials Science", "Chemical Engineering", "Ecology"],
        "technology": ["Continuous Emission Monitoring (CEMS)", "Geopolymer Brick Plants", "Pyrolysis Units", "Drone Forest Canopy Scanners"],
        "resources": ["Environmental Testing Lab", "Slag Characterization Facility", "Materials Synthesis Lab", "Heavy Machinery"]
    },
    "Energy": {
        "subcategories": ["Rural Solar Microgrids", "Biomass Energy", "Grid Reliability", "Mine Methane Recovery", "Energy Storage"],
        "skills": ["Solar PV Engineering", "Microgrid SCADA", "Battery Energy Storage", "Power Electronics", "Renewable Energy Economics"],
        "domains": ["Electrical Engineering", "Energy Engineering", "Clean Energy", "Physics", "Computer Science"],
        "technology": ["Solar PV Arrays", "Lithium / Flow Batteries", "Smart Inverters", "Remote Energy Monitoring", "Smart Pre-paid Meters"],
        "resources": ["High Voltage Testing Lab", "Solar Simulator", "Battery Prototyping Workshop", "Clean Energy Grants"]
    },
    "Water Management": {
        "subcategories": ["Drinking Water", "Water Quality", "Groundwater Depletion", "Piped Water", "Irrigation Canals", "Mine Water Treatment"],
        "skills": ["IoT", "Water Quality Analysis", "Civil Engineering", "Hydrogeology", "SCADA", "Sensor Interfacing", "Filtration Chemistry", "Data Analytics"],
        "domains": ["Civil Engineering", "Environmental Engineering", "Computer Science", "Chemistry", "Water Resource Management", "Earth Sciences"],
        "technology": ["IoT Water Sensors", "RO Purification", "Solar Water Pumps", "Telemetry SCADA", "GIS Mapping", "Smart Meters"],
        "resources": ["Water Testing Lab", "Environmental Chemistry Lab", "Pilot Filtration Plant", "CSR Infrastructure Grants", "Field Technicians"]
    },
    "Sanitation": {
        "subcategories": ["Solid Waste Collection", "Sewage Treatment", "Community Toilets", "Drainage Systems", "Waste Recycling"],
        "skills": ["Sanitation Engineering", "Waste Management", "Biochemical Treatment", "Civil Engineering", "Urban Planning"],
        "domains": ["Environmental Engineering", "Civil Engineering", "Public Health", "Biotechnology"],
        "technology": ["Bio-Digester Toilets", "Smart Waste Bins", "Sewage Treatment Plants (STP)", "Waste Shredders"],
        "resources": ["Sanitation Testing Lab", "Municipal Waste Facility", "Composting Unit"]
    },
    "Urban Infrastructure": {
        "subcategories": ["Road Maintenance", "Stormwater Drainage", "Smart Streetlighting", "Bridge Safety", "Public Transport"],
        "skills": ["Civil & Structural Engineering", "Pavement Design", "IoT Traffic Systems", "Urban Planning", "GIS Mapping"],
        "domains": ["Civil Engineering", "Transportation Engineering", "Urban Planning", "Electrical Engineering"],
        "technology": ["Cold Mix Asphalt", "Pothole Detection Drones", "Smart LED Telemetry", "Structural Health Sensors"],
        "resources": ["Materials Testing Lab", "Structural Dynamics Lab", "Heavy Machinery Network"]
    },
    "Urban Development": {
        "subcategories": ["Road Maintenance", "Stormwater Drainage", "Smart Streetlighting", "Bridge Safety", "Public Transport"],
        "skills": ["Civil & Structural Engineering", "Pavement Design", "IoT Traffic Systems", "Urban Planning", "GIS Mapping"],
        "domains": ["Civil Engineering", "Transportation Engineering", "Urban Planning", "Electrical Engineering"],
        "technology": ["Cold Mix Asphalt", "Pothole Detection Drones", "Smart LED Telemetry", "Structural Health Sensors"],
        "resources": ["Materials Testing Lab", "Structural Dynamics Lab", "Heavy Machinery Network"]
    },
    "Rural Livelihoods": {
        "subcategories": ["Tribal Artisan Clusters", "Handloom & Tussar Silk", "Agro-Processing", "Dairy & Poultry", "Self-Help Groups"],
        "skills": ["Textile Technology", "Supply Chain Management", "Agro-Enterprise", "Product Design", "Digital Marketing"],
        "domains": ["Social Work", "Textile Engineering", "Rural Development", "Management Studies"],
        "technology": ["Solar Weaving Looms", "Cold Chain Logistics", "E-Commerce Marketplaces", "Traceability QR"],
        "resources": ["Artisan Design Studio", "Testing Center", "Incubation Center"]
    },
    "Accessibility": {
        "subcategories": ["Wheelchair Mobility", "Assistive Tech for Visually Impaired", "Barrier-Free Public Spaces", "Deaf & Mute Aids"],
        "skills": ["Assistive Technology", "Biomechanics", "Embedded Systems", "Universal Design", "Computer Vision"],
        "domains": ["Biomedical Engineering", "Computer Science", "Architecture", "Mechanical Engineering"],
        "technology": ["Smart White Canes", "Automated Wheelchair Ramps", "Haptic Navigation Devices", "Text-to-Speech AI"],
        "resources": ["Assistive Devices Lab", "Prototyping Workshop", "Ergonomics Evaluation Lab"]
    },
    "Public Services": {
        "subcategories": ["E-Governance Delivery", "Public Grievance Redressal", "Welfare Scheme Access", "Panchayat Digitization"],
        "skills": ["Software Engineering", "Public Administration", "Cybersecurity", "Cloud Architecture", "Data Science"],
        "domains": ["Computer Science", "Public Policy", "Information Technology", "Law"],
        "technology": ["Blockchain Certificate Registry", "Citizen Mobile Portals", "AI Helpdesk Bots", "Biometric Authentication"],
        "resources": ["E-Gov Testing Center", "Data Center", "Cloud Server Infrastructure"]
    },
    "Disaster Management": {
        "subcategories": ["Flood Early Warning", "Drought Relief", "Landslide Monitoring", "Emergency Shelter Logistics", "Cyclone Response"],
        "skills": ["Geotechnical Engineering", "Remote Sensing & GIS", "Hydrological Modeling", "Disaster Logistics", "IoT Telemetry"],
        "domains": ["Earth Sciences", "Civil Engineering", "Environmental Science", "Computer Science"],
        "technology": ["River Gauge Telemetry", "Early Warning Sirens", "Drone Reconnaissance Fleet", "Satellite Inundation Maps"],
        "resources": ["Emergency Operations Center", "Disaster Drone Fleet", "Hydraulic Testing Lab"]
    },
    "Other": {
        "subcategories": ["Community Innovation", "Grassroots Solutions", "General Development", "Civic Tech"],
        "skills": ["Problem Solving", "Prototyping", "Interdisciplinary Engineering", "Community Engagement"],
        "domains": ["Interdisciplinary Sciences", "Social Innovation", "Engineering Design"],
        "technology": ["Rapid Prototyping", "Open Source Hardware", "Mobile Apps"],
        "resources": ["Maker Space", "Innovation Hub", "Incubator"]
    }
}


# =============================================================================
# TF-IDF & TEXT SIMILARITY UTILITIES
# =============================================================================

STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "is", "are", "was", "were", "and", "or", "as", "be", "has", "have", "had",
    "that", "this", "these", "those", "it", "its", "their", "our", "village", "villagers",
    "district", "jharkhand", "area", "problem", "issue", "need", "facing", "required"
}

def tokenize(text: str) -> List[str]:
    """Extract normalized alphanumeric tokens, excluding common stopwords."""
    if not text:
        return []
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def compute_term_frequencies(tokens: List[str]) -> Dict[str, float]:
    """Compute normalized term frequencies for a list of tokens."""
    tf: Dict[str, float] = {}
    if not tokens:
        return tf
    for t in tokens:
        tf[t] = tf.get(t, 0.0) + 1.0
    total = float(len(tokens))
    for t in tf:
        tf[t] = tf[t] / total
    return tf


def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Compute cosine similarity between two frequency vectors."""
    common_keys = set(vec_a.keys()).intersection(vec_b.keys())
    if not common_keys:
        return 0.0
    dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def calculate_jaccard(list_a: List[str], list_b: List[str]) -> float:
    """Calculate Jaccard similarity index between two string lists."""
    set_a = {item.strip().lower() for item in list_a if item}
    set_b = {item.strip().lower() for item in list_b if item}
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0


# =============================================================================
# 1. PROBLEM ANALYSIS & METADATA EXTRACTION
# =============================================================================

def analyze_problem(title: str, description: str, category_hint: str = "", district: str = "", area: str = "") -> Dict[str, Any]:
    """
    Analyzes submitted societal problem text and extracts:
    - Primary Category & Sub-category
    - Required technical skills
    - Academic domains
    - Required technology
    - Required resources & facilities
    - Priority / Severity
    - Estimated community impact
    """
    combined_text = f"{title} {description}".lower()
    
    # Category detection
    detected_cat = category_hint
    best_match_count = 0
    
    if not detected_cat or detected_cat not in TAXONOMY:
        for cat, data in TAXONOMY.items():
            count = 0
            for skill in data["skills"]:
                if skill.lower() in combined_text:
                    count += 2
            for domain in data["domains"]:
                if domain.lower() in combined_text:
                    count += 2
            for sub in data["subcategories"]:
                if sub.lower() in combined_text:
                    count += 3
            if cat.lower() in combined_text:
                count += 4
            if count > best_match_count:
                best_match_count = count
                detected_cat = cat
        if not detected_cat:
            detected_cat = "Water"  # Default sensible fallback

    cat_meta = TAXONOMY.get(detected_cat, TAXONOMY["Water"])

    # Determine sub-category
    matched_sub = cat_meta["subcategories"][0]
    for sub in cat_meta["subcategories"]:
        if sub.lower() in combined_text:
            matched_sub = sub
            break

    # Extract required skills
    req_skills = []
    for s in cat_meta["skills"]:
        if s.lower() in combined_text or len(req_skills) < 3:
            req_skills.append(s)
    req_skills = list(dict.fromkeys(req_skills))[:4]

    # Extract required domains
    req_domains = []
    for d in cat_meta["domains"]:
        if d.lower() in combined_text or len(req_domains) < 3:
            req_domains.append(d)
    req_domains = list(dict.fromkeys(req_domains))[:3]

    # Extract required tech & resources
    req_tech = cat_meta["technology"][:3]
    req_res = cat_meta["resources"][:3]

    # Priority / Severity calculation
    high_words = ["emergency", "death", "danger", "critical", "severe", "no water", "contamination", "poison", "flood", "outbreak", "acute"]
    medium_words = ["problem", "shortage", "lack", "difficulty", "issue", "poor", "needed", "deficiency"]
    priority = "Low"
    for w in high_words:
        if w in combined_text:
            priority = "High"
            break
    if priority == "Low":
        for w in medium_words:
            if w in combined_text:
                priority = "Medium"
                break

    # Estimated impact
    location_str = f"{area + ', ' if area else ''}{district if district else 'Jharkhand'}"
    impact_estimate = f"Estimated ~5,000 to 25,000 community members in {district if district else 'Jharkhand'}"

    tokens = tokenize(combined_text)
    keywords = list(dict.fromkeys(tokens))[:8]

    return {
        "title": title,
        "description": description,
        "category": detected_cat,
        "sub_category": matched_sub,
        "location": location_str,
        "district": district or "Ranchi",
        "priority": priority,
        "required_skills": req_skills,
        "required_academic_domains": req_domains,
        "required_technology": req_tech,
        "required_resources": req_res,
        "keywords": keywords,
        "estimated_impact": impact_estimate
    }


# =============================================================================
# 2. UNIVERSITY MATCHING ENGINE (EXACT WEIGHTS)
# =============================================================================

def calculate_university_match(problem: Dict[str, Any], university: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates explainable match score between a Problem and a University profile.
    Weights:
    - Domain Match: 30%
    - Skill Match: 25%
    - Research Expertise: 20%
    - Location/Regional Relevance: 10%
    - Facilities: 10%
    - Previous Projects: 5%
    Total: 100%
    """
    prob_text = f"{problem.get('title', '')} {problem.get('description', '')} {' '.join(problem.get('keywords', []))}"
    prob_vec = compute_term_frequencies(tokenize(prob_text))
    
    # 1. Domain Match (30%)
    uni_domains = university.get("academic_domains", []) or university.get("researchStreams", [])
    req_domains = problem.get("required_academic_domains", [])
    domain_jaccard = calculate_jaccard(req_domains, uni_domains)
    # Check text overlap in university departments
    dept_text = " ".join(university.get("departments", [])) + " " + " ".join(uni_domains)
    dept_vec = compute_term_frequencies(tokenize(dept_text))
    domain_sim = max(domain_jaccard, cosine_similarity(prob_vec, dept_vec))
    # Direct match boost
    for rd in req_domains:
        if any(rd.lower() in d.lower() or d.lower() in rd.lower() for d in uni_domains):
            domain_sim = max(domain_sim, 0.85)
    domain_score = min(1.0, domain_sim) * 30.0

    # 2. Skill Match (25%)
    uni_skills = university.get("student_skills", []) or university.get("faculty_expertise", [])
    req_skills = problem.get("required_skills", [])
    skill_jaccard = calculate_jaccard(req_skills, uni_skills)
    skill_text = " ".join(uni_skills)
    skill_vec = compute_term_frequencies(tokenize(skill_text))
    skill_sim = max(skill_jaccard, cosine_similarity(prob_vec, skill_vec))
    for rs in req_skills:
        if any(rs.lower() in s.lower() for s in uni_skills):
            skill_sim = max(skill_sim, 0.80)
    skill_score = min(1.0, skill_sim) * 25.0

    # 3. Research Expertise (20%)
    uni_research = university.get("research_areas", []) or university.get("researchStreams", [])
    research_text = " ".join(uni_research) + " " + university.get("description", "")
    res_vec = compute_term_frequencies(tokenize(research_text))
    res_sim = cosine_similarity(prob_vec, res_vec)
    for rd in req_domains:
        if any(rd.lower() in r.lower() for r in uni_research):
            res_sim = max(res_sim, 0.75)
    research_score = min(1.0, res_sim) * 20.0

    # 4. Location/Regional Relevance (10%)
    prob_district = (problem.get("district") or "").lower()
    uni_location = (university.get("location") or "").lower()
    if prob_district and prob_district in uni_location:
        loc_score = 10.0
    elif "ranchi" in uni_location:
        # State capital institutes have statewide outreach
        loc_score = 7.5
    else:
        loc_score = 5.0

    # 5. Facilities & Labs (10%)
    uni_fac = university.get("facilities", [])
    fac_text = " ".join(uni_fac)
    fac_vec = compute_term_frequencies(tokenize(fac_text))
    fac_sim = cosine_similarity(prob_vec, fac_vec)
    if any(k in fac_text.lower() for k in problem.get("keywords", [])):
        fac_sim = max(fac_sim, 0.70)
    facility_score = min(1.0, max(0.4, fac_sim)) * 10.0

    # 6. Previous Projects (5%)
    uni_proj = university.get("previous_projects", [])
    proj_text = " ".join(uni_proj)
    proj_sim = cosine_similarity(prob_vec, compute_term_frequencies(tokenize(proj_text)))
    if any(k in proj_text.lower() for k in problem.get("keywords", [])):
        proj_sim = max(proj_sim, 0.75)
    project_score = min(1.0, max(0.3, proj_sim)) * 5.0

    total_score = round(domain_score + skill_score + research_score + loc_score + facility_score + project_score, 1)
    total_score = min(99.0, max(15.0, total_score))

    # Generate Explainable Reasons
    reasons = []
    matched_domains = [d for d in uni_domains if any(rd.lower() in d.lower() or d.lower() in rd.lower() for rd in req_domains)]
    if matched_domains:
        reasons.append(f"Domain alignment: {', '.join(matched_domains[:2])}")
    else:
        reasons.append(f"Related academic faculties: {uni_domains[0] if uni_domains else 'Multi-disciplinary'}")

    matched_skills = [s for s in uni_skills if any(rs.lower() in s.lower() for rs in req_skills)]
    if matched_skills:
        reasons.append(f"Technical skills matched: {', '.join(matched_skills[:2])}")
    elif req_skills:
        reasons.append(f"Capable of fielding teams in {req_skills[0]}")

    if university.get("facilities"):
        reasons.append(f"Available infrastructure: {university['facilities'][0]}")

    if prob_district and prob_district in uni_location:
        reasons.append(f"Direct local presence in {problem.get('district')}")
    else:
        reasons.append(f"Statewide operational capability from {university.get('location', 'Jharkhand')}")

    if university.get("previous_projects"):
        reasons.append(f"Prior track record: {university['previous_projects'][0]}")

    return {
        "university_id": university.get("id") or university.get("link"),
        "name": university.get("name"),
        "location": university.get("location"),
        "match_score": total_score,
        "breakdown": {
            "domain_score": round(domain_score, 1),
            "skill_score": round(skill_score, 1),
            "research_score": round(research_score, 1),
            "location_score": round(loc_score, 1),
            "facility_score": round(facility_score, 1),
            "project_score": round(project_score, 1)
        },
        "reasons": reasons,
        "relevant_department": university.get("departments", ["Academic Department"])[0] if university.get("departments") else "Applied Sciences",
        "relevant_research": university.get("research_areas", ["Community Innovation"])[0] if university.get("research_areas") else "R&D",
        "matched_skills": matched_skills[:3] if matched_skills else req_skills[:2],
        "emoji": university.get("emoji", "🎓")
    }


# =============================================================================
# 3. INDUSTRY MATCHING ENGINE (EXACT WEIGHTS)
# =============================================================================

def calculate_industry_match(problem: Dict[str, Any], industry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates explainable match score between a Problem and an Industry/CSR partner.
    Weights:
    - Technology Match: 30%
    - Problem Domain Match: 25%
    - CSR/Impact Alignment: 20%
    - Resources/Funding: 10%
    - Location: 10%
    - Previous Experience: 5%
    Total: 100%
    """
    prob_text = f"{problem.get('title', '')} {problem.get('description', '')} {' '.join(problem.get('keywords', []))}"
    prob_vec = compute_term_frequencies(tokenize(prob_text))

    # 1. Technology Match (30%)
    ind_tech = industry.get("technologies", []) or industry.get("focusAreas", [])
    req_tech = problem.get("required_technology", [])
    tech_jaccard = calculate_jaccard(req_tech, ind_tech)
    tech_text = " ".join(ind_tech)
    tech_vec = compute_term_frequencies(tokenize(tech_text))
    tech_sim = max(tech_jaccard, cosine_similarity(prob_vec, tech_vec))
    for rt in req_tech:
        if any(rt.lower() in t.lower() or t.lower() in rt.lower() for t in ind_tech):
            tech_sim = max(tech_sim, 0.85)
    tech_score = min(1.0, tech_sim) * 30.0

    # 2. Problem Domain Match (25%)
    ind_sector = (industry.get("sector") or "") + " " + (industry.get("name") or "")
    sector_vec = compute_term_frequencies(tokenize(ind_sector))
    sector_sim = cosine_similarity(prob_vec, sector_vec)
    prob_cat = (problem.get("category") or "").lower()
    if prob_cat in ind_sector.lower():
        sector_sim = max(sector_sim, 0.90)
    domain_score = min(1.0, sector_sim) * 25.0

    # 3. CSR / Impact Alignment (20%)
    csr_areas = industry.get("csr_focus_areas", []) or industry.get("focusAreas", [])
    csr_text = " ".join(csr_areas)
    csr_vec = compute_term_frequencies(tokenize(csr_text))
    csr_sim = cosine_similarity(prob_vec, csr_vec)
    if any(k in csr_text.lower() for k in problem.get("keywords", [])) or prob_cat in csr_text.lower():
        csr_sim = max(csr_sim, 0.85)
    csr_score = min(1.0, max(0.35, csr_sim)) * 20.0

    # 4. Resources / Funding (10%)
    funding_cap = industry.get("funding_capability", "Medium")
    if funding_cap == "High":
        res_score = 10.0
    elif funding_cap == "Medium":
        res_score = 8.0
    else:
        res_score = 6.0

    # 5. Location (10%)
    prob_district = (problem.get("district") or "").lower()
    ind_location = (industry.get("location") or "").lower()
    if prob_district and prob_district in ind_location:
        loc_score = 10.0
    else:
        loc_score = 7.0

    # 6. Previous Experience (5%)
    collabs = industry.get("previous_collaborations", [])
    collab_text = " ".join(collabs)
    collab_sim = cosine_similarity(prob_vec, compute_term_frequencies(tokenize(collab_text)))
    if any(k in collab_text.lower() for k in problem.get("keywords", [])):
        collab_sim = max(collab_sim, 0.80)
    exp_score = min(1.0, max(0.3, collab_sim)) * 5.0

    total_score = round(tech_score + domain_score + csr_score + res_score + loc_score + exp_score, 1)
    total_score = min(99.0, max(15.0, total_score))

    # Generate Explainable Reasons
    reasons = []
    matched_tech = [t for t in ind_tech if any(rt.lower() in t.lower() or t.lower() in rt.lower() for rt in req_tech)]
    if matched_tech:
        reasons.append(f"Technology match: {', '.join(matched_tech[:2])}")
    else:
        reasons.append(f"Sector synergy: {industry.get('sector', 'Industry Innovation')}")

    reasons.append(f"CSR / Impact alignment: {csr_areas[0] if csr_areas else 'Community Development'}")
    reasons.append(f"Funding & resource capability: {funding_cap} tier commercial & prototyping backing")

    if prob_district and prob_district in ind_location:
        reasons.append(f"Local operations located in {problem.get('district')}")
    else:
        reasons.append("Statewide deployment capability across Jharkhand")

    if collabs:
        reasons.append(f"Proven collaboration record: {collabs[0]}")

    return {
        "industry_id": industry.get("id") or industry.get("link"),
        "name": industry.get("name"),
        "sector": industry.get("sector"),
        "match_score": total_score,
        "breakdown": {
            "technology_score": round(tech_score, 1),
            "domain_score": round(domain_score, 1),
            "csr_score": round(csr_score, 1),
            "resource_score": round(res_score, 1),
            "location_score": round(loc_score, 1),
            "experience_score": round(exp_score, 1)
        },
        "reasons": reasons,
        "tech_resources": ind_tech[:3] if ind_tech else ["Engineering", "Prototyping"],
        "csr_focus": csr_areas[:2] if csr_areas else ["Community Welfare"],
        "funding_tier": funding_cap,
        "icon": industry.get("icon", "🏢")
    }


# =============================================================================
# AI CATEGORY DETECTION & REVERSE GEOCODING UTILITIES
# =============================================================================

JHARKHAND_DISTRICTS_COORDS = [
    {"name": "Bokaro", "lat": 23.6693, "lon": 86.1511},
    {"name": "Chatra", "lat": 24.2091, "lon": 84.8711},
    {"name": "Deoghar", "lat": 24.4826, "lon": 86.7000},
    {"name": "Dhanbad", "lat": 23.7957, "lon": 86.4304},
    {"name": "Dumka", "lat": 24.2677, "lon": 87.2494},
    {"name": "East Singhbhum", "lat": 22.8046, "lon": 86.2029},
    {"name": "Garhwa", "lat": 24.1614, "lon": 83.8055},
    {"name": "Giridih", "lat": 24.1852, "lon": 86.3090},
    {"name": "Godda", "lat": 24.8267, "lon": 87.2144},
    {"name": "Gumla", "lat": 23.0441, "lon": 84.5414},
    {"name": "Hazaribagh", "lat": 23.9966, "lon": 85.3644},
    {"name": "Jamtara", "lat": 23.9631, "lon": 86.8028},
    {"name": "Khunti", "lat": 23.0728, "lon": 85.2796},
    {"name": "Koderma", "lat": 24.4673, "lon": 85.5944},
    {"name": "Latehar", "lat": 23.7431, "lon": 84.5028},
    {"name": "Lohardaga", "lat": 23.4398, "lon": 84.6798},
    {"name": "Pakur", "lat": 24.6333, "lon": 87.8497},
    {"name": "Palamu", "lat": 24.0384, "lon": 84.0700},
    {"name": "Ramgarh", "lat": 23.6322, "lon": 85.5147},
    {"name": "Ranchi", "lat": 23.3441, "lon": 85.3096},
    {"name": "Sahibganj", "lat": 25.2425, "lon": 87.6433},
    {"name": "Sarikela Kharsawan", "lat": 22.7006, "lon": 85.9304},
    {"name": "Simdega", "lat": 22.6146, "lon": 84.5034},
    {"name": "West Singhbhum", "lat": 22.5658, "lon": 85.8080}
]

CATEGORY_KNOWLEDGE = {
    "Water Management": {
        "phrases": [
            "clean drinking water", "drinking water", "water shortage", "water crisis",
            "no clean drinking water", "water supply", "pipeline leakage", "polluted drinking water",
            "water contamination", "handpump broken", "borewell dried", "tap water", "jal jeevan",
            "irrigation canal", "groundwater level", "fluoride contamination", "arsenic water",
            "shortage of water", "lack of drinking water"
        ],
        "keywords": [
            "water", "drinking", "pipeline", "pipelines", "well", "wells", "borewell", "handpump",
            "tap", "taps", "river", "pond", "ponds", "aquifer", "filtration", "purification",
            "scarcity", "shortage", "tanker", "tankers", "contamination", "chlorination", "arsenic", "fluoride", "jal"
        ]
    },
    "Education": {
        "phrases": [
            "proper classrooms", "no proper classrooms", "teacher shortage", "school building",
            "students in our village", "digital classroom", "smart class", "study material",
            "primary school", "high school", "desk and bench", "tribal literacy", "books shortage"
        ],
        "keywords": [
            "school", "schools", "teacher", "teachers", "student", "students", "education", "college",
            "classroom", "classrooms", "blackboard", "desk", "desks", "bench", "benches", "books",
            "uniforms", "literacy", "tuition", "syllabus", "exam", "learning", "curriculum", "study"
        ]
    },
    "Healthcare": {
        "phrases": [
            "primary health centre", "health centre", "no essential facilities", "medical facilities",
            "doctor shortage", "hospital beds", "ambulance service", "maternal health",
            "malnutrition children", "health clinic", "emergency medical", "vaccination center"
        ],
        "keywords": [
            "hospital", "hospitals", "clinic", "doctor", "doctors", "medicine", "medicines", "health",
            "patient", "patients", "nurse", "nurses", "phc", "chc", "ambulance", "treatment",
            "disease", "diseases", "vaccine", "malnutrition", "pharmacy", "diagnostic", "medical", "first aid"
        ]
    },
    "Agriculture": {
        "phrases": [
            "crop irrigation", "facing crop irrigation", "crop failure", "farmers are facing",
            "drip irrigation", "soil fertility", "cold storage", "harvest loss", "paddy crop",
            "monsoon failure", "seed shortage", "fertilizer scarcity", "plateau farming"
        ],
        "keywords": [
            "farmer", "farmers", "crop", "crops", "farming", "irrigation", "agriculture", "field",
            "fields", "harvest", "seed", "seeds", "fertilizer", "fertilizers", "pesticide", "monsoon",
            "drought", "kisan", "cultivation", "tractor", "soil", "paddy", "agritech"
        ]
    },
    "Sanitation": {
        "phrases": [
            "garbage is not being collected", "garbage not collected", "waste collection",
            "solid waste", "overflowing drain", "waste disposal", "sewage treatment", "open defecation",
            "public toilet", "garbage dump", "safai karmi", "stagnant water drain"
        ],
        "keywords": [
            "garbage", "waste", "sanitation", "drain", "drains", "drainage", "sewage", "trash",
            "dump", "dumping", "toilet", "toilets", "cleanliness", "swachh", "cleaning", "safai",
            "litter", "stench", "manhole", "composting", "filth"
        ]
    },
    "Environment": {
        "phrases": [
            "river water is becoming polluted", "river polluted", "air pollution", "forest conservation",
            "industrial pollution", "mine tailings", "plastic waste", "tree felling", "illegal mining",
            "industrial effluent", "air quality degraded", "soil erosion"
        ],
        "keywords": [
            "environment", "pollution", "polluted", "river", "rivers", "forest", "forests", "trees",
            "ecology", "plastic", "smog", "air quality", "emissions", "wildlife", "conservation",
            "biodiversity", "effluent", "slag", "smoke", "carbon"
        ]
    },
    "Energy": {
        "phrases": [
            "electricity supply", "facing electricity supply", "power supply problems", "power cut",
            "power outage", "low voltage", "solar microgrid", "frequent blackout", "transformer burnt",
            "no electricity in village", "transmission line fault"
        ],
        "keywords": [
            "electricity", "power", "energy", "voltage", "blackout", "load shedding", "transformer",
            "grid", "feeder", "wire", "electric", "pole", "solar", "substation", "transmission",
            "current", "light", "meter"
        ]
    },
    "Urban Infrastructure": {
        "phrases": [
            "roads are damaged", "damaged after heavy rainfall", "potholes on road", "broken bridge",
            "street lights not working", "pedestrian pathway", "traffic congestion", "water logging on roads",
            "damaged culvert", "footpath encroached", "urban roads"
        ],
        "keywords": [
            "road", "roads", "street", "streets", "bridge", "pothole", "potholes", "infrastructure",
            "flyover", "pavement", "sidewalk", "streetlight", "lights", "asphalt", "culvert",
            "highway", "traffic", "damaged", "repair", "tar"
        ]
    },
    "Rural Livelihoods": {
        "phrases": [
            "rural livelihood", "tribal artisans", "handloom weavers", "cottage industry",
            "dairy cooperative", "self-help group", "poultry farming", "unemployment in village",
            "tussar silk marketing", "sohrai art direct sale"
        ],
        "keywords": [
            "livelihood", "artisan", "artisans", "handloom", "tussar", "silk", "craft", "shg",
            "poultry", "livestock", "weaving", "goat", "cattle", "cottage", "mgnrega",
            "employment", "income", "handicrafts", "cooperative"
        ]
    },
    "Accessibility": {
        "phrases": [
            "wheelchair accessible", "disabled persons", "barrier free", "visually impaired",
            "special needs", "ramp required", "braille signage", "handicapped access"
        ],
        "keywords": [
            "disabled", "disability", "wheelchair", "ramp", "ramps", "accessibility", "accessible",
            "blind", "deaf", "handicapped", "braille", "impairment", "barrier-free", "inclusive"
        ]
    },
    "Public Services": {
        "phrases": [
            "ration card issue", "pension delay", "birth certificate", "panchayat office",
            "public services delivery", "caste certificate", "land records mutation", "block office delay"
        ],
        "keywords": [
            "ration", "pension", "certificate", "aadhaar", "panchayat", "bureaucracy", "corruption",
            "block", "scheme", "delivery", "public services", "welfare", "entitlement", "bdo"
        ]
    },
    "Disaster Management": {
        "phrases": [
            "flash flood", "heavy rainfall", "landslide disaster", "cyclone relief",
            "emergency rescue", "village inundated", "submerged under water", "calamity relief"
        ],
        "keywords": [
            "flood", "floods", "flooding", "disaster", "rainfall", "cyclone", "landslide", "earthquake",
            "calamity", "rescue", "evacuation", "emergency", "relief", "inundated", "submerged"
        ]
    }
}


def detect_category_ai(title: str, description: str = "") -> Dict[str, Any]:
    """
    Lightweight NLP & Semantic Category Detector.
    Analyzes both title and description using exact phrases, token matching, and scoring.
    Returns: category, confidence, keywords, suggestions, is_confident.
    """
    full_text = f"{title} {description}".strip()
    if not full_text:
        return {
            "category": "Other",
            "confidence": 0.0,
            "keywords": [],
            "suggestions": [],
            "is_confident": False
        }

    title_lower = title.lower()
    desc_lower = description.lower()

    category_scores: List[Dict[str, Any]] = []

    for cat_name, data in CATEGORY_KNOWLEDGE.items():
        score = 0.0
        matched_kws: List[str] = []

        # 1. Exact phrase matches (High weight)
        for phrase in data["phrases"]:
            p_lower = phrase.lower()
            if p_lower in title_lower:
                score += 48.0
                matched_kws.append(phrase)
            elif p_lower in desc_lower:
                score += 26.0
                matched_kws.append(phrase)

        # 2. Keyword matches
        for kw in data["keywords"]:
            kw_lower = kw.lower()
            if kw_lower in title_lower:
                score += 15.0
                if kw_lower not in matched_kws:
                    matched_kws.append(kw_lower)
            elif kw_lower in desc_lower:
                score += 8.0
                if kw_lower not in matched_kws:
                    matched_kws.append(kw_lower)

        # 3. Category Name mentioned
        if cat_name.lower() in title_lower:
            score += 35.0
            matched_kws.append(cat_name.lower())

        category_scores.append({
            "category": cat_name,
            "score": score,
            "keywords": list(dict.fromkeys(matched_kws))
        })

    category_scores.sort(key=lambda x: x["score"], reverse=True)
    top = category_scores[0]
    second = category_scores[1] if len(category_scores) > 1 else None

    if top["score"] > 0:
        detected_category = top["category"]
        keywords_found = top["keywords"][:5]

        if top["score"] >= 45:
            confidence = min(0.96, 0.85 + (top["score"] - 45) * 0.003)
        elif top["score"] >= 20:
            confidence = 0.55 + (top["score"] - 20) * 0.008
        else:
            confidence = 0.25 + top["score"] * 0.01

        if second and second["score"] > 0 and (top["score"] - second["score"]) < 10:
            confidence = max(0.45, confidence * 0.82)
    else:
        detected_category = "Other"
        confidence = 0.15
        keywords_found = []

    confidence = round(confidence, 2)

    suggestions = []
    for c in category_scores[:3]:
        if c["score"] > 0:
            c_conf = round(min(0.95, (c["score"] / (top["score"] or 1.0)) * confidence), 2)
            suggestions.append({
                "category": c["category"],
                "confidence": c_conf,
                "keywords": c["keywords"][:3]
            })

    return {
        "category": detected_category,
        "confidence": confidence,
        "keywords": keywords_found,
        "suggestions": suggestions,
        "is_confident": confidence >= 0.65
    }


def reverse_geocode_coordinates(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse geocoding helper using exact 24-district centroids and geospatial proximity.
    """
    min_dist = float("inf")
    closest_district = None

    for d in JHARKHAND_DISTRICTS_COORDS:
        d_lat = (d["lat"] - lat) * 111.0
        d_lon = (d["lon"] - lon) * 111.0 * math.cos(math.radians(lat))
        dist_km = math.sqrt(d_lat * d_lat + d_lon * d_lon)

        if dist_km < min_dist:
            min_dist = dist_km
            closest_district = d["name"]

    if closest_district and min_dist < 180.0:
        return {
            "district": closest_district,
            "state": "Jharkhand",
            "latitude": lat,
            "longitude": lon,
            "distance_km": round(min_dist, 2),
            "address": f"{closest_district} District, Jharkhand, India"
        }

    return {
        "district": None,
        "state": "Unknown",
        "latitude": lat,
        "longitude": lon,
        "distance_km": round(min_dist, 2),
        "address": "Coordinates outside Jharkhand boundary"
    }


# =============================================================================
# 4. LOCATION-BASED FRAUD & MISMATCH DETECTION ENGINE
# =============================================================================

LOCATION_VERIFICATION_CONFIG = {
    # Distance thresholds in meters
    "CONSISTENT_METERS": 100.0,         # 0-100m: Consistent
    "MINOR_DIFFERENCE_METERS": 1000.0,  # 100m-1km: Minor difference
    "MISMATCH_METERS": 5000.0,          # 1km-5km: Mismatch
    # Distance thresholds in kilometers for legacy callers
    "NORMAL_THRESHOLD_KM": 0.1,
    "LOW_CONCERN_THRESHOLD_KM": 1.0,
    "MODERATE_CONCERN_THRESHOLD_KM": 5.0,
    # Suspicion score ranges
    "MIN_SUSPICION": 0.05,
    "MAX_SUSPICION": 0.95
}

def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers
    using the Haversine formula.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0
    R = 6371.0  # Earth mean radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return round(R * c, 2)


def calculate_haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great circle distance in meters using Haversine formula.
    """
    return calculate_haversine_distance_km(lat1, lon1, lat2, lon2) * 1000.0


def verify_location_consistency(
    current_lat: float | None,
    current_lon: float | None,
    reported_lat: float | None,
    reported_lon: float | None,
    current_accuracy: float | None = 10.0
) -> Dict[str, Any]:
    """
    Evaluates physical consistency between user's actual GPS position and reported problem location.
    Calculates explainable suspicion score and verification requirements.
    DOES NOT accuse user of fraud or reject complaints; flags for administrative review when appropriate.
    """
    # Edge case: GPS unavailable / permission denied
    if current_lat is None or current_lon is None:
        rep_geo = reverse_geocode_coordinates(reported_lat, reported_lon) if reported_lat is not None and reported_lon is not None else {"district": "Unknown", "address": "Manual Location"}
        return {
            "distance_meters": None,
            "distance_km": None,
            "location_status": "Current GPS not available",
            "verification_status": "Manual Location Accepted",
            "status_label": "GPS Unavailable",
            "suspicion_score": 0.0,
            "suspicion_percentage": 0,
            "verification_required": False,
            "current_location": "GPS Permission Not Granted / Unavailable",
            "reported_location": rep_geo.get("district") or rep_geo.get("address") or "Selected Location",
            "message": "Current GPS not available. Complaint submitted with manual location without penalty.",
            "is_mismatch": False,
            "badge_type": "neutral"
        }

    # Edge case: Reported coordinates missing
    if reported_lat is None or reported_lon is None:
        cur_geo = reverse_geocode_coordinates(current_lat, current_lon)
        return {
            "distance_meters": None,
            "distance_km": None,
            "location_status": "Reported location not selected",
            "verification_status": "Awaiting Location Pin",
            "status_label": "Location Not Dropped",
            "suspicion_score": 0.0,
            "suspicion_percentage": 0,
            "verification_required": False,
            "current_location": cur_geo.get("district") or "Current GPS",
            "reported_location": "Location Pending",
            "message": "Problem coordinates not set yet.",
            "is_mismatch": False,
            "badge_type": "neutral"
        }

    # Calculate real Haversine distance
    distance_km = calculate_haversine_distance_km(current_lat, current_lon, reported_lat, reported_lon)
    distance_meters = round(distance_km * 1000.0, 1)

    cur_geo = reverse_geocode_coordinates(current_lat, current_lon)
    rep_geo = reverse_geocode_coordinates(reported_lat, reported_lon)
    cur_name = cur_geo.get("district") or f"{current_lat:.3f}, {current_lon:.3f}"
    rep_name = rep_geo.get("district") or f"{reported_lat:.3f}, {reported_lon:.3f}"

    acc_radius = float(current_accuracy) if current_accuracy is not None else 10.0
    is_within_accuracy = distance_meters <= acc_radius

    th_consistent = LOCATION_VERIFICATION_CONFIG["CONSISTENT_METERS"]
    th_minor = LOCATION_VERIFICATION_CONFIG["MINOR_DIFFERENCE_METERS"]
    th_mismatch = LOCATION_VERIFICATION_CONFIG["MISMATCH_METERS"]

    if is_within_accuracy or distance_meters <= th_consistent:
        status = "🟢 Location Consistent"
        verification_status = "Automatically Verified"
        status_label = "Location Consistent"
        suspicion = 0.05
        verification_required = False
        message = "Within GPS accuracy range — automatically verified." if is_within_accuracy else "Location consistent with device GPS."
        badge_type = "verified"
        is_mismatch = False

    elif distance_meters <= th_minor:
        status = "🟡 Minor Location Difference"
        verification_status = "Manual Verification Recommended"
        status_label = "Minor Location Difference"
        suspicion = 0.25
        verification_required = False
        message = "Minor location deviation from device GPS."
        badge_type = "low"
        is_mismatch = False

    elif distance_meters <= th_mismatch:
        status = "🟠 Location Mismatch"
        verification_status = "Additional Verification Required"
        status_label = "Location Mismatch"
        suspicion = 0.45
        verification_required = True
        message = "Reported location differs from device GPS. Routine review recommended."
        badge_type = "warning"
        is_mismatch = True

    else:
        status = "🔴 High Location Difference"
        verification_status = "Human Review Recommended"
        status_label = "High Verification Risk"
        suspicion = 0.75
        verification_required = True
        message = "Location differs from current GPS — verification may be required."
        badge_type = "danger"
        is_mismatch = True

    return {
        "distance_meters": distance_meters,
        "distance_km": distance_km,
        "location_status": status,
        "verification_status": verification_status,
        "status_label": status_label,
        "suspicion_score": suspicion,
        "suspicion_percentage": int(suspicion * 100),
        "verification_required": verification_required,
        "current_location": cur_name,
        "reported_location": rep_name,
        "message": message,
        "is_mismatch": is_mismatch,
        "is_within_accuracy": is_within_accuracy,
        "badge_type": badge_type
    }


# =============================================================================
# 5. MULTI-SIGNAL DUPLICATE REPORT DETECTION ENGINE
# =============================================================================

DUPLICATE_CONFIG = {
    "WEIGHTS": {
        "title": 0.35,
        "description": 0.25,
        "category": 0.15,
        "location": 0.20,
        "status_recency": 0.05
    },
    "THRESHOLDS": {
        "NO_DUPLICATE_MAX": 0.59,      # 0 - 59%: No duplicate
        "SIMILAR_MIN": 0.60,           # 60 - 79%: Similar report found
        "DUPLICATE_MIN": 0.80          # 80 - 100%: Possible duplicate report
    }
}

def normalize_category_name(cat: str) -> str:
    """Normalize category aliases for consistent comparison."""
    if not cat:
        return "Other"
    c = cat.strip().lower()
    if "water" in c:
        return "Water Management"
    if "school" in c or "edu" in c:
        return "Education"
    if "health" in c or "medic" in c:
        return "Healthcare"
    if "agri" in c or "crop" in c or "farm" in c:
        return "Agriculture"
    if "sanit" in c or "waste" in c or "garbage" in c:
        return "Sanitation"
    if "road" in c or "bridge" in c or "infra" in c or "urban" in c:
        return "Urban Infrastructure"
    if "energy" in c or "electric" in c or "power" in c:
        return "Energy"
    if "forest" in c or "pollut" in c or "environ" in c:
        return "Environment"
    if "livelihood" in c or "tribal" in c or "artisan" in c:
        return "Rural Livelihoods"
    return cat.strip()


def calculate_duplicate_score(new_report: Dict[str, Any], existing_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes explainable duplicate similarity between a new draft report and an existing database report.
    Signals:
    1. Title Similarity (35%)
    2. Description Similarity (25%)
    3. Category Match (15%)
    4. Geographic Proximity (20%)
    5. Status / Recency (5%)
    """
    matching_reasons: List[str] = []

    # 1. Title Similarity
    new_title = new_report.get("title", "").strip()
    exist_title = existing_report.get("title", "").strip()
    toks_new_t = tokenize(new_title)
    toks_ext_t = tokenize(exist_title)

    tf_new_t = compute_term_frequencies(toks_new_t)
    tf_ext_t = compute_term_frequencies(toks_ext_t)
    title_cosine = cosine_similarity(tf_new_t, tf_ext_t)
    title_jaccard = calculate_jaccard(toks_new_t, toks_ext_t)
    title_sim = round(0.70 * title_cosine + 0.30 * title_jaccard, 3)

    if title_sim >= 0.70:
        matching_reasons.append(f"High title similarity ({int(title_sim * 100)}%)")
    elif title_sim >= 0.40:
        matching_reasons.append(f"Moderate title overlap ({int(title_sim * 100)}%)")

    # 2. Description Similarity
    new_desc = new_report.get("description", "").strip()
    exist_desc = existing_report.get("description", "").strip()
    toks_new_d = tokenize(new_desc)
    toks_ext_d = tokenize(exist_desc)

    if toks_new_d and toks_ext_d:
        tf_new_d = compute_term_frequencies(toks_new_d)
        tf_ext_d = compute_term_frequencies(toks_ext_d)
        desc_cosine = cosine_similarity(tf_new_d, tf_ext_d)
        desc_jaccard = calculate_jaccard(toks_new_d, toks_ext_d)
        desc_sim = round(0.75 * desc_cosine + 0.25 * desc_jaccard, 3)
    else:
        # Fall back to title sim if descriptions are sparse
        desc_sim = title_sim

    if desc_sim >= 0.65:
        matching_reasons.append(f"Strong problem description match ({int(desc_sim * 100)}%)")

    # 3. Category Match
    cat_new = normalize_category_name(new_report.get("category", ""))
    cat_ext = normalize_category_name(existing_report.get("category", ""))

    if cat_new and cat_ext and cat_new.lower() == cat_ext.lower():
        cat_sim = 1.0
        matching_reasons.append(f"Identical category: {cat_new}")
    elif cat_new and cat_ext and (cat_new.lower() in cat_ext.lower() or cat_ext.lower() in cat_new.lower()):
        cat_sim = 0.70
        matching_reasons.append(f"Related category: {cat_new} / {cat_ext}")
    else:
        cat_sim = 0.0

    # 4. Geographic Proximity
    new_lat = new_report.get("latitude")
    new_lon = new_report.get("longitude")
    ext_lat = existing_report.get("latitude")
    ext_lon = existing_report.get("longitude")

    distance_km = None
    geo_sim = 0.0

    if new_lat is not None and new_lon is not None and ext_lat is not None and ext_lon is not None:
        try:
            distance_km = calculate_haversine_distance_km(float(new_lat), float(new_lon), float(ext_lat), float(ext_lon))
            if distance_km <= 0.50:
                geo_sim = 1.0
                dist_str = f"{int(distance_km * 1000)} meters"
                matching_reasons.append(f"Immediate vicinity ({dist_str})")
            elif distance_km <= 2.0:
                geo_sim = round(1.0 - ((distance_km - 0.50) / 1.50) * 0.35, 3)
                matching_reasons.append(f"Nearby location ({distance_km:.1f} km)")
            elif distance_km <= 10.0:
                geo_sim = round(0.65 - ((distance_km - 2.0) / 8.0) * 0.35, 3)
                matching_reasons.append(f"Same local area ({distance_km:.1f} km)")
            elif distance_km <= 30.0:
                geo_sim = round(0.30 - ((distance_km - 10.0) / 20.0) * 0.25, 3)
            else:
                # Far away (>30 km) -> geographic proximity is 0
                geo_sim = 0.0
        except (ValueError, TypeError):
            pass

    # Fallback to district matching if coordinates unavailable
    if distance_km is None:
        dist_new = (new_report.get("district") or "").strip().lower()
        dist_ext = (existing_report.get("district") or "").strip().lower()
        if dist_new and dist_ext and dist_new == dist_ext:
            geo_sim = 0.60
            matching_reasons.append(f"Same district: {new_report.get('district')}")
        else:
            geo_sim = 0.0

    # 5. Status / Recency Match
    status = (existing_report.get("status") or "Pending").strip()
    if status.lower() in ["pending", "in progress"]:
        status_sim = 1.0
        matching_reasons.append(f"Active unresolved community issue (Status: {status})")
    else:
        status_sim = 0.35

    # Combine weighted score
    w = DUPLICATE_CONFIG["WEIGHTS"]
    raw_score = (
        w["title"] * title_sim +
        w["description"] * desc_sim +
        w["category"] * cat_sim +
        w["location"] * geo_sim +
        w["status_recency"] * status_sim
    )

    # LOCATION BOUNDARY PROTECTION (TEST 4):
    # If the problems are far apart (>30 km or different districts) even with similar wording,
    # prevent false positive duplicate classification!
    if distance_km is not None and distance_km > 30.0:
        raw_score = min(0.68, raw_score * 0.75)
    elif distance_km is None:
        dist_new = (new_report.get("district") or "").strip().lower()
        dist_ext = (existing_report.get("district") or "").strip().lower()
        if dist_new and dist_ext and dist_new != dist_ext:
            raw_score = min(0.68, raw_score * 0.75)

    # ZERO CATEGORY PENALTY (TEST 5):
    # If category completely differs and title similarity is low, duplicate score is minimal
    if cat_sim == 0.0 and title_sim < 0.40:
        raw_score = min(0.35, raw_score)

    final_score = round(min(0.99, max(0.0, raw_score)), 2)

    return {
        "duplicate_score": final_score,
        "duplicate_percentage": int(final_score * 100),
        "title_similarity": round(title_sim, 2),
        "description_similarity": round(desc_sim, 2),
        "category_match": cat_sim > 0,
        "distance_km": distance_km,
        "matching_reasons": matching_reasons
    }


def detect_duplicate_reports(new_report: Dict[str, Any], existing_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates new draft report against all existing reports in database to detect duplicate or similar submissions.
    Returns:
    - is_duplicate: bool
    - duplicate_level: "none" | "similar" | "possible_duplicate"
    - duplicate_score: float (0.0 to 1.0)
    - existing_report: matched report dict or None
    - matching_reasons: list of explainable reasons
    """
    if not existing_reports or not new_report.get("title", "").strip():
        return {
            "is_duplicate": False,
            "duplicate_level": "none",
            "duplicate_score": 0.0,
            "duplicate_percentage": 0,
            "existing_report": None,
            "matching_reasons": [],
            "candidates": []
        }

    evaluated: List[Dict[str, Any]] = []

    for ext in existing_reports:
        # Don't compare a problem against itself if an ID matches
        if new_report.get("id") and ext.get("id") == new_report.get("id"):
            continue

        score_res = calculate_duplicate_score(new_report, ext)
        score = score_res["duplicate_score"]

        evaluated.append({
            "existing_report": {
                "id": ext.get("id"),
                "title": ext.get("title"),
                "category": ext.get("category"),
                "district": ext.get("district"),
                "location": ext.get("location"),
                "status": ext.get("status", "Pending"),
                "support_count": ext.get("support_count", 1),
                "distance_km": score_res["distance_km"]
            },
            "duplicate_score": score,
            "duplicate_percentage": score_res["duplicate_percentage"],
            "title_similarity": score_res["title_similarity"],
            "matching_reasons": score_res["matching_reasons"]
        })

    evaluated.sort(key=lambda x: x["duplicate_score"], reverse=True)

    if not evaluated:
        return {
            "is_duplicate": False,
            "duplicate_level": "none",
            "duplicate_score": 0.0,
            "duplicate_percentage": 0,
            "existing_report": None,
            "matching_reasons": [],
            "candidates": []
        }

    top = evaluated[0]
    top_score = top["duplicate_score"]

    if top_score >= DUPLICATE_CONFIG["THRESHOLDS"]["DUPLICATE_MIN"]:
        dup_level = "possible_duplicate"
        is_dup = True
    elif top_score >= DUPLICATE_CONFIG["THRESHOLDS"]["SIMILAR_MIN"]:
        dup_level = "similar"
        is_dup = True
    else:
        dup_level = "none"
        is_dup = False

    return {
        "is_duplicate": is_dup,
        "duplicate_level": dup_level,
        "duplicate_score": top_score,
        "duplicate_percentage": int(top_score * 100),
        "existing_report": top["existing_report"] if is_dup else None,
        "matching_reasons": top["matching_reasons"] if is_dup else [],
        "candidates": evaluated[:3]
    }


