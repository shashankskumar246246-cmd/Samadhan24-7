/* =====================================
   PAGE NAVIGATION
===================================== */

function showPage(pageId, element = null) {

    // Guard against navigation if user is logged out
    if (typeof isUserLoggedIn === "function" && !isUserLoggedIn()) {
        const loginOverlay = document.getElementById("loginOverlayView");
        if (loginOverlay) {
            loginOverlay.classList.add("active");
            document.body.style.overflow = "hidden";
        }
        return;
    }

    const pages = document.querySelectorAll(".page");

    pages.forEach(page => {

        page.classList.remove("active-page");

    });


    const selectedPage = document.getElementById(pageId);

    if (selectedPage) {

        selectedPage.classList.add("active-page");

    }


    const navLinks = document.querySelectorAll(".nav-link");

    navLinks.forEach(link => {

        link.classList.remove("active");

    });


    // Auto-locate sidebar link if element not passed directly
    if (!element) {
        element = document.querySelector(`.sidebar .nav-link[onclick*="'${pageId}'"]`) ||
                  document.querySelector(`.sidebar .nav-link[onclick*='"${pageId}"']`) ||
                  document.querySelector(`.sidebar-menu .nav-link[onclick*="'${pageId}'"]`) ||
                  document.querySelector(`.sidebar-menu .nav-link[onclick*='"${pageId}"']`);
    }

    if (element) {

        element.classList.add("active");

    }


    const mainEl = document.querySelector(".main");
    if (mainEl) {
        mainEl.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }

    window.scrollTo({

        top: 0,
        behavior: "smooth"

    });


    // Close mobile sidebar if open on smaller devices

    const sidebar = document.querySelector(".sidebar");
    if (sidebar) {
        sidebar.classList.remove("open");
    }

    // Invalidate / initialize map when navigating to Submit Problem page
    if (pageId === "submit") {
        if (!problemLeafletMap) {
            if (typeof initProblemLocationMap === "function") initProblemLocationMap();
        } else {
            if (typeof invalidateProblemMap === "function") invalidateProblemMap();
        }
        setTimeout(() => { if (typeof invalidateProblemMap === "function") invalidateProblemMap(); }, 80);
        setTimeout(() => { if (typeof invalidateProblemMap === "function") invalidateProblemMap(); }, 250);
        setTimeout(() => { if (typeof invalidateProblemMap === "function") invalidateProblemMap(); }, 500);
    }

    if (pageId === "dashboard") {
        if (typeof updateIntegrityDashboardStats === "function") updateIntegrityDashboardStats();
        if (typeof updateDomainStatistics === "function") updateDomainStatistics();
    }

}



/* =====================================
   SIDEBAR COLLAPSE & MOBILE DRAWER
===================================== */

function toggleSidebarCollapse() {
    const isCollapsed = document.body.classList.toggle("sidebar-collapsed");
    try {
        localStorage.setItem("samadhan_sidebar_collapsed", isCollapsed ? "true" : "false");
    } catch (e) {}

    // Invalidate Leaflet map size if visible after transition
    if (typeof invalidateProblemMap === "function") {
        setTimeout(invalidateProblemMap, 260);
    }
}

function initSidebarState() {
    try {
        if (localStorage.getItem("samadhan_sidebar_collapsed") === "true") {
            document.body.classList.add("sidebar-collapsed");
        }
    } catch (e) {}
}

function toggleSidebar() {
    const sidebar = document.querySelector(".sidebar");
    if (sidebar) {
        sidebar.classList.toggle("open");
    }
    if (typeof invalidateProblemMap === "function") {
        setTimeout(invalidateProblemMap, 260);
    }
}


/* =====================================
   TOAST
===================================== */

function showToast(message) {

    const toast =
        document.getElementById("toast");

    const toastMessage =
        document.getElementById("toastMessage");


    toastMessage.textContent = message;

    toast.classList.add("show");


    setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);

}


/* =====================================
   FILE UPLOAD
===================================== */

const evidence =
    document.getElementById("evidence");


if (evidence) {

    evidence.addEventListener("change", function () {

        const fileList =
            document.getElementById("fileList");

        fileList.innerHTML = "";


        if (this.files.length === 0) {

            return;

        }


        Array.from(this.files).forEach(file => {

            const div =
                document.createElement("div");

            div.style.margin = "5px";

            div.innerHTML =
                `📎 ${file.name}`;

            fileList.appendChild(div);

        });

    });

}


/* ==========================================================================
   AI AUTO CATEGORY DETECTION & SMART LOCATION ENGINE
   ========================================================================== */

// 1. All 24 Jharkhand District Centroids (for precise offline / fallback geocoding)
const JHARKHAND_DISTRICTS = [
    { name: "Bokaro", lat: 23.6693, lon: 86.1511 },
    { name: "Chatra", lat: 24.2091, lon: 84.8711 },
    { name: "Deoghar", lat: 24.4826, lon: 86.7000 },
    { name: "Dhanbad", lat: 23.7957, lon: 86.4304 },
    { name: "Dumka", lat: 24.2677, lon: 87.2494 },
    { name: "East Singhbhum", lat: 22.8046, lon: 86.2029 },
    { name: "Garhwa", lat: 24.1614, lon: 83.8055 },
    { name: "Giridih", lat: 24.1852, lon: 86.3090 },
    { name: "Godda", lat: 24.8267, lon: 87.2144 },
    { name: "Gumla", lat: 23.0441, lon: 84.5414 },
    { name: "Hazaribagh", lat: 23.9966, lon: 85.3644 },
    { name: "Jamtara", lat: 23.9631, lon: 86.8028 },
    { name: "Khunti", lat: 23.0728, lon: 85.2796 },
    { name: "Koderma", lat: 24.4673, lon: 85.5944 },
    { name: "Latehar", lat: 23.7431, lon: 84.5028 },
    { name: "Lohardaga", lat: 23.4398, lon: 84.6798 },
    { name: "Pakur", lat: 24.6333, lon: 87.8497 },
    { name: "Palamu", lat: 24.0384, lon: 84.0700 },
    { name: "Ramgarh", lat: 23.6322, lon: 85.5147 },
    { name: "Ranchi", lat: 23.3441, lon: 85.3096 },
    { name: "Sahibganj", lat: 25.2425, lon: 87.6433 },
    { name: "Sarikela Kharsawan", lat: 22.7006, lon: 85.9304 },
    { name: "Simdega", lat: 22.6146, lon: 84.5034 },
    { name: "West Singhbhum", lat: 22.5658, lon: 85.8080 }
];

// 2. Comprehensive AI Category Taxonomy & Semantic Vocabularies
const AI_CATEGORY_TAXONOMY = {
    "Water Management": {
        key: "Water Management",
        displayName: "Water Management",
        icon: "💧",
        phrases: [
            "clean drinking water", "drinking water", "water shortage", "water crisis",
            "no clean drinking water", "water supply", "pipeline leakage", "polluted drinking water",
            "water contamination", "handpump broken", "borewell dried", "tap water", "jal jeevan",
            "irrigation canal", "groundwater level", "fluoride contamination", "arsenic water",
            "shortage of water", "lack of drinking water", "clean water shortage", "scarcity of water"
        ],
        keywords: [
            "water", "drinking", "pipeline", "pipelines", "well", "wells", "borewell", "handpump",
            "tap", "taps", "river", "pond", "ponds", "aquifer", "filtration", "purification",
            "scarcity", "shortage", "tanker", "tankers", "contamination", "chlorination", "arsenic", "fluoride", "jal"
        ]
    },
    "Education": {
        key: "Education",
        displayName: "Education",
        icon: "🎓",
        phrases: [
            "proper classrooms", "no proper classrooms", "teacher shortage", "school building",
            "students in our village", "digital classroom", "smart class", "study material",
            "primary school", "high school", "desk and bench", "tribal literacy", "books shortage",
            "classroom facilities", "schools without electricity", "lack of teachers", "poor classrooms"
        ],
        keywords: [
            "school", "schools", "teacher", "teachers", "student", "students", "education", "college",
            "classroom", "classrooms", "blackboard", "desk", "desks", "bench", "benches", "books",
            "uniforms", "literacy", "tuition", "syllabus", "exam", "learning", "curriculum", "study"
        ]
    },
    "Healthcare": {
        key: "Healthcare",
        displayName: "Healthcare",
        icon: "🏥",
        phrases: [
            "primary health centre", "health centre", "no essential facilities", "medical facilities",
            "doctor shortage", "hospital beds", "ambulance service", "maternal health",
            "malnutrition children", "health clinic", "emergency medical", "vaccination center",
            "phc has no", "lack of medicines", "healthcare facilities", "sub health centre"
        ],
        keywords: [
            "hospital", "hospitals", "clinic", "doctor", "doctors", "medicine", "medicines", "health",
            "patient", "patients", "nurse", "nurses", "phc", "chc", "ambulance", "treatment",
            "disease", "diseases", "vaccine", "malnutrition", "pharmacy", "diagnostic", "medical", "first aid"
        ]
    },
    "Agriculture": {
        key: "Agriculture",
        displayName: "Agriculture",
        icon: "🌾",
        phrases: [
            "crop irrigation", "facing crop irrigation", "crop failure", "farmers are facing",
            "drip irrigation", "soil fertility", "cold storage", "harvest loss", "paddy crop",
            "monsoon failure", "seed shortage", "fertilizer scarcity", "plateau farming",
            "irrigation problems", "crop pest attack", "farmers in distress"
        ],
        keywords: [
            "farmer", "farmers", "crop", "crops", "farming", "irrigation", "agriculture", "field",
            "fields", "harvest", "seed", "seeds", "fertilizer", "fertilizers", "pesticide", "monsoon",
            "drought", "kisan", "cultivation", "tractor", "soil", "paddy", "agritech"
        ]
    },
    "Sanitation": {
        key: "Sanitation",
        displayName: "Sanitation",
        icon: "🧹",
        phrases: [
            "garbage is not being collected", "garbage not collected", "waste collection",
            "solid waste", "overflowing drain", "waste disposal", "sewage treatment", "open defecation",
            "public toilet", "garbage dump", "safai karmi", "stagnant water drain",
            "unhygienic conditions", "choked drainage", "sewer overflow", "cleaning problem"
        ],
        keywords: [
            "garbage", "waste", "sanitation", "drain", "drains", "drainage", "sewage", "trash",
            "dump", "dumping", "toilet", "toilets", "cleanliness", "swachh", "cleaning", "safai",
            "litter", "stench", "manhole", "composting", "filth"
        ]
    },
    "Environment": {
        key: "Environment",
        displayName: "Environment",
        icon: "🌳",
        phrases: [
            "river water is becoming polluted", "river polluted", "air pollution", "forest conservation",
            "industrial pollution", "mine tailings", "plastic waste", "tree felling", "illegal mining",
            "industrial effluent", "air quality degraded", "soil erosion", "polluted river", "smoke emission"
        ],
        keywords: [
            "environment", "pollution", "polluted", "river", "rivers", "forest", "forests", "trees",
            "ecology", "plastic", "smog", "air quality", "emissions", "wildlife", "conservation",
            "biodiversity", "effluent", "slag", "smoke", "carbon"
        ]
    },
    "Energy": {
        key: "Energy",
        displayName: "Energy",
        icon: "⚡",
        phrases: [
            "electricity supply", "facing electricity supply", "power supply problems", "power cut",
            "power outage", "low voltage", "solar microgrid", "frequent blackout", "transformer burnt",
            "no electricity in village", "transmission line fault", "frequent power cuts", "voltage fluctuation"
        ],
        keywords: [
            "electricity", "power", "energy", "voltage", "blackout", "load shedding", "transformer",
            "grid", "feeder", "wire", "electric", "pole", "solar", "substation", "transmission",
            "current", "light", "meter"
        ]
    },
    "Urban Infrastructure": {
        key: "Urban Infrastructure",
        displayName: "Urban Infrastructure",
        icon: "🏙️",
        phrases: [
            "roads are damaged", "damaged after heavy rainfall", "potholes on road", "broken bridge",
            "street lights not working", "pedestrian pathway", "traffic congestion", "water logging on roads",
            "damaged culvert", "footpath encroached", "urban roads", "damaged road", "cracked bridge"
        ],
        keywords: [
            "road", "roads", "street", "streets", "bridge", "pothole", "potholes", "infrastructure",
            "flyover", "pavement", "sidewalk", "streetlight", "lights", "asphalt", "culvert",
            "highway", "traffic", "damaged", "repair", "tar"
        ]
    },
    "Rural Livelihoods": {
        key: "Rural Livelihoods",
        displayName: "Rural Livelihoods",
        icon: "👨‍🌾",
        phrases: [
            "rural livelihood", "tribal artisans", "handloom weavers", "cottage industry",
            "dairy cooperative", "self-help group", "poultry farming", "unemployment in village",
            "tussar silk marketing", "sohrai art direct sale", "village livelihoods"
        ],
        keywords: [
            "livelihood", "artisan", "artisans", "handloom", "tussar", "silk", "craft", "shg",
            "poultry", "livestock", "weaving", "goat", "cattle", "cottage", "mgnrega",
            "employment", "income", "handicrafts", "cooperative"
        ]
    },
    "Accessibility": {
        key: "Accessibility",
        displayName: "Accessibility",
        icon: "♿",
        phrases: [
            "wheelchair accessible", "disabled persons", "barrier free", "visually impaired",
            "special needs", "ramp required", "braille signage", "handicapped access", "differently abled"
        ],
        keywords: [
            "disabled", "disability", "wheelchair", "ramp", "ramps", "accessibility", "accessible",
            "blind", "deaf", "handicapped", "braille", "impairment", "barrier-free", "inclusive"
        ]
    },
    "Public Services": {
        key: "Public Services",
        displayName: "Public Services",
        icon: "🏛️",
        phrases: [
            "ration card issue", "pension delay", "birth certificate", "panchayat office",
            "public services delivery", "caste certificate", "land records mutation", "block office delay",
            "government scheme delay", "ration distribution problem"
        ],
        keywords: [
            "ration", "pension", "certificate", "aadhaar", "panchayat", "bureaucracy", "corruption",
            "block", "scheme", "delivery", "public services", "welfare", "entitlement", "bdo"
        ]
    },
    "Disaster Management": {
        key: "Disaster Management",
        displayName: "Disaster Management",
        icon: "🚨",
        phrases: [
            "flash flood", "heavy rainfall", "landslide disaster", "cyclone relief",
            "emergency rescue", "village inundated", "submerged under water", "calamity relief",
            "flood relief needed", "river overflow flood"
        ],
        keywords: [
            "flood", "floods", "flooding", "disaster", "rainfall", "cyclone", "landslide", "earthquake",
            "calamity", "rescue", "evacuation", "emergency", "relief", "inundated", "submerged"
        ]
    },
    "Other": {
        key: "Other",
        displayName: "Other",
        icon: "💡",
        phrases: ["community issue", "other problem", "general issue"],
        keywords: ["problem", "issue", "community", "general", "other", "need", "village"]
    }
};

// State flags
let userManuallySelectedCategory = false;
let categoryDetectionTimer = null;
let nlpCategoryCache = {};

// Leaflet Map State & Browser Geolocation Controller
let problemLeafletMap = null;
let problemLocationMap = null; // backward-compatible alias
let problemMarker = null; // Draggable reported problem pin
let liveLocationMarker = null; // Separate Live GPS location marker
let accuracyCircle = null; // Live GPS Accuracy circle
let liveWatchId = null; // watchPosition tracking ID
let isLocationConfirmed = false;

// Backward-compatible aliases for existing references
let problemLocationMarker = null;
let userCurrentLocationMarker = null;
let userCurrentAccuracyCircle = null;
let leafletProblemMarker = null;
let leafletUserGpsMarker = null;
let leafletAccuracyCircle = null;
let liveLocationWatchId = null;

let selectedLocationDetails = {
    latitude: 23.3441,
    longitude: 85.3096,
    accuracy: null,
    state: "Jharkhand",
    district: "",
    locality: "",
    formatted_address: "",
    source: "manual",
    timestamp: null
};


/* --------------------------------------------------------------------------
   3. AI CATEGORY DETECTION ENGINE (NLP & SEMANTIC SCORING)
   -------------------------------------------------------------------------- */

function detectCategoryNLP(title, description = "") {
    const rawText = `${title} ${description}`.trim();
    if (!rawText) {
        return {
            category: "Other",
            confidence: 0,
            keywords: [],
            suggestions: [],
            isConfident: false
        };
    }

    const cacheKey = rawText.toLowerCase();
    if (nlpCategoryCache[cacheKey]) {
        return nlpCategoryCache[cacheKey];
    }

    const titleLower = title.toLowerCase();
    const descLower = description.toLowerCase();
    const fullLower = `${titleLower} ${descLower}`;

    // Tokenize full text into words
    const tokens = fullLower
        .replace(/[^a-z0-9\s]/g, " ")
        .split(/\s+/)
        .filter(w => w.length > 2 && !STOPWORDS_SET.has(w));

    const tokenSet = new Set(tokens);
    const categoryScores = [];

    for (const [catName, catData] of Object.entries(AI_CATEGORY_TAXONOMY)) {
        if (catName === "Other") continue;

        let score = 0;
        const matchedKeywords = [];

        // 1. Exact Phrase Matches in Title (Weight: 45) and Description (Weight: 25)
        for (const phrase of catData.phrases) {
            const pLower = phrase.toLowerCase();
            if (titleLower.includes(pLower)) {
                score += 48;
                matchedKeywords.push(phrase);
            } else if (descLower.includes(pLower)) {
                score += 26;
                matchedKeywords.push(phrase);
            }
        }

        // 2. Keyword Matches in Title (Weight: 14) and Description (Weight: 8)
        for (const kw of catData.keywords) {
            const kwLower = kw.toLowerCase();
            if (titleLower.includes(kwLower)) {
                score += 15;
                if (!matchedKeywords.includes(kwLower)) matchedKeywords.push(kwLower);
            } else if (descLower.includes(kwLower)) {
                score += 8;
                if (!matchedKeywords.includes(kwLower)) matchedKeywords.push(kwLower);
            }
        }

        // 3. Category Name itself in text
        if (titleLower.includes(catName.toLowerCase())) {
            score += 35;
            matchedKeywords.push(catName.toLowerCase());
        }

        categoryScores.push({
            category: catName,
            rawScore: score,
            matchedKeywords: [...new Set(matchedKeywords)]
        });
    }

    // Sort descending by score
    categoryScores.sort((a, b) => b.rawScore - a.rawScore);

    const top = categoryScores[0];
    const second = categoryScores[1];

    let confidence = 0;
    let detectedCategory = "Other";
    let keywordsFound = [];

    if (top && top.rawScore > 0) {
        detectedCategory = top.category;
        keywordsFound = top.matchedKeywords.slice(0, 5);

        // Normalize raw score to a smooth, explainable 0.00 - 0.98 scale
        if (top.rawScore >= 45) {
            // High confidence match (matches user prompt's ~92-96% requirement)
            confidence = Math.min(0.96, 0.85 + (top.rawScore - 45) * 0.003);
        } else if (top.rawScore >= 20) {
            // Moderate confidence (55% - 74%)
            confidence = 0.55 + (top.rawScore - 20) * 0.008;
        } else {
            // Low confidence (< 50%)
            confidence = 0.25 + top.rawScore * 0.01;
        }

        // If second highest is very close, slightly temper confidence (ambiguous)
        if (second && second.rawScore > 0 && (top.rawScore - second.rawScore) < 10) {
            confidence = Math.max(0.45, confidence * 0.82);
        }
    } else {
        detectedCategory = "Other";
        confidence = 0.15;
    }

    // Prepare top 3 suggestions
    const suggestions = categoryScores
        .filter(c => c.rawScore > 0)
        .slice(0, 3)
        .map(c => ({
            category: c.category,
            confidence: Math.round(Math.min(0.95, (c.rawScore / (top.rawScore || 1)) * confidence) * 100),
            keywords: c.matchedKeywords.slice(0, 3)
        }));

    const result = {
        category: detectedCategory,
        confidence: parseFloat(confidence.toFixed(2)),
        keywords: keywordsFound,
        suggestions: suggestions,
        isConfident: confidence >= 0.65
    };

    nlpCategoryCache[cacheKey] = result;
    return result;
}

// Backward-compatible signature
function detectCategory(text) {
    const res = detectCategoryNLP(text, "");
    return res.category || "General";
}

/* --------------------------------------------------------------------------
   4. UI REAL-TIME FEEDBACK & DEBOUNCED EVENT HANDLERS
   -------------------------------------------------------------------------- */

function handleProblemTextDebounced() {
    clearTimeout(categoryDetectionTimer);
    categoryDetectionTimer = setTimeout(() => {
        runAICategoryDetection();
        if (typeof triggerDuplicateDetectionDebounced === "function") {
            triggerDuplicateDetectionDebounced();
        }
    }, 320);
}

function runAICategoryDetection() {
    const titleInput = document.getElementById("problemTitle");
    const descInput = document.getElementById("description");
    const catSelect = document.getElementById("category");

    const title = titleInput ? titleInput.value.trim() : "";
    const description = descInput ? descInput.value.trim() : "";

    if (!title && !description) {
        const aiBox = document.getElementById("aiCategoryBox");
        if (aiBox) aiBox.style.display = "none";
        const hubCatName = document.getElementById("aiCatSummaryName");
        const hubCatConf = document.getElementById("aiCatSummaryConfidence");
        const hubCatTag = document.getElementById("aiCatSummaryTag");
        if (hubCatName) hubCatName.textContent = "Pending text input";
        if (hubCatConf) hubCatConf.textContent = "Confidence: --%";
        if (hubCatTag) {
            hubCatTag.textContent = "Awaiting Input";
            hubCatTag.className = "badge-status-neutral";
        }
        return;
    }

    const result = detectCategoryNLP(title, description);
    applyCategoryDetectionResult(result);
}

function applyCategoryDetectionResult(result) {
    const aiBox = document.getElementById("aiCategoryBox");
    const catSelect = document.getElementById("category");
    const catNameElem = document.getElementById("aiDetectedCatName");
    const confBadge = document.getElementById("aiConfidenceBadge");
    const confText = document.getElementById("aiConfidenceText");
    const confBar = document.getElementById("aiConfidenceBar");
    const statusTag = document.getElementById("aiCatStatusTag");
    const keywordsWrap = document.getElementById("aiKeywordsWrap");
    const keywordsList = document.getElementById("aiKeywordsList");
    const suggestionsWrap = document.getElementById("aiSuggestionsWrap");
    const suggestionsList = document.getElementById("aiSuggestionsList");
    const overrideHint = document.getElementById("categoryOverrideHint");

    // Sync AI Analysis Hub Card
    const hubCatName = document.getElementById("aiCatSummaryName");
    const hubCatConf = document.getElementById("aiCatSummaryConfidence");
    const hubCatTag = document.getElementById("aiCatSummaryTag");
    if (hubCatName) hubCatName.textContent = result.category;
    if (hubCatConf) hubCatConf.textContent = `Confidence: ${Math.round(result.confidence * 100)}%`;
    if (hubCatTag) {
        hubCatTag.textContent = result.isConfident ? "✓ Auto-detected" : "Review Recommended";
        hubCatTag.className = result.isConfident ? "badge-status-neutral" : "status-pill status-pill-warning";
    }

    if (!aiBox) return;

    aiBox.style.display = "block";
    const confPct = Math.round(result.confidence * 100);

    // Detected category title
    if (catNameElem) {
        catNameElem.textContent = result.category;
    }

    // Confidence Pill & Bar
    if (confText) {
        confText.textContent = `Confidence: ${confPct}%`;
    }
    if (confBar) {
        confBar.style.width = `${Math.max(8, confPct)}%`;
    }

    if (confBadge) {
        confBadge.className = "ai-confidence-pill";
        if (result.confidence >= 0.70) {
            confBadge.classList.add("high");
            if (confBar) confBar.style.background = "linear-gradient(90deg, #10b981, #059669)";
        } else if (result.confidence >= 0.45) {
            confBadge.classList.add("medium");
            if (confBar) confBar.style.background = "linear-gradient(90deg, #f59e0b, #d97706)";
        } else {
            confBadge.classList.add("low");
            if (confBar) confBar.style.background = "linear-gradient(90deg, #94a3b8, #64748b)";
        }
    }

    // Keywords Display
    if (keywordsWrap && keywordsList) {
        if (result.keywords && result.keywords.length > 0) {
            keywordsWrap.style.display = "flex";
            keywordsList.innerHTML = result.keywords.map(kw => `<span class="keyword-pill">#${kw}</span>`).join("");
        } else {
            keywordsWrap.style.display = "none";
        }
    }

    // Feature 2 & 12: Decision based on Confidence Threshold
    if (result.isConfident) {
        // High confidence (>= 65%): Auto-fill category if user hasn't overridden
        if (!userManuallySelectedCategory && catSelect) {
            // Find option or legacy alias
            catSelect.value = result.category;
            if (statusTag) {
                statusTag.textContent = "✓ Auto-filled";
                statusTag.style.background = "rgba(16, 185, 129, 0.15)";
                statusTag.style.color = "#059669";
            }
        }
        if (suggestionsWrap) suggestionsWrap.style.display = "none";
    } else if (result.confidence >= 0.35 && result.suggestions && result.suggestions.length > 0) {
        // Medium confidence (35% - 64%): Feature 12 - Do NOT blindly trust AI!
        if (statusTag) {
            statusTag.textContent = userManuallySelectedCategory ? "✓ User Selected" : "Needs Confirmation";
            statusTag.style.background = "rgba(245, 158, 11, 0.15)";
            statusTag.style.color = "#b45309";
        }

        // Render top 2-3 clickable suggestions for user confirmation
        if (suggestionsWrap && suggestionsList) {
            suggestionsWrap.style.display = "block";
            suggestionsList.innerHTML = result.suggestions.map((s, idx) => `
                <button type="button" class="category-suggestion-chip" onclick="selectSuggestedCategory('${s.category}')">
                    <span>${idx + 1}. ${s.category}</span>
                    <span class="chip-conf">${s.confidence}%</span>
                </button>
            `).join("");
        }
    } else {
        // Very low confidence (< 35%): Ask for manual selection
        if (statusTag) {
            statusTag.textContent = "Manual Selection";
            statusTag.style.background = "rgba(100, 116, 139, 0.15)";
            statusTag.style.color = "#475569";
        }
        if (suggestionsWrap && suggestionsList) {
            suggestionsWrap.style.display = "block";
            suggestionsList.innerHTML = `<span style="font-size: 0.8rem; color: #64748b;">Category could not be confidently detected. Please select it from the dropdown manually.</span>`;
        }
    }
}

function selectSuggestedCategory(catName) {
    const catSelect = document.getElementById("category");
    const overrideHint = document.getElementById("categoryOverrideHint");
    const statusTag = document.getElementById("aiCatStatusTag");
    const suggestionsWrap = document.getElementById("aiSuggestionsWrap");

    if (catSelect) {
        catSelect.value = catName;
    }
    userManuallySelectedCategory = true;

    if (overrideHint) overrideHint.style.display = "inline";
    if (statusTag) {
        statusTag.textContent = `✓ Selected: ${catName}`;
        statusTag.style.background = "rgba(16, 185, 129, 0.15)";
        statusTag.style.color = "#059669";
    }
    if (suggestionsWrap) {
        suggestionsWrap.style.display = "none";
    }
    showToast(`Category set to ${catName}`);
}

/* --------------------------------------------------------------------------
   5. LEAFLET.JS & SMART LOCATION CONTROLLER (OPENSTREETMAP / CARTO & BROWSER GPS)
   -------------------------------------------------------------------------- */

/**
 * Diagnostic status updater for GPS & Security environment (Step 10)
 */
function updateGpsDiagnosticStatus(statusText) {
    const statusEl = document.getElementById("diagGpsStatus");
    const secEl = document.getElementById("diagSecureContext");
    const geoEl = document.getElementById("diagGeoAvailable");

    if (statusEl) statusEl.textContent = statusText;
    if (secEl) secEl.textContent = window.isSecureContext ? "true (Secure)" : "false (Insecure)";
    if (geoEl) geoEl.textContent = ("geolocation" in navigator) ? "true (Available)" : "false (Unavailable)";
}

/**
 * Initialize single Leaflet Map instance on #problemLocationMap
 * Using OpenStreetMap tiles with CARTO attribution matching project design
 */
function initProblemLocationMap() {
    const mapContainer = document.getElementById("problemLocationMap");
    if (!mapContainer) return;

    // Guard: do not re-initialize the same map instance
    if (problemLeafletMap) {
        try {
            problemLeafletMap.invalidateSize({ animate: false, pan: false });
        } catch (e) {}
        return;
    }

    // Defer initialization if container is currently hidden (0x0 dimensions)
    if (mapContainer.offsetWidth === 0 && mapContainer.offsetHeight === 0) {
        return;
    }

    if (!window.L || typeof window.L.map !== "function") {
        console.error("Leaflet.js is required but not loaded.");
        return;
    }

    mapContainer.innerHTML = "";

    const defaultLat = selectedLocationDetails.latitude || 23.3441;
    const defaultLng = selectedLocationDetails.longitude || 85.3096;

    // 1. Create Leaflet map
    problemLeafletMap = L.map(mapContainer, {
        zoomControl: true,
        attributionControl: true
    }).setView([defaultLat, defaultLng], 12);

    // 2. OpenStreetMap / CARTO tile layer matching Image 2
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    }).addTo(problemLeafletMap);

    // 3. Problem Location Marker (Draggable)
    problemMarker = L.marker([defaultLat, defaultLng], {
        draggable: true,
        title: "Reported Problem Location (Drag to adjust)",
        zIndexOffset: 500
    }).addTo(problemLeafletMap);

    leafletProblemMarker = problemMarker;
    problemLocationMarker = problemMarker;

    problemMarker.bindPopup("<strong>📍 Reported Problem Location</strong><br>Drag marker or click anywhere to adjust.").openPopup();

    problemMarker.on("dragend", function (e) {
        const pos = e.target.getLatLng();
        setProblemLocation(pos.lat, pos.lng, true, "marker_drag");
    });

    // 4. Map Click Event: repositions Problem Location Marker
    problemLeafletMap.on("click", function (e) {
        setProblemLocation(e.latlng.lat, e.latlng.lng, true, "map_click");
        showToast("Location selected on map.");
    });

    // Backward-compatibility wrapper for any remaining problemLocationMap calls
    problemLocationMap = {
        setView: function (latLonArr, zoom) {
            if (problemLeafletMap && Array.isArray(latLonArr)) {
                problemLeafletMap.setView(latLonArr, zoom || 15);
            }
        },
        invalidateSize: function () {
            if (problemLeafletMap) {
                problemLeafletMap.invalidateSize();
            }
        }
    };

    updateGpsDiagnosticStatus("Ready (Click 'Use My Current Location')");

    // Re-render live user GPS marker if previously acquired
    if (window.userCurrentGps && typeof window.userCurrentGps.latitude === "number") {
        updateLiveGpsMarker(
            window.userCurrentGps.latitude,
            window.userCurrentGps.longitude,
            window.userCurrentGps.accuracy
        );
    }

    setTimeout(() => {
        if (problemLeafletMap) problemLeafletMap.invalidateSize();
    }, 150);
}

/**
 * Invalidate map size on page change or window resize
 */
function invalidateProblemMap() {
    const mapContainer = document.getElementById("problemLocationMap");
    if (!mapContainer || (mapContainer.offsetWidth === 0 && mapContainer.offsetHeight === 0)) return;

    if (problemLeafletMap) {
        problemLeafletMap.invalidateSize({ animate: false, pan: false });
        if (problemMarker && typeof problemMarker.getLatLng === "function") {
            const pos = problemMarker.getLatLng();
            if (pos) problemLeafletMap.panTo(pos);
        }
    } else {
        initProblemLocationMap();
    }
}

// Window resize listener with debounce
let mapWindowResizeTimer = null;
window.addEventListener("resize", function () {
    clearTimeout(mapWindowResizeTimer);
    mapWindowResizeTimer = setTimeout(() => {
        const submitPage = document.getElementById("submit");
        if (submitPage && submitPage.classList.contains("active-page")) {
            invalidateProblemMap();
        }
    }, 150);
});

/**
 * Update Location Accuracy Display Badge
 */
function updateAccuracyDisplay(accuracyMeters) {
    const badge = document.getElementById("gpsAccuracyBadge");
    const text = document.getElementById("accuracyValText");
    const confAcc = document.getElementById("confAccuracyText");

    if (!badge || !text) return;

    badge.style.display = "inline-flex";
    const acc = Math.round(accuracyMeters);

    if (confAcc) confAcc.textContent = `${acc} m`;

    if (acc <= 25) {
        badge.className = "gps-accuracy-badge high";
        text.textContent = `✓ GPS accuracy: ${acc} m`;
    } else if (acc <= 100) {
        badge.className = "gps-accuracy-badge moderate";
        text.textContent = `⚠ GPS accuracy: ${acc} m`;
    } else {
        badge.className = "gps-accuracy-badge low";
        text.textContent = `⚠ Location accuracy: ${acc} m.`;
    }
}

/**
 * Update Live GPS Location Marker & Accuracy Circle (Blue pin)
 * Moving GPS updates DO NOT automatically move the Problem Marker!
 */
function updateLiveGpsMarker(lat, lon, accuracy) {
    if (typeof lat !== "number" || typeof lon !== "number" || !problemLeafletMap) return;

    const pos = [lat, lon];
    const acc = accuracy || 10;

    // 1. Live location pulsing blue pin
    if (!liveLocationMarker) {
        const userIcon = L.divIcon({
            className: "leaflet-user-gps-pin",
            html: '<div style="width:16px;height:16px;background:#2563eb;border:2.5px solid #ffffff;border-radius:50%;box-shadow:0 0 12px rgba(37,99,235,0.85);animation:livePulsing 1.8s infinite;"></div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
        });
        liveLocationMarker = L.marker(pos, { icon: userIcon, zIndexOffset: 1000 }).addTo(problemLeafletMap);
        liveLocationMarker.bindPopup("<strong>🔵 Your Live Device Location</strong><br>Accuracy: ±" + Math.round(acc) + " m");
    } else {
        liveLocationMarker.setLatLng(pos);
        if (!problemLeafletMap.hasLayer(liveLocationMarker)) {
            liveLocationMarker.addTo(problemLeafletMap);
        }
    }

    // 2. Accuracy radius circle
    if (acc > 0) {
        if (!accuracyCircle) {
            accuracyCircle = L.circle(pos, {
                radius: acc,
                color: "#2563eb",
                fillColor: "#3b82f6",
                fillOpacity: 0.12,
                weight: 1.5
            }).addTo(problemLeafletMap);
        } else {
            accuracyCircle.setLatLng(pos);
            accuracyCircle.setRadius(acc);
            if (!problemLeafletMap.hasLayer(accuracyCircle)) {
                accuracyCircle.addTo(problemLeafletMap);
            }
        }
    }

    // Keep backward-compatible references
    leafletUserGpsMarker = liveLocationMarker;
    userCurrentLocationMarker = liveLocationMarker;
    leafletAccuracyCircle = accuracyCircle;
    userCurrentAccuracyCircle = accuracyCircle;
}

// Backward-compatible alias
function updateUserCurrentLocationMarker(lat, lon, accuracy) {
    updateLiveGpsMarker(lat, lon, accuracy);
}

/**
 * Set and apply the reported problem location
 * Updates form fields, Problem Marker, confirmation panel, and reverse geocoding
 */
function setProblemLocation(lat, lon, doReverseGeocode = true, source = "manual") {
    const latField = document.getElementById("latitude");
    const lonField = document.getElementById("longitude");
    const coordsText = document.getElementById("coordinatesText");
    const coordsPill = document.getElementById("coordinatesPill");
    const locSourceInput = document.getElementById("locSource");
    const locTimestampInput = document.getElementById("locTimestamp");

    if (latField) latField.value = lat.toFixed(6);
    if (lonField) lonField.value = lon.toFixed(6);
    if (locSourceInput) locSourceInput.value = source;
    if (locTimestampInput) locTimestampInput.value = new Date().toISOString();

    if (coordsText) {
        coordsText.textContent = `GPS: ${lat.toFixed(5)}° N, ${lon.toFixed(5)}° E`;
    }
    if (coordsPill) {
        coordsPill.classList.add("active");
    }

    // Move Problem Marker
    if (problemMarker && typeof problemMarker.setLatLng === "function") {
        problemMarker.setLatLng([lat, lon]);
    } else if (problemLeafletMap) {
        initProblemLocationMap();
        if (problemMarker) problemMarker.setLatLng([lat, lon]);
    }

    selectedLocationDetails.latitude = lat;
    selectedLocationDetails.longitude = lon;
    selectedLocationDetails.source = source;
    selectedLocationDetails.timestamp = new Date().toISOString();

    // Update Confirmation Panel Coordinates
    const confLat = document.getElementById("confLatText");
    const confLon = document.getElementById("confLonText");
    if (confLat) confLat.textContent = lat.toFixed(5);
    if (confLon) confLon.textContent = lon.toFixed(5);

    resetLocationConfirmationState();

    if (doReverseGeocode) {
        reverseGeocodeLocation(lat, lon);
    }

    // Check consistency vs live GPS location if available
    if (typeof verifyLocationConsistencyUI === "function") {
        verifyLocationConsistencyUI();
    }
    if (typeof triggerDuplicateDetectionDebounced === "function") {
        triggerDuplicateDetectionDebounced();
    }
}

// Backward-compatible alias
function applyLocationCoordinates(lat, lon, moveMarker = true, source = "manual") {
    setProblemLocation(lat, lon, true, source);
}

/**
 * Reset confirmation badge & button to pending
 */
function resetLocationConfirmationState() {
    isLocationConfirmed = false;
    const locConfirmedInput = document.getElementById("locConfirmed");
    if (locConfirmedInput) locConfirmedInput.value = "false";

    const badge = document.getElementById("confStatusBadge");
    if (badge) {
        badge.className = "conf-status-badge pending";
        badge.textContent = "Pending Confirmation";
    }

    const btn = document.getElementById("btnConfirmLocation");
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="ri-check-line"></i> Confirm This Location';
        btn.classList.remove("confirmed");
    }
}

/**
 * Handle successful GPS position update from watchPosition() / getCurrentPosition()
 */
function handleLocationSuccess(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const accuracy = position.coords.accuracy || 10;
    const timeStr = new Date().toLocaleTimeString();

    window.userCurrentGps = {
        latitude: lat,
        longitude: lon,
        accuracy: accuracy,
        timestamp: Date.now()
    };

    // Update Live GPS marker & accuracy circle (Blue pin)
    updateLiveGpsMarker(lat, lon, accuracy);
    updateAccuracyDisplay(accuracy);

    // Update Telemetry display
    const telemetryPill = document.getElementById("locTelemetryPill");
    const telemetryText = document.getElementById("locTelemetryText");
    if (telemetryPill && telemetryText) {
        telemetryPill.style.display = "inline-flex";
        telemetryText.textContent = `Source: Live GPS Tracking • Last Updated: ${timeStr}`;
    }

    // Show "Use Current Location as Problem Location" button
    const copyBtn = document.getElementById("btnCopyGpsToProblem");
    if (copyBtn) copyBtn.style.display = "inline-flex";

    updateGpsDiagnosticStatus("🟢 GPS Active");

    const status = document.getElementById("locationStatus");
    if (status) {
        status.className = "location-status-msg success";
        status.innerHTML = `🟢 Live Location Active &mdash; Lat: ${lat.toFixed(5)}°, Lon: ${lon.toFixed(5)}° (±${Math.round(accuracy)}m)`;
        status.style.display = "block";
    }

    // Verify distance between user GPS and Problem marker
    if (typeof verifyLocationConsistencyUI === "function") {
        verifyLocationConsistencyUI();
    }
}

/**
 * Handle GPS error from browser Geolocation API
 */
function handleLocationError(error) {
    const btnDetect = document.getElementById("btnDetectLocation");
    if (btnDetect) btnDetect.classList.remove("loading");

    let msg = "Location permission denied. Please allow location access in your browser.";
    let diag = "🔴 Permission Denied";

    if (error && error.code === 1) {
        msg = "Location permission denied. Please allow location access in your browser.";
        diag = "🔴 Permission Denied";
    } else if (error && error.code === 2) {
        msg = "Position unavailable. Could not detect GPS position.";
        diag = "🔴 Position Unavailable";
    } else if (error && error.code === 3) {
        msg = "Location request timed out. Please try again or select manually.";
        diag = "🔴 Request Timed Out";
    }

    updateGpsDiagnosticStatus(diag);

    const status = document.getElementById("locationStatus");
    if (status) {
        status.className = "location-status-msg error";
        status.textContent = msg;
        status.style.display = "block";
    }

    showToast(msg);
}

/**
 * Start Real-Time Live Location Tracking with watchPosition()
 */
function startLiveLocation() {
    if (!navigator.geolocation) {
        const msg = "Geolocation is not supported by this browser.";
        const status = document.getElementById("locationStatus");
        if (status) {
            status.className = "location-status-msg error";
            status.textContent = msg;
            status.style.display = "block";
        }
        updateGpsDiagnosticStatus("⚠️ Geolocation Not Supported");
        showToast(msg);
        return;
    }

    if (liveWatchId !== null) {
        navigator.geolocation.clearWatch(liveWatchId);
        liveWatchId = null;
    }

    const btn = document.getElementById("btnLiveLocation");
    const btnText = document.getElementById("btnLiveLocationText");
    const indicator = document.getElementById("mapLiveIndicator");
    const status = document.getElementById("locationStatus");

    if (btn) btn.classList.add("active");
    if (btnText) btnText.textContent = "Stop Tracking";
    if (indicator) indicator.style.display = "inline-flex";

    if (status) {
        status.className = "location-status-msg";
        status.textContent = "🟡 Requesting permission & locating...";
        status.style.display = "block";
    }

    updateGpsDiagnosticStatus("🟡 Requesting Permission");

    liveWatchId = navigator.geolocation.watchPosition(
        handleLocationSuccess,
        handleLocationError,
        {
            enableHighAccuracy: true,
            maximumAge: 5000,
            timeout: 15000
        }
    );

    window.gpsWatchId = liveWatchId;
    liveLocationWatchId = liveWatchId;
}

/**
 * Stop Live Location Tracking with clearWatch()
 * The last GPS location remains visible on the map
 */
function stopLiveLocation() {
    if (liveWatchId !== null) {
        navigator.geolocation.clearWatch(liveWatchId);
        liveWatchId = null;
        window.gpsWatchId = null;
        liveLocationWatchId = null;
    }

    const btn = document.getElementById("btnLiveLocation");
    const btnText = document.getElementById("btnLiveLocationText");
    const indicator = document.getElementById("mapLiveIndicator");
    const status = document.getElementById("locationStatus");

    if (btn) btn.classList.remove("active");
    if (btnText) btnText.textContent = "Start Live Location";
    if (indicator) indicator.style.display = "none";

    if (status) {
        status.textContent = "Live tracking stopped.";
        setTimeout(() => {
            if (status.textContent === "Live tracking stopped.") {
                status.style.display = "none";
            }
        }, 2500);
    }

    updateGpsDiagnosticStatus("Stopped");
    showToast("Live GPS tracking stopped.");
}

// Backward-compatible tracking functions
function startLiveLocationTracking() { startLiveLocation(); }
function stopLiveLocationTracking() { stopLiveLocation(); }
function toggleLiveLocation() {
    if (liveWatchId !== null) {
        stopLiveLocation();
    } else {
        startLiveLocation();
    }
}

/**
 * Primary "Use My Current Location" Action
 * Requests browser permission, fetches GPS coordinates, centers map,
 * initially places Problem Marker at current GPS position, and starts live tracking
 */
function useCurrentLocation() {
    const btn = document.getElementById("btnDetectLocation");
    const status = document.getElementById("locationStatus");

    if (!navigator.geolocation) {
        const msg = "Location permission was denied. You can manually select the problem location on the map.";
        if (status) {
            status.className = "location-status-msg error";
            status.textContent = msg;
            status.style.display = "block";
        }
        updateGpsDiagnosticStatus("⚠️ Geolocation Not Supported");
        showToast("Geolocation is not supported by your browser.");
        return;
    }

    if (btn) btn.classList.add("loading");
    if (status) {
        status.className = "location-status-msg";
        status.textContent = "Requesting live GPS coordinates from browser...";
        status.style.display = "block";
    }

    updateGpsDiagnosticStatus("🟡 Locating...");

    navigator.geolocation.getCurrentPosition(
        position => {
            if (btn) btn.classList.remove("loading");
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy || 10;

            // Handle location success
            handleLocationSuccess(position);

            // Initially move Problem Marker to current location
            setProblemLocation(lat, lon, true, "device_gps");

            // Center map on user location
            if (problemLeafletMap) {
                problemLeafletMap.setView([lat, lon], 15);
            }

            // Start continuous tracking
            startLiveLocation();

            showToast("Current location detected via device GPS.");
        },
        error => {
            if (btn) btn.classList.remove("loading");
            handleLocationError(error);
        },
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
    );
}

// Backward-compatible alias
function getLocation() {
    useCurrentLocation();
}

/**
 * Copy Current GPS Location explicitly to Problem Location
 */
function copyCurrentGpsToProblemLocation() {
    if (!window.userCurrentGps || typeof window.userCurrentGps.latitude !== "number") {
        showToast("Please detect your current location first.");
        return;
    }
    const { latitude, longitude } = window.userCurrentGps;
    setProblemLocation(latitude, longitude, true, "current_gps_copied");
    if (problemLeafletMap) {
        problemLeafletMap.setView([latitude, longitude], 15);
    }
    showToast("🎯 Problem location updated to current GPS position.");
}

/**
 * Reverse Geocode coordinates using OpenStreetMap Nominatim with local fallback
 * Updates State, District, and Formatted Address without erasing manual Village/Area input
 */
async function reverseGeocodeLocation(lat, lon) {
    const status = document.getElementById("locationStatus");
    const districtSelect = document.getElementById("district");
    const stateInput = document.getElementById("state");
    const areaInput = document.getElementById("area");
    const autoTag = document.getElementById("districtAutoTag");
    const confState = document.getElementById("confStateText");
    const confDistrict = document.getElementById("confDistrictText");
    const confArea = document.getElementById("confAreaText");
    const confAddress = document.getElementById("confAddressText");
    const locFormattedAddress = document.getElementById("locFormattedAddress");

    let detectedDistrict = null;
    let detectedState = null;
    let detectedArea = null;
    let formattedAddress = "";

    // 1. OpenStreetMap Nominatim Reverse Geocoding
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3500);
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&addressdetails=1`;
        const res = await fetch(url, { signal: controller.signal, headers: { "Accept-Language": "en" } });
        clearTimeout(timeoutId);

        if (res.ok) {
            const data = await res.json();
            if (data && data.address) {
                const addr = data.address;
                detectedState = addr.state || null;
                const rawDistrict = addr.state_district || addr.county || addr.district || addr.city || "";
                detectedDistrict = matchJharkhandDistrict(rawDistrict);

                detectedArea = addr.village || addr.suburb || addr.neighbourhood || addr.road || null;
                formattedAddress = data.display_name || "";
            }
        }
    } catch (e) {
        // Fallback to local district centroids
    }

    // 2. Geospatial Distance Fallback for 24 Jharkhand Districts
    if (!detectedDistrict) {
        const closest = findClosestJharkhandDistrict(lat, lon);
        if (closest && closest.distanceKm < 180) {
            detectedDistrict = closest.name;
            if (!detectedState) detectedState = "Jharkhand";
        }
    }

    // Update Form & Confirmation State
    if (stateInput && detectedState) {
        stateInput.value = detectedState;
    }
    if (confState) {
        confState.textContent = detectedState || "Jharkhand";
    }

    if (detectedDistrict && districtSelect) {
        districtSelect.value = detectedDistrict;
        if (autoTag) autoTag.style.display = "inline";
        if (confDistrict) confDistrict.textContent = detectedDistrict;

        if (status) {
            status.className = "location-status-msg success";
            status.innerHTML = `✓ Detected: <strong>${detectedDistrict}</strong>, ${detectedState || "Jharkhand"}`;
        }
    } else {
        if (autoTag) autoTag.style.display = "none";
        if (confDistrict) confDistrict.textContent = "Not detected (Manual select)";
    }

    // Preserve manually entered Village/Area/Street input: only fill if empty
    if (detectedArea && areaInput && !areaInput.value.trim()) {
        areaInput.value = detectedArea;
    }
    if (confArea) {
        confArea.textContent = (areaInput && areaInput.value.trim()) || detectedArea || "--";
    }

    if (formattedAddress) {
        if (confAddress) confAddress.textContent = formattedAddress;
        if (locFormattedAddress) locFormattedAddress.value = formattedAddress;
        selectedLocationDetails.formatted_address = formattedAddress;
    } else {
        const fallbackAddr = `${detectedArea ? detectedArea + ', ' : ''}${detectedDistrict || ''}, ${detectedState || 'Jharkhand'}`;
        if (confAddress) confAddress.textContent = fallbackAddr;
        if (locFormattedAddress) locFormattedAddress.value = fallbackAddr;
        selectedLocationDetails.formatted_address = fallbackAddr;
    }

    selectedLocationDetails.state = detectedState || "Jharkhand";
    selectedLocationDetails.district = detectedDistrict || "";
    selectedLocationDetails.locality = detectedArea || "";
}

// Backward-compatible alias
function reverseGeocodeLocationGoogle(lat, lon) {
    reverseGeocodeLocation(lat, lon);
}


function matchJharkhandDistrict(rawName) {
    if (!rawName) return null;
    const clean = rawName.toLowerCase().replace(/district|division/g, "").trim();
    for (const d of JHARKHAND_DISTRICTS) {
        if (clean.includes(d.name.toLowerCase()) || d.name.toLowerCase().includes(clean)) {
            return d.name;
        }
    }
    return null;
}

function findClosestJharkhandDistrict(lat, lon) {
    let closest = null;
    let minDistance = Infinity;

    for (const d of JHARKHAND_DISTRICTS) {
        // Fast flat-surface approximation (1 deg ~ 111 km)
        const dLat = (d.lat - lat) * 111;
        const dLon = (d.lon - lon) * 111 * Math.cos((lat * Math.PI) / 180);
        const distKm = Math.sqrt(dLat * dLat + dLon * dLon);

        if (distKm < minDistance) {
            minDistance = distKm;
            closest = { name: d.name, distanceKm: distKm };
        }
    }
    return closest;
}



/* =====================================
   AI PRIORITY
===================================== */

function calculatePriority(text) {

    text = text.toLowerCase();


    const highPriorityWords = [

        "emergency",
        "death",
        "danger",
        "shortage",
        "critical",
        "unsafe",
        "no water",
        "hospital",
        "flood"

    ];


    const mediumPriorityWords = [

        "problem",
        "lack",
        "shortage",
        "difficulty",
        "issue"

    ];


    for (const word of highPriorityWords) {

        if (text.includes(word)) {

            return "High";

        }

    }


    for (const word of mediumPriorityWords) {

        if (text.includes(word)) {

            return "Medium";

        }

    }


    return "Low";

}


/* =====================================
   PROBLEM SUBMISSION & AI MATCHING TRIGGER
===================================== */

const problemForm = document.getElementById("problemForm");

if (problemForm) {
    problemForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const title = document.getElementById("problemTitle")?.value.trim();
        const description = document.getElementById("description")?.value.trim();
        const selectedCategory = document.getElementById("category")?.value;
        const district = document.getElementById("district")?.value || "Ranchi";
        const state = document.getElementById("state")?.value.trim() || "Jharkhand";
        const area = document.getElementById("area")?.value.trim() || "";
        const latVal = parseFloat(document.getElementById("latitude")?.value) || null;
        const lonVal = parseFloat(document.getElementById("longitude")?.value) || null;

        if (!title || !description) {
            showToast("Please enter both Problem Title and Description.");
            return;
        }

        // 1. Run AI Problem Analyzer to extract metadata
        const analysis = analyzeProblem(title, description, selectedCategory, district, area);
        analysis.state = state;
        analysis.latitude = latVal;
        analysis.longitude = lonVal;

        // Attach Location Metadata (Feature 1 & Location Fraud-Risk Shield)
        const curGps = window.userCurrentGps || {};
        const locVerif = window.locationVerification || window.currentLocationVerification || {};
        const locCurrent = locVerif.currentGps || {};

        analysis.current_gps_latitude = locCurrent.latitude !== undefined ? locCurrent.latitude : (curGps.latitude || null);
        analysis.current_gps_longitude = locCurrent.longitude !== undefined ? locCurrent.longitude : (curGps.longitude || null);
        analysis.current_gps_accuracy = locCurrent.accuracy !== undefined ? locCurrent.accuracy : (curGps.accuracy || null);
        analysis.reported_latitude = latVal;
        analysis.reported_longitude = lonVal;
        analysis.distance_meters = locVerif.distanceMeters !== undefined ? locVerif.distanceMeters : null;
        analysis.distance_km = locVerif.distanceKm !== undefined ? locVerif.distanceKm : (locVerif.distance_km !== undefined ? locVerif.distance_km : null);
        analysis.location_risk_score = locVerif.locationRiskScore !== undefined ? locVerif.locationRiskScore : 0;
        analysis.suspicion_risk = locVerif.suspicionRisk !== undefined ? locVerif.suspicionRisk : (locVerif.suspicion_score || 0);
        analysis.location_status = locVerif.locationStatus || (curGps.latitude ? "🟢 Location Consistent" : "Current GPS not available");
        analysis.verification_status = locVerif.verificationStatus || "Automatically Verified";
        analysis.location_source = selectedLocationDetails.source || (curGps.latitude ? "browser_geolocation" : "manual");

        // Backward compatibility fields
        analysis.current_latitude = analysis.current_gps_latitude;
        analysis.current_longitude = analysis.current_gps_longitude;
        analysis.mismatch_distance_km = analysis.distance_km;
        analysis.suspicion_score = analysis.suspicion_risk;
        analysis.accuracy = selectedLocationDetails.accuracy || analysis.current_gps_accuracy;
        analysis.formatted_address = selectedLocationDetails.formatted_address;
        analysis.location_confirmed = isLocationConfirmed;
        analysis.location_timestamp = selectedLocationDetails.timestamp || new Date().toISOString();

        // Attach Duplicate Detection (Feature 2) Metadata
        const dupRes = window.currentDuplicateResult;
        if (dupRes && dupRes.duplicate_score >= 0.60) {
            analysis.is_duplicate = true;
            analysis.duplicate_score = dupRes.duplicate_score;
            analysis.duplicate_of_id = dupRes.id;
            analysis.duplicate_action = window.overrideDuplicateReport ? "Reported Anyway" : "Under Review";
        } else {
            analysis.is_duplicate = false;
            analysis.duplicate_score = 0;
            analysis.duplicate_of_id = null;
            analysis.duplicate_action = "None";
        }
        analysis.support_count = 1;

        // 2. Persist new problem in local storage
        const newProblem = saveSubmittedProblem(title, description, analysis);

        // 3. Asynchronously sync to live Python REST Backend if online
        if (MatchingAPI.isBackendLive) {
            fetch(`${MatchingAPI.backendBaseUrl}/api/problems`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: title,
                    description: description,
                    category: analysis.category,
                    district: district,
                    village: area,
                    state: state,
                    latitude: latVal,
                    longitude: lonVal,
                    accuracy: analysis.accuracy,
                    formatted_address: analysis.formatted_address,
                    location_source: analysis.location_source,
                    location_confirmed: analysis.location_confirmed,
                    location_timestamp: analysis.location_timestamp,
                    current_gps_latitude: analysis.current_gps_latitude,
                    current_gps_longitude: analysis.current_gps_longitude,
                    current_gps_accuracy: analysis.current_gps_accuracy,
                    reported_latitude: analysis.reported_latitude,
                    reported_longitude: analysis.reported_longitude,
                    distance_meters: analysis.distance_meters,
                    distance_km: analysis.distance_km,
                    location_risk_score: analysis.location_risk_score,
                    suspicion_risk: analysis.suspicion_risk,
                    location_status: analysis.location_status,
                    verification_status: analysis.verification_status,
                    current_latitude: analysis.current_latitude,
                    current_longitude: analysis.current_longitude,
                    mismatch_distance_km: analysis.mismatch_distance_km,
                    suspicion_score: analysis.suspicion_score,
                    is_duplicate: analysis.is_duplicate,
                    duplicate_score: analysis.duplicate_score,
                    duplicate_of_id: analysis.duplicate_of_id,
                    duplicate_action: analysis.duplicate_action
                })
            }).then(() => {
                if (typeof updateIntegrityDashboardStats === "function") {
                    updateIntegrityDashboardStats();
                }
            }).catch(e => console.warn("Backend problem sync notice:", e));
        }

        // 4. Trigger initial auto-matching and notifications
        runAutoMatchingForProblem(newProblem.id);

        let toastMsg = `Problem #${newProblem.id} submitted! AI Category: ${analysis.category} | District: ${district}.`;
        if (analysis.location_status === "Location Mismatch") {
            toastMsg += " ⚠ Location mismatch flagged for review.";
        } else if (analysis.is_duplicate) {
            toastMsg += ` ℹ Linked to #${analysis.duplicate_of_id} (Duplicate).`;
        }
        showToast(toastMsg);

        setTimeout(() => {
            problemForm.reset();
            const fl = document.getElementById("fileList");
            if (fl) fl.innerHTML = "";
            resetProblemMapAndAI();

            // Seamlessly open Smart Matching for the newly submitted problem
            openProblemMatches(newProblem.id);
        }, 1200);
    });
}


/* =====================================
   RESET FORM
===================================== */

function resetProblemMapAndAI() {
    userManuallySelectedCategory = false;
    window.overrideDuplicateReport = false;
    window.currentDuplicateResult = null;

    // Stop live location tracking if running
    if (typeof stopLiveLocationTracking === "function") {
        stopLiveLocationTracking();
    }

    const aiBox = document.getElementById("aiCategoryBox");
    if (aiBox) aiBox.style.display = "none";

    const overrideHint = document.getElementById("categoryOverrideHint");
    if (overrideHint) overrideHint.style.display = "none";

    const autoTag = document.getElementById("districtAutoTag");
    if (autoTag) autoTag.style.display = "none";

    const coordsText = document.getElementById("coordinatesText");
    if (coordsText) coordsText.textContent = 'GPS Coordinates: Not detected yet (Click "Use My Current Location" or click on map)';

    const coordsPill = document.getElementById("coordinatesPill");
    if (coordsPill) coordsPill.classList.remove("active");

    const status = document.getElementById("locationStatus");
    if (status) {
        status.textContent = "";
        status.style.display = "none";
    }

    const stateInput = document.getElementById("state");
    if (stateInput) stateInput.value = "Jharkhand";

    const latField = document.getElementById("latitude");
    const lonField = document.getElementById("longitude");
    if (latField) latField.value = "";
    if (lonField) lonField.value = "";

    const accBadge = document.getElementById("gpsAccuracyBadge");
    if (accBadge) accBadge.style.display = "none";

    // Reset confirmation state
    if (typeof resetLocationConfirmationState === "function") {
        resetLocationConfirmationState();
    }

    // Reset Location Verification & Duplicate Detection UI
    if (typeof resetLocationVerificationCardUI === "function") {
        resetLocationVerificationCardUI();
    }
    const dupCard = document.getElementById("aiDuplicateCard");
    if (dupCard) dupCard.style.display = "none";

    // Reset Leaflet markers & view
    const defaultCenter = [23.3441, 85.3096];
    if (problemLeafletMap) {
        problemLeafletMap.setView(defaultCenter, 12);
    }
    if (problemMarker) {
        problemMarker.setLatLng(defaultCenter);
    }
    if (liveLocationMarker && problemLeafletMap) {
        problemLeafletMap.removeLayer(liveLocationMarker);
        liveLocationMarker = null;
        leafletUserGpsMarker = null;
        userCurrentLocationMarker = null;
    }
    if (accuracyCircle && problemLeafletMap) {
        problemLeafletMap.removeLayer(accuracyCircle);
        accuracyCircle = null;
        leafletAccuracyCircle = null;
        userCurrentAccuracyCircle = null;
    }
}

function resetForm() {

    const form =
        document.getElementById("problemForm");

    if (form) {
        form.reset();
    }

    const fl = document.getElementById("fileList");
    if (fl) fl.innerHTML = "";

    resetProblemMapAndAI();

}


/* =====================================
   FILTER PROBLEMS
===================================== */

function filterProblems() {
    const search = (document.getElementById("problemSearch")?.value || "").toLowerCase().trim();
    const category = document.getElementById("problemCategory")?.value || "";
    const statusFilter = document.getElementById("problemStatus")?.value || "";

    const cards = document.querySelectorAll(".problem-card");

    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const cardCategory = card.dataset.category || "";
        const cardStatus = card.dataset.status || "";
        const cardLocStatus = card.dataset.locstatus || "";
        const cardIsDup = card.dataset.isdup === "true";

        const searchMatch = !search || text.includes(search);
        const categoryMatch = !category || cardCategory.toLowerCase() === category.toLowerCase();

        let statusMatch = true;
        if (statusFilter) {
            if (statusFilter === "Verified") {
                statusMatch = cardLocStatus === "Location Verified" || cardLocStatus === "Verified" || text.includes("verified");
            } else if (statusFilter === "Needs Verification") {
                statusMatch = cardLocStatus === "Needs Verification" || cardLocStatus === "Moderate Distance" || cardStatus === "Needs Verification" || text.includes("verification");
            } else if (statusFilter === "Location Mismatch") {
                statusMatch = cardLocStatus === "Location Mismatch" || text.includes("mismatch");
            } else if (statusFilter === "Possible Duplicate") {
                statusMatch = cardIsDup || text.includes("duplicate");
            } else {
                statusMatch = cardStatus.toLowerCase() === statusFilter.toLowerCase();
            }
        }

        if (searchMatch && categoryMatch && statusMatch) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

function filterProblemsByVerification(statusType) {
    if (typeof showPage === "function") {
        showPage("problems");
    }
    const statusSelect = document.getElementById("problemStatus");
    if (statusSelect) {
        statusSelect.value = statusType;
    }
    filterProblems();
}


/* =====================================
   GLOBAL SEARCH
===================================== */

function globalSearch() {

    const search =
        document.getElementById(
            "globalSearch"
        ).value.toLowerCase();


    if (!search) {

        return;

    }


    const problemCards =
        document.querySelectorAll(
            ".problem-card"
        );


    let found = false;


    problemCards.forEach(card => {

        if (
            card.textContent
                .toLowerCase()
                .includes(search)
        ) {

            found = true;

        }

    });


    if (found) {

        showPage("problems");

        document.getElementById(
            "problemSearch"
        ).value = search;

        filterProblems();

    }

}


/* =====================================
   VIEW PROBLEM & SMART MATCHING LINK
===================================== */

function viewProblem(id) {
    openProblemMatches(id);
}

function openProblemMatches(id) {
    if (typeof setActiveProblemAndMatch === "function") {
        setActiveProblemAndMatch(id);
    }
    showPage("matching");
    showToast(`Loaded AI recommendations for Problem #${id}`);
}


/* ==========================================================================
   JHARKHAND RESEARCH UNIVERSITIES - DATA STORE & MANAGEMENT
   ==========================================================================
   All universities are stored in this centralized data array.
   - Automatic alphabetical A–Z sorting is applied.
   - Instant search and highlighting works dynamically.
   - To add a new university, simply copy any object and add it to this array!
   ========================================================================== */

const universities = [
    {
        name: "All India Institute of Medical Sciences (AIIMS), Deoghar",
        location: "Deoghar, Jharkhand",
        researchStreams: ["Medical & Health Sciences", "Clinical Epidemiology", "Public Health", "Biotechnology", "Healthcare AI"],
        description: "Apex medical research institute serving eastern India, advancing clinical medicine, genomics, and regional community health systems.",
        emoji: "🏥",
        link: "aiims-deoghar"
    },
    {
        name: "Binod Bihari Mahto Koyalanchal University (BBMKU)",
        location: "Dhanbad, Jharkhand",
        researchStreams: ["Basic Sciences", "Environmental Science", "Energy & Mining Ecology", "Life Sciences", "Social Sciences"],
        description: "State university in the coal belt focused on mine-land ecological restoration, geo-environmental rehabilitation, and clean energy transitions.",
        emoji: "🎓",
        link: "bbmku"
    },
    {
        name: "Birla Institute of Technology (BIT), Mesra",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Engineering & Technology", "Computer Science / AI / Data Science", "Space Engineering & Rocketry", "Biotechnology", "Pharmaceutical Sciences"],
        description: "Premier deemed research university renowned for space engineering, satellite telemetry, autonomous robotics, and advanced drug delivery systems.",
        emoji: "🚀",
        link: "bit-mesra"
    },
    {
        name: "Birsa Agricultural University (BAU)",
        location: "Kanke, Ranchi, Jharkhand",
        researchStreams: ["Agriculture", "Veterinary Sciences", "Biotechnology", "Forestry & Agro-Ecology", "Soil Sciences"],
        description: "Pioneering agricultural institution developing drought-resilient plateau crops, sustainable agro-forestry, and indigenous livestock genetics.",
        emoji: "🌾",
        link: "bau"
    },
    {
        name: "Central University of Jharkhand (CUJ)",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Environmental Science", "Energy Engineering", "Nanotechnology", "Basic Sciences", "Humanities & Tribal Studies"],
        description: "Central university established by Parliament, leading frontier research in green hydrogen, water remediation, nanomaterials, and tribal linguistics.",
        emoji: "🏛️",
        link: "cuj"
    },
    {
        name: "Dr. Shyama Prasad Mukherjee University (DSPMU)",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Basic Sciences", "Computer Science", "Environmental Studies", "Humanities", "Social Sciences"],
        description: "Historic multidisciplinary university fostering academic research in computational sciences, plant biodiversity, and regional tribal languages.",
        emoji: "📚",
        link: "dspmu"
    },
    {
        name: "IIT (Indian School of Mines), Dhanbad",
        location: "Dhanbad, Jharkhand",
        researchStreams: ["Mining & Mineral Engineering", "Computer Science / AI / Data Science", "Earth Sciences", "Petroleum Engineering", "Environmental Science"],
        description: "Institute of National Importance established in 1926; international authority in mining technology, earth sciences, seismic monitoring, and energy engineering.",
        emoji: "⛏️",
        link: "iit-ism"
    },
    {
        name: "Indian Institute of Information Technology (IIIT), Ranchi",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Computer Science / AI / Data Science", "Electronics & Communication", "Data Analytics", "Cyber-Physical Systems", "Cybersecurity"],
        description: "Institute of National Importance specializing in deep learning architectures, embedded IoT devices, computer vision, and autonomous systems.",
        emoji: "💻",
        link: "iiit-ranchi"
    },
    {
        name: "Indian Institute of Management (IIM), Ranchi",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Management", "Public Policy & Governance", "Data Analytics", "Innovation & Entrepreneurship", "Social Sciences"],
        description: "Premier national management institute producing high-impact research in public administration, digital economies, and sustainable livelihoods.",
        emoji: "📊",
        link: "iim-ranchi"
    },
    {
        name: "Jharkhand Innovation Institute",
        location: "Jamshedpur, Jharkhand",
        researchStreams: ["Innovation & Entrepreneurship", "Startups", "Computer Science / AI", "Healthcare", "Design Thinking"],
        description: "Dynamic state innovation catalyst incubating student deep-tech startups, affordable healthcare diagnosis devices, and social innovation enterprises.",
        emoji: "💡",
        link: "card-uni-jii"
    },
    {
        name: "Jharkhand Rai University",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Engineering & Technology", "Computer Science / AI", "Agriculture", "Pharmaceutical Sciences", "Management"],
        description: "Industry-aligned university with active research labs in agricultural biotechnology, pharmaceutical formulations, and applied machine learning.",
        emoji: "🌱",
        link: "jru"
    },
    {
        name: "Kolhan University",
        location: "Chaibasa, West Singhbhum, Jharkhand",
        researchStreams: ["Basic Sciences", "Humanities", "Social Sciences", "Tribal Studies", "Mineral Resources"],
        description: "State university in the mineral-rich Kolhan belt, conducting extensive research in tribal ethnography, regional ecosystems, and mineral economics.",
        emoji: "🌳",
        link: "kolhan-uni"
    },
    {
        name: "National Institute of Advanced Manufacturing Technology (NIAMT)",
        location: "Hatia, Ranchi, Jharkhand",
        researchStreams: ["Engineering & Technology", "Advanced Manufacturing", "Materials Science", "Metallurgy", "Foundry & Forge Technology"],
        description: "Apex specialized national institute leading research in precision casting, metal additive manufacturing, composite alloys, and industrial automation.",
        emoji: "⚙️",
        link: "niamt"
    },
    {
        name: "National Institute of Technology (NIT), Jamshedpur",
        location: "Jamshedpur, Jharkhand",
        researchStreams: ["Engineering & Technology", "Metallurgy & Materials Science", "Robotics & Automation", "Clean Energy", "Computer Science"],
        description: "Institute of National Importance in the industrial hub of Jamshedpur, spearheading research in smart grid systems, automotive metallurgy, and robotics.",
        emoji: "⚡",
        link: "nit-jsr"
    },
    {
        name: "National University of Study and Research in Law (NUSRL)",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Law & Public Policy", "Intellectual Property Rights", "Environmental Jurisprudence", "Tribal Rights", "Cyber Law"],
        description: "Leading national law university engaged in judicial governance research, intellectual property commercialization, and environmental legal advocacy.",
        emoji: "⚖️",
        link: "nusrl"
    },
    {
        name: "Nilamber-Pitamber University (NPU)",
        location: "Medininagar, Palamu, Jharkhand",
        researchStreams: ["Basic Sciences", "Humanities", "Agro-Economics", "Water Resource Management", "Social Sciences"],
        description: "Regional university in western Jharkhand focusing on drought mitigation strategies, soil revitalization, and tribal socioeconomic empowerment.",
        emoji: "💧",
        link: "npu"
    },
    {
        name: "Ranchi Technical University",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Engineering & Technology", "IoT & Smart City", "Renewable Energy", "Smart Grid Systems", "Automation"],
        description: "Premier technical university advancing smart grid technologies, solar-wind microgrids, and IoT sensor networks for urban infrastructure.",
        emoji: "🔋",
        link: "card-uni-rtu"
    },
    {
        name: "Ranchi University",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Basic Sciences", "Biotechnology", "Social Sciences", "Humanities", "Tribal & Regional Languages"],
        description: "Historic university established in 1960, renowned for pioneering work in tribal folklore conservation, botanical pharmacology, and chemical analysis.",
        emoji: "📖",
        link: "ranchi-uni"
    },
    {
        name: "Sarala Birla University",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Computer Science / AI / Data Science", "Engineering & Technology", "Applied Sciences", "Management", "Humanities"],
        description: "Modern university providing research platforms in cloud data engineering, smart automation, applied physical sciences, and corporate strategy.",
        emoji: "🌐",
        link: "sbu"
    },
    {
        name: "Sido Kanhu Murmu University (SKMU)",
        location: "Dumka, Jharkhand",
        researchStreams: ["Humanities", "Social Sciences", "Tribal Culture & Languages", "Environmental Studies", "Rural Economics"],
        description: "Premier university in Santhal Pargana dedicated to tribal rights documentation, Santhali literature preservation, and rural livelihood research.",
        emoji: "🏹",
        link: "skmu"
    },
    {
        name: "University of Jharkhand",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Research & Innovation", "Computer Science / AI / Data Science", "Water Resource Management", "Agriculture", "Environmental Science"],
        description: "State apex research center coordinating multidisciplinary teams to tackle real-world community challenges and societal innovation programs.",
        emoji: "🎓",
        link: "card-uni-jharkhand"
    },
    {
        name: "Vinoba Bhave University (VBU)",
        location: "Hazaribagh, Jharkhand",
        researchStreams: ["Basic Sciences", "Biotechnology", "Computer Science", "Environmental Biology", "Social Sciences"],
        description: "Leading state university in North Chotanagpur, conducting vital research in biodiversity conservation, medicinal flora, and microbiology.",
        emoji: "🔬",
        link: "vbu"
    },
    {
        name: "Xavier Institute of Social Service (XISS)",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Social Sciences", "Rural Development", "Sustainable Livelihoods", "Management", "Public Health Policy"],
        description: "Celebrated autonomous research institute pioneering grassroots social work, community development models, and CSR impact assessments.",
        emoji: "🤝",
        link: "xiss"
    },
    {
        name: "YBN University",
        location: "Ranchi, Jharkhand",
        researchStreams: ["Medical & Health Sciences", "Pharmacy & Clinical Care", "Agriculture", "Basic Sciences", "Engineering"],
        description: "Comprehensive multidisciplinary university operating dedicated research centers in allied healthcare diagnostics and agro-climatic farming.",
        emoji: "🩺",
        link: "ybn-uni"
    }
];

// Backward-compatibility alias
const universitiesData = universities;

let currentProfileUniversity = null;

/* Helper: Get alphabetically sorted universities */
function getSortedUniversities() {

    return [...universities].sort((a, b) =>
        a.name.localeCompare(b.name, undefined, { sensitivity: "base" })
    );

}

/* Helper: Highlight matching search terms inside text */
function highlightMatch(text, query) {

    if (!query || !text) return escapeHtml(text);

    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(${escapedQuery})`, "gi");

    // Split text to escape HTML while preserving match
    const parts = text.split(regex);
    return parts.map(part => {
        if (part.toLowerCase() === query.toLowerCase()) {
            return `<mark class="search-highlight">${escapeHtml(part)}</mark>`;
        }
        return escapeHtml(part);
    }).join("");

}

/* Render the Scrollable More Universities Grid */
function renderMoreUniversities(filterQuery = "") {

    const grid = document.getElementById("moreUniversitiesGrid");
    const noFound = document.getElementById("noUniversitiesFound");
    const noFoundText = document.getElementById("noFoundText");
    const statsElem = document.getElementById("searchResultStats");
    const totalCountElem = document.getElementById("totalUniversitiesCount");
    const countBadge = document.getElementById("uniCountBadge");

    // Update global counters
    if (totalCountElem) {
        totalCountElem.textContent = `${universities.length} Universities Available`;
    }
    if (countBadge) {
        countBadge.textContent = universities.length;
    }

    if (!grid) return;

    const query = filterQuery.trim().toLowerCase();
    const sortedList = getSortedUniversities();

    // Filter by name or location
    const matched = sortedList.filter(uni => {
        if (!query) return true;
        const nameMatch = uni.name.toLowerCase().includes(query);
        const locMatch = uni.location && uni.location.toLowerCase().includes(query);
        const streamMatch = uni.researchStreams && uni.researchStreams.some(s => s.toLowerCase().includes(query));
        return nameMatch || locMatch || streamMatch;
    });

    // Update statistics message
    if (statsElem) {
        if (!query) {
            statsElem.textContent = `Showing all ${sortedList.length} universities (arranged alphabetically A–Z)`;
        } else {
            statsElem.innerHTML = `Found <strong>${matched.length}</strong> matching ${matched.length === 1 ? 'university' : 'universities'} for "<em>${escapeHtml(filterQuery)}</em>"`;
        }
    }

    // Handle empty state
    if (matched.length === 0) {
        grid.innerHTML = "";
        if (noFound) {
            noFound.style.display = "block";
            if (noFoundText) {
                noFoundText.textContent = `No universities found matching "${escapeHtml(filterQuery)}". Try searching by another district or stream.`;
            }
        }
        return;
    }

    if (noFound) {
        noFound.style.display = "none";
    }

    // Render cards
    grid.innerHTML = matched.map(uni => {
        const isSearchActive = query.length > 0;
        const cardClass = isSearchActive ? "more-uni-card matching-highlight" : "more-uni-card";

        const highlightedName = isSearchActive ? highlightMatch(uni.name, query) : escapeHtml(uni.name);
        const highlightedLoc = isSearchActive ? highlightMatch(uni.location, query) : escapeHtml(uni.location);

        const streamsHtml = (uni.researchStreams || ["Research", "Higher Education"]).map(stream => {
            return `<span class="stream-tag">${escapeHtml(stream)}</span>`;
        }).join("");

        return `
            <div class="${cardClass}" id="more-card-${escapeQuotes(uni.link || uni.name.replace(/\s+/g, '-').toLowerCase())}">
                <div class="more-uni-top">
                    <div class="more-uni-logo">
                        ${uni.emoji || '🎓'}
                    </div>
                    <span class="more-uni-location">
                        <i class="ri-map-pin-line"></i> ${highlightedLoc}
                    </span>
                </div>

                <h3>${highlightedName}</h3>

                <p class="more-uni-desc">${escapeHtml(uni.description)}</p>

                <div class="more-uni-streams-title">Relevant Research Streams</div>
                <div class="research-streams">
                    ${streamsHtml}
                </div>

                <button
                    class="outline-btn"
                    onclick="openUniversityProfile('${escapeQuotes(uni.name)}')"
                    title="Explore ${escapeHtml(uni.name)} academic profile"
                >
                    <i class="ri-eye-line"></i> View Profile
                </button>
            </div>
        `;
    }).join("");

}

/* Search input handler */
function handleUniversitySearch(query) {

    const clearBtn = document.getElementById("searchClearBtn");
    if (clearBtn) {
        clearBtn.style.display = query.trim().length > 0 ? "flex" : "none";
    }

    renderMoreUniversities(query);

}

/* Clear search input */
function clearUniversitySearch() {

    const input = document.getElementById("searchUniversitiesInput");
    const clearBtn = document.getElementById("searchClearBtn");

    if (input) {
        input.value = "";
        input.focus();
    }
    if (clearBtn) {
        clearBtn.style.display = "none";
    }

    renderMoreUniversities("");

}

/* Toggle More Universities Section Smoothly */
function toggleMoreUniversitiesSection() {

    const section = document.getElementById("moreUniversitiesSection");
    const btn = document.getElementById("moreUniversitiesBtn");
    const input = document.getElementById("searchUniversitiesInput");

    if (!section) return;

    // Smooth scroll down to the More Universities section
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    // Focus search input
    setTimeout(() => {
        if (input) {
            input.focus();
        }
    }, 400);

    // Apply flash highlight to the section
    section.classList.remove("card-highlight-flash");
    void section.offsetWidth;
    section.classList.add("card-highlight-flash");

    if (btn) {
        btn.classList.add("active");
        setTimeout(() => btn.classList.remove("active"), 1200);
    }

}

/* Open University Profile Modal and display toast */
function openUniversityProfile(nameOrLink) {

    // Find the university data
    const query = String(nameOrLink).trim().toLowerCase();
    const uni = universities.find(u =>
        u.name.toLowerCase() === query ||
        (u.link && u.link.toLowerCase() === query)
    ) || {
        name: nameOrLink,
        location: "Jharkhand, India",
        researchStreams: ["Higher Education", "Innovation", "Research"],
        description: "Active higher education & research institution in Jharkhand participating in societal innovation.",
        emoji: "🎓"
    };

    currentProfileUniversity = uni;

    // Toast notification (consistent with existing portal behavior)
    showToast(`Viewing academic profile: ${uni.name}`);

    // Populate modal
    const modalLogo = document.getElementById("modalUniLogo");
    const modalName = document.getElementById("modalUniName");
    const modalDept = document.getElementById("modalUniDept");
    const modalLoc = document.getElementById("modalUniLocation");
    const modalTags = document.getElementById("modalUniTags");
    const modalDesc = document.getElementById("modalUniDesc");

    if (modalLogo) {
        modalLogo.textContent = uni.emoji || "🎓";
    }
    if (modalName) modalName.textContent = uni.name;
    if (modalDept) {
        const topStream = uni.researchStreams && uni.researchStreams.length > 0 ? uni.researchStreams[0] : "Academic Partner";
        modalDept.textContent = `${topStream} & Multidisciplinary Research`;
    }
    if (modalLoc) modalLoc.textContent = uni.location || "Jharkhand, India";
    if (modalDesc) modalDesc.textContent = uni.description || "Societal innovation network partner.";

    if (modalTags && uni.researchStreams) {
        modalTags.innerHTML = uni.researchStreams.map(tag => `<span>${escapeHtml(tag)}</span>`).join("\n");
    }

    // Open modal
    const modal = document.getElementById("universityProfileModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }

}

/* Close University Profile Modal */
function closeUniversityProfileModal() {

    const modal = document.getElementById("universityProfileModal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }

}

/* Handle click outside modal card */
function handleUniModalOverlayClick(event) {

    if (event.target && event.target.id === "universityProfileModal") {
        closeUniversityProfileModal();
    }

}

/* Collaborate action */
function initiateCollaboration() {

    const uniName = currentProfileUniversity ? currentProfileUniversity.name : "University";
    closeUniversityProfileModal();
    showToast(`Collaboration invitation sent to ${uniName}!`);

}

/* Compatibility helper for profile button in existing cards */
function viewUniversityProfile(name) {

    openUniversityProfile(name);

}

/* Helper escape functions */
function escapeHtml(str) {

    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}

function escapeQuotes(str) {

    if (!str) return "";
    return String(str).replace(/'/g, "\\'");

}


/* ==========================================================================
   CENTRALIZED DATA-DRIVEN JHARKHAND INDUSTRIES SYSTEM
   ==========================================================================
   To add another industry in the future, simply add ONE new object to this array.
   The system will automatically:
   1. Place it into the correct A–Z alphabetical position.
   2. Make it searchable and filterable in the Search Industries input.
   3. Highlight matching query text automatically.
   4. Update the industry count badge and header stats.
   5. Apply the standard card design and open the interactive profile modal.
   ========================================================================== */

const industries = [
    {
        name: "Agriculture & AgriTech",
        sector: "Agri-Business & Technology",
        icon: "🌾",
        description: "Advanced agricultural machinery, precision drip irrigation, plateau crop processing, and cold storage logistics.",
        buttonText: "Partner With Us",
        link: "agritech",
        focusAreas: ["Precision Farming", "Cold Chain", "Soil Health", "Drip Irrigation"]
    },
    {
        name: "Automobile & Auto Components",
        sector: "Heavy Engineering & Mobility",
        icon: "🚗",
        description: "Auto ancillary manufacturing, commercial vehicles, EV drivetrains, and precision casting in Adityapur industrial belt.",
        buttonText: "Explore Partnerships",
        link: "automobile",
        focusAreas: ["EV Systems", "Auto Ancillaries", "Precision Forging", "Fleet Mobility"]
    },
    {
        name: "Banking & Financial Services",
        sector: "BFSI & Microfinance",
        icon: "🏦",
        description: "Rural micro-credit, priority sector lending, digital financial inclusion, and venture debt for regional enterprises.",
        buttonText: "View Opportunities",
        link: "banking-finance",
        focusAreas: ["Microfinance", "Priority Lending", "Rural FinTech", "Enterprise Credit"]
    },
    {
        name: "Biotechnology",
        sector: "Bio-Sciences & Agriculture",
        icon: "🧬",
        description: "Bio-fertilizers, medicinal plant genomics, tissue culture labs, and indigenous bio-resource commercialization.",
        buttonText: "Collaborate",
        link: "biotechnology",
        focusAreas: ["Bio-fertilizers", "Plant Genetics", "Bio-pharma", "Herbal Extracts"]
    },
    {
        name: "Construction & Infrastructure",
        sector: "Civil & Urban Development",
        icon: "🏗️",
        description: "Sustainable civil infrastructure, smart highway materials, green building technologies, and urban civil engineering.",
        buttonText: "Partner With Us",
        link: "construction",
        focusAreas: ["Eco-Concrete", "Highway Engineering", "Prefab Tech", "Smart Infrastructure"]
    },
    {
        name: "CSR Organizations",
        sector: "Social Responsibility & Grants",
        icon: "💰",
        description: "Support projects through CSR funding, community development grants, and grassroots impact initiatives across districts.",
        buttonText: "View Opportunities",
        link: "csr-organizations",
        focusAreas: ["CSR Funding", "Community Development", "Rural Welfare", "Social Grants"]
    },
    {
        name: "Education & EdTech",
        sector: "Higher Education & Skills",
        icon: "📚",
        description: "Vernacular digital learning tools, polytechnic skills incubators, STEM labs, and industrial apprentice programs.",
        buttonText: "Explore Programs",
        link: "edtech",
        focusAreas: ["Digital Classrooms", "Vocational Skills", "STEM Labs", "Vernacular Content"]
    },
    {
        name: "Electronics & Hardware Design",
        sector: "Semiconductor & IoT",
        icon: "⚡",
        description: "Industrial IoT sensors, power electronics, embedded controllers, and rural solar microgrid telemetry systems.",
        buttonText: "Collaborate",
        link: "electronics",
        focusAreas: ["IoT Sensors", "Power Electronics", "PCB Fabrication", "Solar Inverters"]
    },
    {
        name: "Energy & Renewable Energy",
        sector: "Clean Tech & Solar",
        icon: "☀️",
        description: "Large-scale solar farms, pumped hydro storage, floating solar arrays on reservoirs, and green hydrogen pilots.",
        buttonText: "Explore Projects",
        link: "renewable-energy",
        focusAreas: ["Solar PV", "Pumped Hydro", "Floating Solar", "Green Hydrogen"]
    },
    {
        name: "Environmental & Waste Management",
        sector: "Circular Economy & Ecology",
        icon: "♻️",
        description: "Industrial slag recycling, municipal solid waste valorization, mine tailings stabilization, and plastic upcycling.",
        buttonText: "View Opportunities",
        link: "waste-management",
        focusAreas: ["Slag Utilization", "Mine Reclamation", "Plastic Recycling", "E-Waste"]
    },
    {
        name: "Food Processing",
        sector: "Value-Add Agriculture",
        icon: "🍲",
        description: "Agro-processing cluster units, lac and honey packaging, regional horticulture drying, and certified export packaging.",
        buttonText: "Partner With Us",
        link: "food-processing",
        focusAreas: ["Agro-clusters", "Lac Processing", "Organic Packaging", "Horticulture"]
    },
    {
        name: "Healthcare & Pharmaceuticals",
        sector: "Medicine & Public Health",
        icon: "🩺",
        description: "Essential formulation pharma units, telemedicine diagnostics, primary health center supplies, and affordable devices.",
        buttonText: "Collaborate",
        link: "healthcare-pharma",
        focusAreas: ["Tele-health", "Generic Drugs", "Rural Diagnostics", "Medical Supplies"]
    },
    {
        name: "Information Technology & Software",
        sector: "Enterprise Tech & Cloud",
        icon: "💻",
        description: "Enterprise cloud systems, state digital governance platforms, AI workflow automation, and custom open-source tools.",
        buttonText: "Explore Projects",
        link: "it-software",
        focusAreas: ["Cloud Infrastructure", "AI & ML", "Citizen Portals", "Cybersecurity"]
    },
    {
        name: "IT/ITES & BPO",
        sector: "Technology Services",
        icon: "🎧",
        description: "Regional BPO hubs, digital data annotation, geographic information systems (GIS), and e-governance back-office support.",
        buttonText: "Explore Opportunities",
        link: "it-ites",
        focusAreas: ["GIS Mapping", "Data Annotation", "E-Gov Services", "Customer Support"]
    },
    {
        name: "Logistics & Transportation",
        sector: "Supply Chain & Freight",
        icon: "🚚",
        description: "Multimodal rail-road freight corridors, inland container depots, mining dispatch logistics, and warehousing automation.",
        buttonText: "Partner With Us",
        link: "logistics",
        focusAreas: ["Multimodal Freight", "Fleet Telematics", "Cold Storage", "Warehousing"]
    },
    {
        name: "Manufacturing & Heavy Engineering",
        sector: "Industrial Equipment",
        icon: "⚙️",
        description: "Heavy industrial machinery, mining equipment assembly, foundry products, and precision fabrication workshops in Ranchi.",
        buttonText: "Explore Projects",
        link: "manufacturing",
        focusAreas: ["Heavy Machinery", "Foundry Castings", "Industrial Automation", "Tooling"]
    },
    {
        name: "Mining & Minerals",
        sector: "Core Extraction & Processing",
        icon: "⛏️",
        description: "Coal, iron ore, copper, bauxite, and mica extraction with eco-friendly smart mining, drone surveying, and worker safety tech.",
        buttonText: "Collaborate",
        link: "mining-minerals",
        focusAreas: ["Smart Mining", "Drone Surveys", "Mineral Beneficiation", "Safety Sensors"]
    },
    {
        name: "Power & Utilities",
        sector: "Energy Infrastructure",
        icon: "🔌",
        description: "Thermal and clean transmission lines, smart grid distribution, substation SCADA telemetry, and 24/7 rural feeder monitoring.",
        buttonText: "View Opportunities",
        link: "power-utilities",
        focusAreas: ["Grid Automation", "SCADA Systems", "Rural Feeders", "Substation Tech"]
    },
    {
        name: "Startups & MSMEs",
        sector: "Innovation & Rapid Deployment",
        icon: "🚀",
        description: "Help develop and deploy innovative solutions, commercialize local patents, and create technology jobs across Jharkhand.",
        buttonText: "Partner With Us",
        link: "startups-msmes",
        focusAreas: ["Incubators", "Commercialization", "Local Enterprise", "Seed Capital"]
    },
    {
        name: "Steel & Metal",
        sector: "Metallurgical Industries",
        icon: "🏭",
        description: "Primary steel making, specialized alloy steels, rolling mills, and sponge iron manufacturing in Jamshedpur and Bokaro.",
        buttonText: "Explore Projects",
        link: "steel-metal",
        focusAreas: ["Green Steelmaking", "Specialty Alloys", "Blast Furnace Tech", "Rolling Mills"]
    },
    {
        name: "Technology Partners",
        sector: "Digital Innovation & Mentorship",
        icon: "🏢",
        description: "Provide technology and technical mentorship, cloud hosting architecture, cybersecurity reviews, and engineering workshops.",
        buttonText: "Explore Projects",
        link: "technology-partners",
        focusAreas: ["Architecture Design", "Cloud Hosting", "Developer Labs", "Code Reviews"]
    },
    {
        name: "Telecommunications",
        sector: "Network & Connectivity",
        icon: "📡",
        description: "Optical fiber last-mile rollout in tribal areas, 5G enterprise networks, cellular towers, and satellite broadband terminals.",
        buttonText: "Partner With Us",
        link: "telecom",
        focusAreas: ["BharatNet Rollout", "5G Private Networks", "Fiber Infrastructure", "Tower Ops"]
    },
    {
        name: "Textile & Handicrafts",
        sector: "Indigenous Artisan Crafts",
        icon: "🧵",
        description: "Tussar silk weaving, handloom cooperatives, Sohrai tribal art commercialization, and digital artisan marketplaces.",
        buttonText: "View Opportunities",
        link: "textile-handicrafts",
        focusAreas: ["Tussar Silk", "Artisan Direct", "Sohrai Tribal Art", "Handlooms"]
    },
    {
        name: "Tourism & Hospitality",
        sector: "Eco-Tourism & Heritage",
        icon: "🏕️",
        description: "Eco-tourism homestays around Betla and Netarhat, digital tourism booking engines, and heritage conservation circuits.",
        buttonText: "Explore Opportunities",
        link: "tourism-hospitality",
        focusAreas: ["Eco-Tourism", "Homestay Tech", "Cultural Circuits", "Waterfall Trails"]
    },
    {
        name: "Water Management & Sanitation",
        sector: "Environmental Utilities",
        icon: "💧",
        description: "Smart rural piped water networks, check-dam telemetry, mine-water purification plants, and urban wastewater treatment.",
        buttonText: "Collaborate",
        link: "water-management",
        focusAreas: ["Jal Jeevan Telemetry", "Mine Water RO", "Check Dams", "Wastewater Reuse"]
    }
];

// Backward-compatibility alias
const industriesData = industries;

let currentProfileIndustry = null;

/* Helper: Get alphabetically sorted industries (A–Z) */
function getSortedIndustries() {

    return [...industries].sort((a, b) =>
        a.name.localeCompare(b.name, undefined, { sensitivity: "base" })
    );

}

/* Render the Scrollable More Industries Grid */
function renderMoreIndustries(filterQuery = "") {

    const grid = document.getElementById("moreIndustriesGrid");
    const noFound = document.getElementById("noIndustriesFound");
    const noFoundText = document.getElementById("noIndustryFoundText");
    const statsElem = document.getElementById("searchIndustryResultStats");
    const totalCountElem = document.getElementById("totalIndustriesCount");
    const countBadge = document.getElementById("industryCountBadge");

    // Update global counters
    if (totalCountElem) {
        totalCountElem.textContent = `${industries.length} Industries Available`;
    }
    if (countBadge) {
        countBadge.textContent = industries.length;
    }

    if (!grid) return;

    const query = filterQuery.trim().toLowerCase();
    const sortedList = getSortedIndustries();

    // Filter by name, sector, description, or focusAreas
    const matched = sortedList.filter(ind => {
        if (!query) return true;
        const nameMatch = ind.name && ind.name.toLowerCase().includes(query);
        const sectorMatch = ind.sector && ind.sector.toLowerCase().includes(query);
        const descMatch = ind.description && ind.description.toLowerCase().includes(query);
        const focusMatch = ind.focusAreas && ind.focusAreas.some(f => f.toLowerCase().includes(query));
        return nameMatch || sectorMatch || descMatch || focusMatch;
    });

    // Update statistics message
    if (statsElem) {
        if (!query) {
            statsElem.textContent = `Showing all ${sortedList.length} industries (arranged alphabetically A–Z)`;
        } else {
            statsElem.innerHTML = `Found <strong>${matched.length}</strong> matching ${matched.length === 1 ? 'industry' : 'industries'} for "<em>${escapeHtml(filterQuery)}</em>"`;
        }
    }

    // Handle empty state
    if (matched.length === 0) {
        grid.innerHTML = "";
        if (noFound) {
            noFound.style.display = "block";
            if (noFoundText) {
                noFoundText.textContent = `No industries found matching "${escapeHtml(filterQuery)}". Try searching by another sector or keyword.`;
            }
        }
        return;
    }

    if (noFound) {
        noFound.style.display = "none";
    }

    // Render cards
    grid.innerHTML = matched.map(ind => {
        const isSearchActive = query.length > 0;
        const cardClass = isSearchActive ? "more-industry-card matching-highlight" : "more-industry-card";

        const highlightedName = isSearchActive ? highlightMatch(ind.name, query) : escapeHtml(ind.name);
        const highlightedSector = isSearchActive ? highlightMatch(ind.sector || "Industry Partner", query) : escapeHtml(ind.sector || "Industry Partner");

        const tagsHtml = (ind.focusAreas || ["Partnership", "Innovation"]).map(tag => {
            const highlightedTag = isSearchActive ? highlightMatch(tag, query) : escapeHtml(tag);
            return `<span class="industry-tag">${highlightedTag}</span>`;
        }).join("");

        const buttonLabel = ind.buttonText || "Partner With Us";
        const iconSymbol = ind.icon || ind.emoji || "🏢";

        return `
            <div class="${cardClass}" id="more-ind-${escapeQuotes(ind.link || ind.name.replace(/\\s+/g, '-').toLowerCase())}">
                <div class="more-industry-top">
                    <div class="more-industry-logo">
                        ${iconSymbol}
                    </div>
                    <span class="more-industry-sector">
                        <i class="ri-briefcase-line"></i> ${highlightedSector}
                    </span>
                </div>

                <h3>${highlightedName}</h3>

                <p class="more-industry-desc">${escapeHtml(ind.description || "")}</p>

                <div class="more-industry-focus-title">Focus & Capabilities</div>
                <div class="industry-focus-tags">
                    ${tagsHtml}
                </div>

                <button
                    class="primary-btn"
                    onclick="openIndustryProfile('${escapeQuotes(ind.name)}')"
                    title="Explore ${escapeHtml(ind.name)} partnership scope"
                >
                    <i class="ri-external-link-line"></i> ${escapeHtml(buttonLabel)}
                </button>
            </div>
        `;
    }).join("");

}

/* Search input handler for Industries */
function handleIndustrySearch(query) {

    const clearBtn = document.getElementById("searchIndustryClearBtn");
    if (clearBtn) {
        clearBtn.style.display = query.trim().length > 0 ? "flex" : "none";
    }

    renderMoreIndustries(query);

}

/* Clear search input for Industries */
function clearIndustrySearch() {

    const input = document.getElementById("searchIndustriesInput");
    const clearBtn = document.getElementById("searchIndustryClearBtn");

    if (input) {
        input.value = "";
        input.focus();
    }
    if (clearBtn) {
        clearBtn.style.display = "none";
    }

    renderMoreIndustries("");

}

/* Toggle More Industries Section Smoothly */
function toggleMoreIndustriesSection() {

    const section = document.getElementById("moreIndustriesSection");
    const btn = document.getElementById("moreIndustriesBtn");
    const input = document.getElementById("searchIndustriesInput");

    if (!section) return;

    // Smooth scroll down to the More Industries section
    section.scrollIntoView({ behavior: "smooth", block: "start" });

    // Focus search input
    setTimeout(() => {
        if (input) {
            input.focus();
        }
    }, 400);

    // Apply flash highlight to the section
    section.classList.remove("card-highlight-flash");
    void section.offsetWidth;
    section.classList.add("card-highlight-flash");

    if (btn) {
        btn.classList.add("active");
        setTimeout(() => btn.classList.remove("active"), 1200);
    }

}

/* Open Industry Profile Modal and display toast */
function openIndustryProfile(nameOrLink) {

    const query = String(nameOrLink).trim().toLowerCase();
    const ind = industries.find(i =>
        i.name.toLowerCase() === query ||
        (i.link && i.link.toLowerCase() === query)
    ) || {
        name: nameOrLink,
        sector: "Industrial Partner",
        icon: "🏢",
        description: "Active industrial partner contributing resources, technology, or funding to societal innovation in Jharkhand.",
        buttonText: "Partner With Us",
        focusAreas: ["Innovation", "Collaboration", "Deployment"]
    };

    currentProfileIndustry = ind;

    // Toast notification
    showToast(`Viewing industry partner: ${ind.name}`);

    // Populate modal
    const modalLogo = document.getElementById("modalIndLogo");
    const modalName = document.getElementById("modalIndName");
    const modalSector = document.getElementById("modalIndSector");
    const modalDomain = document.getElementById("modalIndDomain");
    const modalModel = document.getElementById("modalIndModel");
    const modalTags = document.getElementById("modalIndTags");
    const modalDesc = document.getElementById("modalIndDesc");
    const modalActionBtn = document.getElementById("modalIndActionBtn");

    if (modalLogo) modalLogo.textContent = ind.icon || ind.emoji || "🏢";
    if (modalName) modalName.textContent = ind.name;
    if (modalSector) modalSector.textContent = ind.sector || "Jharkhand Innovation Ecosystem Partner";
    if (modalDomain) modalDomain.textContent = ind.sector || "Industrial Sector";
    if (modalModel) modalModel.textContent = ind.buttonText || "Active Partner";
    if (modalDesc) modalDesc.textContent = ind.description || "";

    if (modalTags && ind.focusAreas) {
        modalTags.innerHTML = ind.focusAreas.map(tag => `<span>${escapeHtml(tag)}</span>`).join("\n");
    }

    if (modalActionBtn) {
        modalActionBtn.innerHTML = `<i class="ri-mail-send-line"></i> ${escapeHtml(ind.buttonText || "Partner With Us")}`;
    }

    // Open modal
    const modal = document.getElementById("industryProfileModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }

}

/* Close Industry Profile Modal */
function closeIndustryProfileModal() {

    const modal = document.getElementById("industryProfileModal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }

}

/* Handle click outside modal card */
function handleIndustryModalOverlayClick(event) {

    if (event.target && event.target.id === "industryProfileModal") {
        closeIndustryProfileModal();
    }

}

/* Collaborate action for Industry */
function initiateIndustryCollaboration() {

    const indName = currentProfileIndustry ? currentProfileIndustry.name : "Industry Partner";
    closeIndustryProfileModal();
    showToast(`Partnership inquiry submitted to ${indName}!`);

}

/* ==========================================================================
   ADMIN SETTINGS & STATE MANAGEMENT SYSTEM
   ==========================================================================
   Provides persistent configuration for:
   - Dark Mode & Visual Theme
   - Session & Authentication Flow (Login/Logout protection)
   - Profile & Account Management
   - Notification Channels
   - Preferences & Accessibility (Reduce motion, larger text, high contrast)
   - System Information
   - Settings Reset (Non-destructive to application records)
   ========================================================================== */

const SETTINGS_KEYS = {
    THEME: "samadhan_theme",
    LOGGED_IN: "samadhan_is_logged_in",
    PROFILE: "samadhan_user_profile",
    NOTIFICATIONS: "samadhan_notifications",
    PREFERENCES: "samadhan_preferences"
};

const DEFAULT_PROFILE = {
    fullName: "Praveen Kumar Sharma",
    email: "admin@jharkhand.gov.in",
    phone: "+91 94311 02845",
    role: "Portal Administrator",
    department: "Department of Higher & Technical Education, GoJ",
    location: "Ranchi, Jharkhand"
};

const DEFAULT_NOTIFICATIONS = {
    notifProblems: true,
    notifProjects: true,
    notifUniv: true,
    notifIndustry: true,
    notifSystem: true,
    notifEmail: false
};

const DEFAULT_PREFERENCES = {
    language: "en",
    defaultView: "dashboard",
    reduceMotion: false,
    largerText: false,
    highContrast: false
};

/* --------------------------------------------------------------------------
   1. THEME & DARK MODE MANAGEMENT
   -------------------------------------------------------------------------- */

function getSavedTheme() {
    try {
        return localStorage.getItem(SETTINGS_KEYS.THEME) || "light";
    } catch (e) {
        return "light";
    }
}

function applyTheme(theme) {
    const isDark = (theme === "dark");

    if (isDark) {
        document.documentElement.setAttribute("data-theme", "dark");
        document.body.classList.add("dark-theme", "dark-mode");
    } else {
        document.documentElement.removeAttribute("data-theme");
        document.body.classList.remove("dark-theme", "dark-mode");
    }

    // Synchronize toggle switch (supporting all ID variants)
    const themeCheckbox = document.getElementById("darkModeToggle") || document.getElementById("themeToggleCheckbox");
    if (themeCheckbox) {
        themeCheckbox.checked = isDark;
    }

    // Synchronize toggle status text
    const themeStatus = document.getElementById("themeToggleStatus");
    if (themeStatus) {
        themeStatus.textContent = isDark ? "Dark Mode Active" : "Light Mode Active";
    }

    // Synchronize theme option preview cards (supporting all ID variants)
    const lightCard = document.getElementById("themeCardLight") || document.getElementById("themeOptionLight");
    const darkCard = document.getElementById("themeCardDark") || document.getElementById("themeOptionDark");
    if (lightCard) lightCard.classList.toggle("active", !isDark);
    if (darkCard) darkCard.classList.toggle("active", isDark);

    // Synchronize System Information card (supporting all ID variants)
    const sysTheme = document.getElementById("sysInfoTheme") || document.getElementById("sysCurrentTheme");
    if (sysTheme) {
        sysTheme.textContent = isDark ? "Dark Mode" : "Light Mode";
    }

    // Synchronize Google Map dark mode theme
    if (typeof updateGoogleMapTheme === "function") {
        updateGoogleMapTheme(isDark);
    }
}

function toggleDarkMode(isDark) {
    const newTheme = isDark ? "dark" : "light";
    try {
        localStorage.setItem(SETTINGS_KEYS.THEME, newTheme);
    } catch (e) {
        console.warn("Unable to persist theme to localStorage", e);
    }
    applyTheme(newTheme);
    showToast(`Switched to ${isDark ? "Dark Mode" : "Light Mode"}`);
}

function selectTheme(theme) {
    try {
        localStorage.setItem(SETTINGS_KEYS.THEME, theme);
    } catch (e) {
        console.warn("Unable to persist theme to localStorage", e);
    }
    applyTheme(theme);
    showToast(`Theme updated: ${theme === "dark" ? "Dark Mode" : "Light Mode"}`);
}

// Immediate theme bootstrap to prevent light flash
(function() {
    try {
        const saved = localStorage.getItem("samadhan_theme");
        if (saved === "dark") {
            document.documentElement.setAttribute("data-theme", "dark");
            if (document.body) {
                document.body.classList.add("dark-theme", "dark-mode");
            }
        }
    } catch (e) {}
})();



/* --------------------------------------------------------------------------
   2. AUTHENTICATION & SESSION MANAGEMENT
   -------------------------------------------------------------------------- */

function isUserLoggedIn() {
    try {
        const status = localStorage.getItem(SETTINGS_KEYS.LOGGED_IN);
        // Default to logged in (true) so the portal is fully usable upon first load
        if (status === null) {
            localStorage.setItem(SETTINGS_KEYS.LOGGED_IN, "true");
            return true;
        }
        return status !== "false";
    } catch (e) {
        return true;
    }
}

function confirmLogout() {
    const modal = document.getElementById("logoutConfirmModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function closeLogoutModal() {
    const modal = document.getElementById("logoutConfirmModal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
}

function handleLogoutOverlayClick(event) {
    if (event.target && event.target.id === "logoutConfirmModal") {
        closeLogoutModal();
    }
}

function executeLogout() {
    closeLogoutModal();
    try {
        localStorage.setItem(SETTINGS_KEYS.LOGGED_IN, "false");
    } catch (e) {}

    // Display portal authentication overlay
    const loginOverlay = document.getElementById("loginOverlayView");
    if (loginOverlay) {
        loginOverlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    // Deactivate current active page to safeguard portal data
    const pages = document.querySelectorAll(".page");
    pages.forEach(p => p.classList.remove("active-page"));

    showToast("You have been safely logged out.");
}

function executeLogin(event) {
    if (event) event.preventDefault();

    try {
        localStorage.setItem(SETTINGS_KEYS.LOGGED_IN, "true");
    } catch (e) {}

    const loginOverlay = document.getElementById("loginOverlayView");
    if (loginOverlay) {
        loginOverlay.classList.remove("active");
        document.body.style.overflow = "";
    }

    // Navigate to dashboard
    showPage("dashboard");
    showToast("Welcome back, Portal Administrator!");
}


/* --------------------------------------------------------------------------
   3. ACCOUNT & PROFILE MANAGEMENT
   -------------------------------------------------------------------------- */

function getUserProfile() {
    try {
        const stored = localStorage.getItem(SETTINGS_KEYS.PROFILE);
        return stored ? { ...DEFAULT_PROFILE, ...JSON.parse(stored) } : { ...DEFAULT_PROFILE };
    } catch (e) {
        return { ...DEFAULT_PROFILE };
    }
}

function getInitials(name) {
    if (!name) return "AD";
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function renderUserProfile() {
    const profile = getUserProfile();
    const initials = getInitials(profile.fullName);

    // Profile Card Header (supports both HTML ID conventions)
    const pName = document.getElementById("settingsUserName") || document.getElementById("settingsProfileName");
    const pEmail = document.getElementById("settingsUserEmail") || document.getElementById("settingsProfileEmail");
    const pRole = document.getElementById("settingsUserRole") || document.getElementById("settingsProfileRole");
    const pInitials = document.getElementById("settingsAvatar") || document.getElementById("settingsAvatarInitials");

    if (pName) pName.textContent = profile.fullName;
    if (pEmail) pEmail.textContent = profile.email;
    if (pRole) pRole.textContent = profile.role;
    if (pInitials) pInitials.textContent = initials;

    // Detailed Account Info
    const dName = document.getElementById("settingsDetailName");
    const dEmail = document.getElementById("settingsDetailEmail");
    const dPhone = document.getElementById("settingsDetailPhone");
    const dDept = document.getElementById("settingsCellDept") || document.getElementById("settingsDetailDept");
    const dLoc = document.getElementById("settingsCellLocation") || document.getElementById("settingsDetailLocation");

    if (dName) dName.textContent = profile.fullName;
    if (dEmail) dEmail.textContent = profile.email;
    if (dPhone) dPhone.textContent = profile.phone;
    if (dDept) dDept.textContent = profile.department;
    if (dLoc) dLoc.textContent = profile.location;

    // Topbar synchronizations
    const topAvatar = document.getElementById("topbarAvatar");
    const topName = document.getElementById("topbarUserName");
    const topRole = document.getElementById("topbarUserRole");

    if (topAvatar) topAvatar.textContent = initials;
    if (topName) topName.textContent = profile.fullName;
    if (topRole) topRole.textContent = profile.role;
}

function openEditProfileModal() {
    const profile = getUserProfile();

    const inName = document.getElementById("editProfileName") || document.getElementById("editProfileFullName");
    const inEmail = document.getElementById("editProfileEmail");
    const inPhone = document.getElementById("editProfilePhone");
    const inDept = document.getElementById("editProfileDept");
    const inLoc = document.getElementById("editProfileLocation");

    if (inName) inName.value = profile.fullName || "";
    if (inEmail) inEmail.value = profile.email || "";
    if (inPhone) inPhone.value = profile.phone || "";
    if (inDept) inDept.value = profile.department || "";
    if (inLoc) inLoc.value = profile.location || "";

    const modal = document.getElementById("editProfileModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function closeEditProfileModal() {
    const modal = document.getElementById("editProfileModal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
}

function handleEditProfileOverlayClick(event) {
    if (event.target && event.target.id === "editProfileModal") {
        closeEditProfileModal();
    }
}

function saveUserProfile(event) {
    if (event) event.preventDefault();

    const nameInput = document.getElementById("editProfileName") || document.getElementById("editProfileFullName");
    const fullName = nameInput?.value.trim();
    const email = document.getElementById("editProfileEmail")?.value.trim();
    const phone = document.getElementById("editProfilePhone")?.value.trim();
    const department = document.getElementById("editProfileDept")?.value.trim();
    const location = document.getElementById("editProfileLocation")?.value.trim();

    if (!fullName || !email) {
        showToast("Full Name and Email Address are required.");
        return;
    }

    const current = getUserProfile();
    const updated = {
        ...current,
        fullName,
        email,
        phone: phone || current.phone,
        department: department || current.department,
        location: location || current.location
    };

    try {
        localStorage.setItem(SETTINGS_KEYS.PROFILE, JSON.stringify(updated));
    } catch (e) {
        console.warn("Unable to save profile to localStorage", e);
    }

    renderUserProfile();
    closeEditProfileModal();
    showToast("Profile information updated successfully!");
}


/* --------------------------------------------------------------------------
   4. SECURITY & PASSWORD MANAGEMENT
   -------------------------------------------------------------------------- */

function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const icon = btn.querySelector("i");
    if (input.type === "password") {
        input.type = "text";
        if (icon) {
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
        }
    } else {
        input.type = "password";
        if (icon) {
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
        }
    }
}

function handleChangePassword(event) {
    if (event) event.preventDefault();

    const curr = document.getElementById("currentPassword")?.value.trim();
    const newPwd = document.getElementById("newPassword")?.value.trim();
    const confirmPwd = document.getElementById("confirmNewPassword")?.value.trim();
    const feedbackBox = document.getElementById("securityFeedbackMessage");

    function showFeedback(msg, isSuccess = false) {
        if (feedbackBox) {
            feedbackBox.style.display = "block";
            feedbackBox.style.background = isSuccess ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)";
            feedbackBox.style.border = isSuccess ? "1px solid #10b981" : "1px solid #ef4444";
            feedbackBox.style.color = isSuccess ? "#059669" : "#dc2626";
            feedbackBox.innerHTML = `${isSuccess ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-circle-exclamation"></i>'} ${msg}`;
        }
    }

    if (!curr || !newPwd || !confirmPwd) {
        showFeedback("All password fields are required.");
        showToast("Please fill in all password fields.");
        return;
    }

    if (newPwd.length < 6) {
        showFeedback("New password must contain at least 6 characters.");
        showToast("Password must be at least 6 characters.");
        return;
    }

    if (newPwd !== confirmPwd) {
        showFeedback("New password and confirmation do not match.");
        showToast("New passwords do not match.");
        return;
    }

    if (curr === newPwd) {
        showFeedback("New password must be different from current password.");
        showToast("New password must be different.");
        return;
    }

    // Reset password form fields
    const form = document.getElementById("changePasswordForm");
    if (form) form.reset();

    // In accordance with requirements: Clearly keep UI prepared for backend API integration
    showFeedback("✓ Password validated successfully. Backend authentication API integration will apply this change to the database server.", true);
    showToast("Password validated! Ready for backend API integration.");
}


/* --------------------------------------------------------------------------
   5. NOTIFICATIONS & PREFERENCES MANAGEMENT
   -------------------------------------------------------------------------- */

function getNotificationPrefs() {
    try {
        const stored = localStorage.getItem(SETTINGS_KEYS.NOTIFICATIONS);
        return stored ? { ...DEFAULT_NOTIFICATIONS, ...JSON.parse(stored) } : { ...DEFAULT_NOTIFICATIONS };
    } catch (e) {
        return { ...DEFAULT_NOTIFICATIONS };
    }
}

const NOTIFICATION_FIELD_MAP = {
    problems: ["notifyProblems", "notifProblems"],
    projects: ["notifyProjects", "notifProjects"],
    universities: ["notifyUniversities", "notifUniv", "notifyUniv"],
    industry: ["notifyIndustry", "notifIndustry"],
    system: ["notifySystem", "notifSystem"],
    email: ["notifyEmail", "notifEmail"]
};

function saveNotificationPref(key, isChecked) {
    const current = getNotificationPrefs();
    // Normalize key to standard short form (e.g., 'notifProblems' -> 'problems')
    const cleanKey = key.replace(/^notif(y)?/i, "").toLowerCase();
    current[key] = isChecked;
    current[cleanKey] = isChecked;
    try {
        localStorage.setItem(SETTINGS_KEYS.NOTIFICATIONS, JSON.stringify(current));
    } catch (e) {}
    showToast("Notification preferences updated.");
}

function renderNotificationToggles() {
    const prefs = getNotificationPrefs();
    for (const [group, idList] of Object.entries(NOTIFICATION_FIELD_MAP)) {
        let val = prefs[group];
        if (val === undefined) {
            val = prefs["notif" + group.charAt(0).toUpperCase() + group.slice(1)];
        }
        if (val === undefined) {
            val = (group !== "email");
        }
        idList.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.checked = !!val;
        });
    }
}

function getGeneralPreferences() {
    try {
        const stored = localStorage.getItem(SETTINGS_KEYS.PREFERENCES);
        return stored ? { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) } : { ...DEFAULT_PREFERENCES };
    } catch (e) {
        return { ...DEFAULT_PREFERENCES };
    }
}

function saveGeneralPref(key, value) {
    const prefs = getGeneralPreferences();
    prefs[key] = value;
    try {
        localStorage.setItem(SETTINGS_KEYS.PREFERENCES, JSON.stringify(prefs));
    } catch (e) {}
    if (key === "language") {
        showToast(`Language set to ${value === 'hi' ? 'Hindi (हिंदी)' : 'English'}. Multilingual architecture ready.`);
    } else if (key === "defaultView") {
        showToast(`Default view set to: ${value.toUpperCase()}`);
    }
}

function toggleReduceMotion(enabled) {
    document.body.classList.toggle("reduce-motion", enabled);
    const prefs = getGeneralPreferences();
    prefs.reduceMotion = enabled;
    try {
        localStorage.setItem(SETTINGS_KEYS.PREFERENCES, JSON.stringify(prefs));
    } catch (e) {}
    showToast(`Reduced animations ${enabled ? "enabled" : "disabled"}`);
}

function toggleLargerText(enabled) {
    document.body.classList.toggle("larger-text", enabled);
    const prefs = getGeneralPreferences();
    prefs.largerText = enabled;
    try {
        localStorage.setItem(SETTINGS_KEYS.PREFERENCES, JSON.stringify(prefs));
    } catch (e) {}
    showToast(`Larger text mode ${enabled ? "enabled" : "disabled"}`);
}

function toggleHighContrast(enabled) {
    document.body.classList.toggle("high-contrast", enabled);
    const prefs = getGeneralPreferences();
    prefs.highContrast = enabled;
    try {
        localStorage.setItem(SETTINGS_KEYS.PREFERENCES, JSON.stringify(prefs));
    } catch (e) {}
    showToast(`High contrast mode ${enabled ? "enabled" : "disabled"}`);
}

function renderPreferences() {
    const prefs = getGeneralPreferences();

    const lang = document.getElementById("prefLanguage");
    if (lang) lang.value = prefs.language || "en";

    const defView = document.getElementById("prefDefaultView");
    if (defView) defView.value = prefs.defaultView || "dashboard";

    const chkMotion = document.getElementById("prefReduceMotion");
    if (chkMotion) chkMotion.checked = !!prefs.reduceMotion;
    document.body.classList.toggle("reduce-motion", !!prefs.reduceMotion);

    const chkText = document.getElementById("prefLargerText");
    if (chkText) chkText.checked = !!prefs.largerText;
    document.body.classList.toggle("larger-text", !!prefs.largerText);

    const chkContrast = document.getElementById("prefHighContrast");
    if (chkContrast) chkContrast.checked = !!prefs.highContrast;
    document.body.classList.toggle("high-contrast", !!prefs.highContrast);
}


/* --------------------------------------------------------------------------
   6. RESET SETTINGS (NON-DESTRUCTIVE)
   -------------------------------------------------------------------------- */

function confirmResetSettings() {
    const modal = document.getElementById("resetSettingsConfirmModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function closeResetSettingsModal() {
    const modal = document.getElementById("resetSettingsConfirmModal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
}

function handleResetOverlayClick(event) {
    if (event.target && event.target.id === "resetSettingsConfirmModal") {
        closeResetSettingsModal();
    }
}

function executeResetSettings() {
    closeResetSettingsModal();

    try {
        // Reset Theme to Light
        localStorage.setItem(SETTINGS_KEYS.THEME, "light");
        applyTheme("light");

        // Reset Notifications
        localStorage.setItem(SETTINGS_KEYS.NOTIFICATIONS, JSON.stringify(DEFAULT_NOTIFICATIONS));
        renderNotificationToggles();

        // Reset Preferences
        localStorage.setItem(SETTINGS_KEYS.PREFERENCES, JSON.stringify(DEFAULT_PREFERENCES));
        renderPreferences();
    } catch (e) {
        console.warn("Error resetting settings", e);
    }

    showToast("Settings reset to defaults! Portal and account data preserved.");
}

function saveAllSettingsManual() {
    showToast("Settings saved successfully.");
}

function initializeSettings() {
    // 1. Apply Theme
    const savedTheme = getSavedTheme();
    applyTheme(savedTheme);

    // 2. Auth / Session Check
    if (!isUserLoggedIn()) {
        const loginOverlay = document.getElementById("loginOverlayView");
        if (loginOverlay) {
            loginOverlay.classList.add("active");
            document.body.style.overflow = "hidden";
        }
    } else {
        const loginOverlay = document.getElementById("loginOverlayView");
        if (loginOverlay) {
            loginOverlay.classList.remove("active");
            document.body.style.overflow = "";
        }
    }

    // 3. Render Profile
    renderUserProfile();

    // 4. Render Notifications
    renderNotificationToggles();

    // 5. Render Preferences & Accessibility
    renderPreferences();
}


/* ==========================================================================
   SMART INDIA HACKATHON 2026: AUTOMATIC UNIVERSITY + INDUSTRY MATCHING ENGINE
   ==========================================================================
   Enterprise explainable recommendation and collaboration system.
   Features:
   - Multi-factor weighted university & industry matching (exact weights).
   - Problem NLP extraction (skills, domains, tech, resources, priority, impact).
   - Dynamic caching and local persistence in localStorage.
   - Solution lifecycle tracker (Recommended -> Interested -> Accepted -> In Collaboration -> Prototype -> Testing -> Deployed -> Completed).
   - Real-time notification center and live badge counter.
   - Dual-mode API adapter (synchronizes with Python backend if active, or runs standalone in-browser).
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. DOMAIN TAXONOMY & KEYWORD DICTIONARIES
   -------------------------------------------------------------------------- */

const MATCHING_TAXONOMY = {
    Water: {
        subcategories: ["Drinking Water", "Water Quality", "Groundwater Depletion", "Piped Water", "Irrigation Canals", "Mine Water Treatment"],
        skills: ["IoT", "Water Quality Analysis", "Civil Engineering", "Hydrogeology", "SCADA", "Sensor Interfacing", "Filtration Chemistry", "Data Analytics"],
        domains: ["Civil Engineering", "Environmental Engineering", "Computer Science", "Chemistry", "Water Resource Management", "Earth Sciences"],
        technology: ["IoT Water Sensors", "RO Purification", "Solar Water Pumps", "Telemetry SCADA", "GIS Mapping", "Smart Meters"],
        resources: ["Water Testing Lab", "Environmental Chemistry Lab", "Pilot Filtration Plant", "CSR Infrastructure Grants", "Field Technicians"]
    },
    Agriculture: {
        subcategories: ["Drip Irrigation", "Soil Fertility", "Plateau Crops", "Cold Storage", "Pest Detection", "Farmer Market Access"],
        skills: ["Precision Farming", "AgriTech IoT", "Soil Chemistry", "Crop Pathology", "Drone Remote Sensing", "Embedded Systems", "Agro-Forestry"],
        domains: ["Agriculture Science", "Soil Sciences", "Biotechnology", "Electronics Engineering", "Agro-Economics", "Robotics"],
        technology: ["Smart Drip Telemetry", "Drone Multispectral Imaging", "Solar Cold Storage", "Mobile Advisory Apps", "Automated Greenhouses"],
        resources: ["Agricultural Research Farm", "Soil Analysis Lab", "Drone Fleet", "Agri-Incubation Center", "FPO Network"]
    },
    Healthcare: {
        subcategories: ["Primary Care Access", "Telemedicine", "Maternal Health", "Malnutrition", "Rural Diagnostics", "Mobile Medical Units"],
        skills: ["Tele-health Diagnostics", "Biomedical Engineering", "Public Health", "Clinical AI", "Embedded Medical Sensors", "Epidemiology"],
        domains: ["Medical & Health Sciences", "Public Health", "Biotechnology", "Computer Science", "Pharmaceutical Sciences"],
        technology: ["Telemedicine Kiosks", "Point-of-Care Blood Testing", "Portable ECG/Ultrasound", "Health Cloud Records", "AI Diagnostic Screeners"],
        resources: ["Apex Hospital Beds", "Clinical Diagnostics Lab", "Biomedical Prototyping Lab", "Ambulance Network", "CSR Healthcare Grants"]
    },
    Education: {
        subcategories: ["Teacher Shortage", "Digital Classrooms", "STEM Education", "Vernacular Learning", "Vocational Training", "Tribal Literacy"],
        skills: ["EdTech Software", "Curriculum Design", "Vernacular NLP", "Interactive Pedagogy", "Offline Digital Content", "Hardware Maintenance"],
        domains: ["Computer Science / AI", "Humanities", "Tribal & Regional Languages", "Education Technology", "Social Sciences"],
        technology: ["Solar Powered Tablets", "Offline Content Servers", "Smart Class Interactive Displays", "Speech Recognition for Tribal Dialects"],
        resources: ["STEM Tinkering Labs", "Digital Content Studio", "Teacher Training Facility", "CSR Education Grants"]
    },
    Environment: {
        subcategories: ["Industrial Slag Recycling", "Mine Land Reclamation", "Air & Water Pollution", "Solid Waste Management", "Plastic Upcycling", "Forest Conservation"],
        skills: ["Waste Valorization", "Environmental Chemistry", "Mine Tailings Stabilization", "Ecology & Forestry", "Air Quality Monitoring"],
        domains: ["Environmental Science", "Mining & Mineral Engineering", "Metallurgy & Materials Science", "Chemical Engineering", "Ecology"],
        technology: ["Continuous Emission Monitoring (CEMS)", "Geopolymer Brick Plants", "Pyrolysis Units", "Drone Forest Canopy Scanners"],
        resources: ["Environmental Testing Lab", "Slag Characterization Facility", "Materials Synthesis Lab", "Heavy Machinery"]
    },
    Energy: {
        subcategories: ["Rural Solar Microgrids", "Biomass Energy", "Grid Reliability", "Mine Methane Recovery", "Energy Storage"],
        skills: ["Solar PV Engineering", "Microgrid SCADA", "Battery Energy Storage", "Power Electronics", "Renewable Energy Economics"],
        domains: ["Electrical Engineering", "Energy Engineering", "Clean Energy", "Physics", "Computer Science"],
        technology: ["Solar PV Arrays", "Lithium / Flow Batteries", "Smart Inverters", "Remote Energy Monitoring", "Smart Pre-paid Meters"],
        resources: ["High Voltage Testing Lab", "Solar Simulator", "Battery Prototyping Workshop", "Clean Energy Grants"]
    },
    "Water Management": {
        subcategories: ["Drinking Water", "Water Quality", "Groundwater Depletion", "Piped Water", "Irrigation Canals", "Mine Water Treatment"],
        skills: ["IoT", "Water Quality Analysis", "Civil Engineering", "Hydrogeology", "SCADA", "Sensor Interfacing", "Filtration Chemistry", "Data Analytics"],
        domains: ["Civil Engineering", "Environmental Engineering", "Computer Science", "Chemistry", "Water Resource Management", "Earth Sciences"],
        technology: ["IoT Water Sensors", "RO Purification", "Solar Water Pumps", "Telemetry SCADA", "GIS Mapping", "Smart Meters"],
        resources: ["Water Testing Lab", "Environmental Chemistry Lab", "Pilot Filtration Plant", "CSR Infrastructure Grants", "Field Technicians"]
    },
    Sanitation: {
        subcategories: ["Solid Waste Collection", "Sewage Treatment", "Community Toilets", "Drainage Systems", "Waste Recycling"],
        skills: ["Sanitation Engineering", "Waste Management", "Biochemical Treatment", "Civil Engineering", "Urban Planning"],
        domains: ["Environmental Engineering", "Civil Engineering", "Public Health", "Biotechnology"],
        technology: ["Bio-Digester Toilets", "Smart Waste Bins", "Sewage Treatment Plants (STP)", "Waste Shredders"],
        resources: ["Sanitation Testing Lab", "Municipal Waste Facility", "Composting Unit"]
    },
    "Urban Infrastructure": {
        subcategories: ["Road Maintenance", "Stormwater Drainage", "Smart Streetlighting", "Bridge Safety", "Public Transport"],
        skills: ["Civil & Structural Engineering", "Pavement Design", "IoT Traffic Systems", "Urban Planning", "GIS Mapping"],
        domains: ["Civil Engineering", "Transportation Engineering", "Urban Planning", "Electrical Engineering"],
        technology: ["Cold Mix Asphalt", "Pothole Detection Drones", "Smart LED Telemetry", "Structural Health Sensors"],
        resources: ["Materials Testing Lab", "Structural Dynamics Lab", "Heavy Machinery Network"]
    },
    "Urban Development": {
        subcategories: ["Road Maintenance", "Stormwater Drainage", "Smart Streetlighting", "Bridge Safety", "Public Transport"],
        skills: ["Civil & Structural Engineering", "Pavement Design", "IoT Traffic Systems", "Urban Planning", "GIS Mapping"],
        domains: ["Civil Engineering", "Transportation Engineering", "Urban Planning", "Electrical Engineering"],
        technology: ["Cold Mix Asphalt", "Pothole Detection Drones", "Smart LED Telemetry", "Structural Health Sensors"],
        resources: ["Materials Testing Lab", "Structural Dynamics Lab", "Heavy Machinery Network"]
    },
    "Rural Livelihoods": {
        subcategories: ["Tribal Artisan Clusters", "Handloom & Tussar Silk", "Agro-Processing", "Dairy & Poultry", "Self-Help Groups"],
        skills: ["Textile Technology", "Supply Chain Management", "Agro-Enterprise", "Product Design", "Digital Marketing"],
        domains: ["Social Work", "Textile Engineering", "Rural Development", "Management Studies"],
        technology: ["Solar Weaving Looms", "Cold Chain Logistics", "E-Commerce Marketplaces", "Traceability QR"],
        resources: ["Artisan Design Studio", "Testing Center", "Incubation Center"]
    },
    "Rural Livelihood": {
        subcategories: ["Tribal Artisan Clusters", "Handloom & Tussar Silk", "Agro-Processing", "Dairy & Poultry", "Self-Help Groups"],
        skills: ["Textile Technology", "Supply Chain Management", "Agro-Enterprise", "Product Design", "Digital Marketing"],
        domains: ["Social Work", "Textile Engineering", "Rural Development", "Management Studies"],
        technology: ["Solar Weaving Looms", "Cold Chain Logistics", "E-Commerce Marketplaces", "Traceability QR"],
        resources: ["Artisan Design Studio", "Testing Center", "Incubation Center"]
    },
    Accessibility: {
        subcategories: ["Wheelchair Mobility", "Assistive Tech for Visually Impaired", "Barrier-Free Public Spaces", "Deaf & Mute Aids"],
        skills: ["Assistive Technology", "Biomechanics", "Embedded Systems", "Universal Design", "Computer Vision"],
        domains: ["Biomedical Engineering", "Computer Science", "Architecture", "Mechanical Engineering"],
        technology: ["Smart White Canes", "Automated Wheelchair Ramps", "Haptic Navigation Devices", "Text-to-Speech AI"],
        resources: ["Assistive Devices Lab", "Prototyping Workshop", "Ergonomics Evaluation Lab"]
    },
    "Public Services": {
        subcategories: ["E-Governance Delivery", "Public Grievance Redressal", "Welfare Scheme Access", "Panchayat Digitization"],
        skills: ["Software Engineering", "Public Administration", "Cybersecurity", "Cloud Architecture", "Data Science"],
        domains: ["Computer Science", "Public Policy", "Information Technology", "Law"],
        technology: ["Blockchain Certificate Registry", "Citizen Mobile Portals", "AI Helpdesk Bots", "Biometric Authentication"],
        resources: ["E-Gov Testing Center", "Data Center", "Cloud Server Infrastructure"]
    },
    "Public Administration": {
        subcategories: ["E-Governance Delivery", "Public Grievance Redressal", "Welfare Scheme Access", "Panchayat Digitization"],
        skills: ["Software Engineering", "Public Administration", "Cybersecurity", "Cloud Architecture", "Data Science"],
        domains: ["Computer Science", "Public Policy", "Information Technology", "Law"],
        technology: ["Blockchain Certificate Registry", "Citizen Mobile Portals", "AI Helpdesk Bots", "Biometric Authentication"],
        resources: ["E-Gov Testing Center", "Data Center", "Cloud Server Infrastructure"]
    },
    "Disaster Management": {
        subcategories: ["Flood Early Warning", "Drought Relief", "Landslide Monitoring", "Emergency Shelter Logistics", "Cyclone Response"],
        skills: ["Geotechnical Engineering", "Remote Sensing & GIS", "Hydrological Modeling", "Disaster Logistics", "IoT Telemetry"],
        domains: ["Earth Sciences", "Civil Engineering", "Environmental Science", "Computer Science"],
        technology: ["River Gauge Telemetry", "Early Warning Sirens", "Drone Reconnaissance Fleet", "Satellite Inundation Maps"],
        resources: ["Emergency Operations Center", "Disaster Drone Fleet", "Hydraulic Testing Lab"]
    },
    Other: {
        subcategories: ["Community Innovation", "Grassroots Solutions", "General Development", "Civic Tech"],
        skills: ["Problem Solving", "Prototyping", "Interdisciplinary Engineering", "Community Engagement"],
        domains: ["Interdisciplinary Sciences", "Social Innovation", "Engineering Design"],
        technology: ["Rapid Prototyping", "Open Source Hardware", "Mobile Apps"],
        resources: ["Maker Space", "Innovation Hub", "Incubator"]
    }
};

const STOPWORDS_SET = new Set([
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "is", "are", "was", "were", "and", "or", "as", "be", "has", "have", "had",
    "that", "this", "these", "those", "it", "its", "their", "our", "village", "villagers",
    "district", "jharkhand", "area", "problem", "issue", "need", "facing", "required"
]);


/* --------------------------------------------------------------------------
   2. TEXT PROCESSING & VECTOR SIMILARITY (TF-IDF)
   -------------------------------------------------------------------------- */

function tokenizeText(text) {
    if (!text) return [];
    return String(text)
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, " ")
        .split(/\s+/)
        .filter(w => w.length > 2 && !STOPWORDS_SET.has(w));
}

function computeTermFreq(tokens) {
    const tf = {};
    if (!tokens || tokens.length === 0) return tf;
    tokens.forEach(t => { tf[t] = (tf[t] || 0) + 1; });
    const total = tokens.length;
    Object.keys(tf).forEach(k => { tf[k] = tf[k] / total; });
    return tf;
}

function calculateCosineSimilarity(vecA, vecB) {
    const keysA = Object.keys(vecA);
    const keysB = new Set(Object.keys(vecB));
    const commonKeys = keysA.filter(k => keysB.has(k));
    if (commonKeys.length === 0) return 0;

    let dot = 0;
    commonKeys.forEach(k => { dot += vecA[k] * vecB[k]; });

    let normA = 0;
    keysA.forEach(k => { normA += vecA[k] * vecA[k]; });
    normA = Math.sqrt(normA);

    let normB = 0;
    Object.values(vecB).forEach(v => { normB += v * v; });
    normB = Math.sqrt(normB);

    if (normA === 0 || normB === 0) return 0;
    return dot / (normA * normB);
}

function calculateJaccardIndex(listA, listB) {
    if (!listA || !listB || listA.length === 0 || listB.length === 0) return 0;
    const setA = new Set(listA.map(s => String(s).trim().toLowerCase()));
    const setB = new Set(listB.map(s => String(s).trim().toLowerCase()));
    const intersection = [...setA].filter(x => setB.has(x)).length;
    const union = new Set([...setA, ...setB]).size;
    return union > 0 ? intersection / union : 0;
}


/* --------------------------------------------------------------------------
   3. DATA ENRICHMENT: UNIVERSITIES & INDUSTRIES
   -------------------------------------------------------------------------- */

// Specific institutional capability profiles for Jharkhand Universities
const UNIVERSITY_ENRICHMENTS = {
    "bit-mesra": {
        id: "bit-mesra",
        departments: ["Civil & Environmental Engineering", "Computer Science & Engineering", "Space Engineering & Rocketry", "Electrical & Electronics"],
        academicDomains: ["Civil Engineering", "Environmental Engineering", "Computer Science", "IoT", "Data Analytics"],
        facultyExpertise: ["Dr. S. K. Verma (Water Quality)", "Dr. A. Mustafi (Edge IoT)", "Dr. N. Patra (Autonomous Systems)"],
        researchAreas: ["IoT Water Quality Telemetry", "Autonomous Drone Sensors", "Plateau Soil Geotechnics", "Clean Energy"],
        facilities: ["Environmental Pollution Testing Lab", "Advanced VLSI & IoT Systems Center", "High Performance Computing Lab"],
        innovationCapabilities: ["TIH Technology Innovation Hub", "DST-Supported Incubator", "Patent Facilitation Cell"],
        previousProjects: ["Subarnarekha River Basin Telemetry Pilot", "Smart Microgrid for Khunti Villages"],
        studentSkills: ["Embedded C/C++", "IoT Hardware Prototyping", "Python / ML", "Civil GIS Mapping"]
    },
    "iit-ism": {
        id: "iit-ism",
        departments: ["Environmental Science & Engineering", "Mining Engineering", "Computer Science & Engineering", "Civil Engineering"],
        academicDomains: ["Environmental Engineering", "Mining & Mineral Engineering", "Water Resource Management", "Earth Sciences", "AI/ML"],
        facultyExpertise: ["Prof. G. Udayabhanu (Mine Water Remediation)", "Prof. C. Banerjee (Geophysics)", "Prof. A. K. Pal (Slag Valorization)"],
        researchAreas: ["Mine Acid Water Neutralization", "Heavy Metal Filtration", "Remote Sensing & GIS", "Tailings Stabilization"],
        facilities: ["Apex Water Chemistry Lab", "Centre for Mining Environment", "GIS & Satellite Imagery Lab"],
        innovationCapabilities: ["IIT Innovation & Incubation Centre (CIIE)", "TEXMiN Technology Innovation Hub"],
        previousProjects: ["Dhanbad Coalfield Acid Mine Drainage Treatment", "Drinking Water Supply to Jharia Resettlement Colony"],
        studentSkills: ["Water Quality Testing", "Hydrogeological Modeling", "IoT Telemetry", "Drone Surveying"]
    },
    "nit-jsr": {
        id: "nit-jsr",
        departments: ["Civil Engineering", "Metallurgical & Materials Engineering", "Electrical Engineering", "Computer Science"],
        academicDomains: ["Civil Engineering", "Smart Infrastructure", "Metallurgy", "Clean Energy", "Robotics"],
        facultyExpertise: ["Dr. S. K. Prasad (Water Infrastructure)", "Dr. R. V. Sharma (Renewables)", "Dr. D. S. Rao (Materials)"],
        researchAreas: ["Sustainable Water Pipelines", "Industrial Waste Recycling", "Solar Microgrids", "Smart Sensors"],
        facilities: ["Materials Characterization Center", "Fluid Mechanics & Hydraulics Lab", "Smart Grid Demonstration Unit"],
        innovationCapabilities: ["MSME Incubation Centre", "Maker Space Workshop"],
        previousProjects: ["Subarnarekha Industrial Effluent Treatment Model", "East Singhbhum Village Solar Pumping Pilot"],
        studentSkills: ["Hydraulic Modeling", "CAD/SolidWorks", "Embedded Systems", "Water Quality Assay"]
    },
    "bau": {
        id: "bau",
        departments: ["Soil Science & Agricultural Chemistry", "Agricultural Engineering", "Forestry", "Agronomy"],
        academicDomains: ["Agriculture Science", "Soil Sciences", "Biotechnology", "Agro-Forestry", "Water Resource Management"],
        facultyExpertise: ["Dr. B. K. Agarwal (Plateau Soil Fertility)", "Dr. D. N. Singh (Drought Resistant Crops)", "Dr. P. Kaushik (Irrigation)"],
        researchAreas: ["Drought-Resilient Plateau Crops", "Micro-Irrigation Telemetry", "Soil Revitalization", "Bio-Fertilizers"],
        facilities: ["Central Instrumentation Lab", "Soil Health Testing Vans", "Plateau Experimental Research Farms"],
        innovationCapabilities: ["Agri-Business Incubator (RABI)", "Krishi Vigyan Kendra (KVK) Network"],
        previousProjects: ["Deoghar District Drip Irrigation Scheme", "Jharkhand Millets Mission Seed Bank"],
        studentSkills: ["Soil Analysis", "Drip System Assembly", "Crop Diagnostics", "Farmer Field Training"]
    },
    "aiims-deoghar": {
        id: "aiims-deoghar",
        departments: ["Community Medicine & Public Health", "Biochemistry & Pathology", "General Medicine", "Pediatrics"],
        academicDomains: ["Medical & Health Sciences", "Public Health", "Clinical AI", "Epidemiology", "Biotechnology"],
        facultyExpertise: ["Dr. S. Sengupta (Rural Epidemiology)", "Dr. M. K. Panda (Telemedicine Diagnostics)"],
        researchAreas: ["Remote Diagnostic Screener Systems", "Waterborne Disease Surveillance", "Maternal Nutrition"],
        facilities: ["Apex Molecular Biology Lab", "Telemedicine Outpost Hub", "Clinical Diagnostics Center"],
        innovationCapabilities: ["Medical Innovation & Device Testing Cell", "ICMR Research Center"],
        previousProjects: ["Santhal Pargana Waterborne Fluorosis Screening", "Mobile Primary Diagnostic Units in Dumka"],
        studentSkills: ["Public Health Screening", "Point-of-Care Testing", "Biostatistics", "Clinical Data Analysis"]
    },
    "iiit-ranchi": {
        id: "iiit-ranchi",
        departments: ["Computer Science & Engineering", "Electronics & Communication Engineering"],
        academicDomains: ["Computer Science / AI", "IoT & Sensor Networks", "Data Analytics", "Cybersecurity", "Embedded Systems"],
        facultyExpertise: ["Dr. J. K. Roy (Deep Learning)", "Dr. P. Sharma (Edge Computing & IoT)", "Dr. R. Soren (Vernacular NLP)"],
        researchAreas: ["Edge AI Sensor Networks", "Vernacular Language Chatbots for Citizens", "Rural Telemetry Systems"],
        facilities: ["Nvidia GPU AI Cluster", "IoT & Embedded Prototyping Lab", "Cyber-Physical Systems Lab"],
        innovationCapabilities: ["T-Hub Innovation Cell", "Open-Source Software Development Center"],
        previousProjects: ["Jharkhand Citizen Grievance AI Categorizer", "Rural School Offline Digital Learning Tablet App"],
        studentSkills: ["Python / TensorFlow", "React / Web Apps", "ESP32 / Arduino Firmware", "PostgreSQL / Cloud"]
    },
    "cuj": {
        id: "cuj",
        departments: ["Water Engineering & Management", "Energy Engineering", "Environmental Sciences", "Tribal Studies"],
        academicDomains: ["Water Resource Management", "Environmental Engineering", "Energy Engineering", "Tribal Studies"],
        facultyExpertise: ["Dr. M. K. Yadav (Hydrology)", "Dr. B. Das (Green Hydrogen)", "Dr. S. K. Mishra (Water Filtration)"],
        researchAreas: ["Fluoride & Arsenic Water Remediation", "Decentralized Solar Water Kiosks", "Indigenous Biodiversity Conservation"],
        facilities: ["Centre for Water Engineering", "Renewable Energy Research Park", "Nanomaterials Fabrication Lab"],
        innovationCapabilities: ["University Innovation Cluster", "MoE-Supported Design Innovation Centre"],
        previousProjects: ["Gumla Low-Cost Drinking Water Filtration Filter Units", "Solar Water Micro-Utility in Khunti"],
        studentSkills: ["Water Quality Testing", "Nanofiltration Assembly", "GIS Watershed Analysis", "Field Surveying"]
    }
};

// Apply enrichments dynamically across all 24 universities
universities.forEach(u => {
    const linkKey = u.link || u.name.replace(/\s+/g, '-').toLowerCase();
    const specific = UNIVERSITY_ENRICHMENTS[linkKey];
    u.id = linkKey;
    if (specific) {
        Object.assign(u, specific);
    } else {
        u.departments = u.departments || ["School of Science & Technology", "Department of Rural Development"];
        u.academicDomains = u.academicDomains || u.researchStreams || ["Applied Sciences", "Regional Development"];
        u.facultyExpertise = u.facultyExpertise || ["Regional Academic Research Faculty", "Faculty Project Director"];
        u.researchAreas = u.researchAreas || u.researchStreams || ["Societal Innovation"];
        u.facilities = u.facilities || ["Central Research Laboratory", "Student Innovation Center"];
        u.innovationCapabilities = u.innovationCapabilities || ["Institutional Incubation Cell"];
        u.previousProjects = u.previousProjects || ["Jharkhand Higher Education Community Impact Project"];
        u.studentSkills = u.studentSkills || ["Data Collection", "Prototype Fabrication", "Community Survey"];
    }
});

// Specific capability profiles for Jharkhand Industries & CSR Partners
const INDUSTRY_ENRICHMENTS = {
    "water-management": {
        id: "water-management",
        technologies: ["IoT Water Sensors", "RO & Nano Filtration", "Solar Powered Pumping", "SCADA Telemetry", "Smart Water Meters"],
        skills: ["Water Quality Analysis", "Civil Pipeline Engineering", "SCADA Integration", "Community Training"],
        csrFocusAreas: ["Drinking Water Access", "Rural Sanitation", "Groundwater Recharge", "Jal Jeevan Mission Support"],
        fundingCapability: "High",
        mentoringCapability: true,
        prototypingCapability: true,
        deploymentCapability: true,
        district: "Ranchi",
        previousCollaborations: ["UNICEF Rural Water Access Project", "Jharkhand Drinking Water & Sanitation Dept Pilot"]
    },
    "agritech": {
        id: "agritech",
        technologies: ["Smart Drip Irrigation", "Soil Moisture IoT Sensors", "Solar Cold Storage", "Mobile Advisory Systems"],
        skills: ["Precision Irrigation", "Sensor Interfacing", "Farming Systems Analysis", "Supply Chain"],
        csrFocusAreas: ["Smallholder Farmer Livelihoods", "Water Conservation", "Organic Plateau Agriculture"],
        fundingCapability: "High",
        mentoringCapability: true,
        prototypingCapability: true,
        deploymentCapability: true,
        district: "Ranchi",
        previousCollaborations: ["Birsa Agricultural University Field Pilots", "NABARD FPO Solar Pump Integration"]
    },
    "electronics": {
        id: "electronics",
        technologies: ["IoT Sensors", "Embedded Microcontrollers (ESP32/STM32)", "Solar Charge Controllers", "LoRaWAN Gateways"],
        skills: ["PCB Design", "Firmware Engineering", "Hardware Prototyping", "Telemetry SCADA"],
        csrFocusAreas: ["Rural STEM Education", "Digital Infrastructure", "Clean Energy Telemetry"],
        fundingCapability: "Medium",
        mentoringCapability: true,
        prototypingCapability: true,
        deploymentCapability: true,
        district: "East Singhbhum",
        previousCollaborations: ["NIT Jamshedpur Maker Lab", "Smart City Ranchi Streetlight Telemetry"]
    },
    "csr-organizations": {
        id: "csr-organizations",
        technologies: ["Impact Tracking Dashboards", "Beneficiary Verification Portals", "Mobile Monitoring"],
        skills: ["CSR Grant Deployment", "Community Mobilization", "Monitoring & Evaluation", "Regulatory Compliance"],
        csrFocusAreas: ["Drinking Water", "Education & Digital Literacy", "Healthcare in Tribal Pockets", "Youth Employment"],
        fundingCapability: "High",
        mentoringCapability: true,
        prototypingCapability: false,
        deploymentCapability: true,
        district: "Ranchi",
        previousCollaborations: ["Tata Steel Foundation Rural Water Partnership", "Central Coalfields CSR Health Kiosks"]
    },
    "renewable-energy": {
        id: "renewable-energy",
        technologies: ["Solar PV Systems", "Lithium Battery Energy Storage (BESS)", "Microgrid Controllers", "Pre-paid Metering"],
        skills: ["Solar Engineering", "Microgrid Architecture", "High Voltage Safety", "Feeder Telemetry"],
        csrFocusAreas: ["Rural Electrification", "Zero Emission Energy", "Tribal Village Solar Mini-Grids"],
        fundingCapability: "High",
        mentoringCapability: true,
        prototypingCapability: true,
        deploymentCapability: true,
        district: "Ranchi",
        previousCollaborations: ["JREDA Forest Village Electrification", "BIT Mesra Solar Microgrid Demonstration"]
    }
};

// Apply enrichments dynamically across all 25 industries
industries.forEach(i => {
    const linkKey = i.link || i.name.replace(/\s+/g, '-').toLowerCase();
    const specific = INDUSTRY_ENRICHMENTS[linkKey];
    i.id = linkKey;
    if (specific) {
        Object.assign(i, specific);
    } else {
        i.technologies = i.technologies || i.focusAreas || ["Industrial Equipment", "Automation Tools"];
        i.skills = i.skills || ["Operations", "Quality Assurance", "Prototyping"];
        i.csrFocusAreas = i.csrFocusAreas || i.focusAreas || ["Community Welfare", "Skill Development"];
        i.fundingCapability = i.fundingCapability || "Medium";
        i.mentoringCapability = true;
        i.prototypingCapability = true;
        i.deploymentCapability = true;
        i.district = i.district || "Ranchi";
        i.previousCollaborations = i.previousCollaborations || ["Jharkhand State Industrial Partnership"];
    }
});


/* --------------------------------------------------------------------------
   4. SAMPLE COMMUNITY PROBLEMS DATASET
   -------------------------------------------------------------------------- */

const SAMPLE_PROBLEMS = [
    {
        "id": "SCP-1001",
        "title": "Smart Digital STEM Labs for Peri-Urban Schools",
        "description": "Government schools around Ranchi lack modern science labs and interactive digital kits. A low-cost vernacular digital lab with simulations is needed.",
        "category": "Education",
        "subCategory": "Digital Classrooms",
        "location": "Kanke Block, Ranchi",
        "district": "Ranchi",
        "state": "Jharkhand",
        "latitude": 23.435,
        "longitude": 85.321,
        "current_latitude": 23.431,
        "current_longitude": 85.325,
        "distance_km": 0.6,
        "mismatch_distance_km": 0.6,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 3,
        "priority": "High",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1002",
        "title": "Mobile Tele-Clinic & Diagnostics for Remote Tribal Hamlets",
        "description": "Tribal hamlets on the outskirts of Ranchi require portable point-of-care diagnostics and telemedicine consultations with specialists.",
        "category": "Healthcare",
        "subCategory": "Telemedicine",
        "location": "Burmu Block, Ranchi",
        "district": "Ranchi",
        "state": "Jharkhand",
        "latitude": 23.582,
        "longitude": 85.122,
        "current_latitude": 23.585,
        "current_longitude": 85.12,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 4,
        "priority": "High",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1003",
        "title": "Decentralized Organic Waste Composting for Daily Vegetable Mandis",
        "description": "Severe organic vegetable waste accumulation at wholesale mandis in Ranchi causing foul smell and drainage blockage. Requires bio-composting digester units.",
        "category": "Environment",
        "subCategory": "Waste Management",
        "location": "Pandra Market Yard, Ranchi",
        "district": "Ranchi",
        "state": "Jharkhand",
        "latitude": 23.385,
        "longitude": 85.289,
        "current_latitude": 23.381,
        "current_longitude": 85.292,
        "distance_km": 0.5,
        "mismatch_distance_km": 0.5,
        "location_status": "verified",
        "suspicion_score": 0.06,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 2,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1004",
        "title": "Groundwater Depletion & Sub-Surface Aquifer Recharging in Hatia Basin",
        "description": "Hatia dam catchment has experienced drastic water table drops affecting 45,000 residents during summer months. Need IoT sensor recharge borewells.",
        "category": "Water",
        "subCategory": "Water Recharge",
        "location": "Hatia, Ranchi",
        "district": "Ranchi",
        "state": "Jharkhand",
        "latitude": 23.295,
        "longitude": 85.312,
        "current_latitude": 23.31,
        "current_longitude": 85.305,
        "distance_km": 1.8,
        "mismatch_distance_km": 1.8,
        "location_status": "low_concern",
        "suspicion_score": 0.18,
        "verification_status": "Needs Verification",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 5,
        "priority": "High",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1005",
        "title": "Solar Cold Storage & Polyhouse Micro-Drip for Peri-Urban Farmers",
        "description": "Peri-urban smallholders in Ormanjhi need micro-climate polyhouses and off-grid solar cold storage to prevent tomato and vegetable spoilage.",
        "category": "Agriculture",
        "subCategory": "Cold Storage",
        "location": "Ormanjhi, Ranchi",
        "district": "Ranchi",
        "state": "Jharkhand",
        "latitude": 23.483,
        "longitude": 85.478,
        "current_latitude": 22.801,
        "current_longitude": 86.202,
        "distance_km": 108.4,
        "mismatch_distance_km": 108.4,
        "location_status": "Location Mismatch",
        "suspicion_score": 0.88,
        "verification_status": "Needs Verification",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 1,
        "priority": "High",
        "status": "Needs Verification",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1006",
        "title": "Drinking Water Fluoride Contamination & Scarcity in Bishunpur",
        "description": "Villagers in Bishunpur block, Gumla district face severe drinking water shortages. High fluoride and iron levels require community-scale filtration.",
        "category": "Water",
        "subCategory": "Drinking Water",
        "location": "Bishunpur Block, Gumla",
        "district": "Gumla",
        "state": "Jharkhand",
        "latitude": 23.376,
        "longitude": 84.372,
        "current_latitude": 23.374,
        "current_longitude": 84.37,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 8,
        "priority": "High",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1007",
        "title": "Acute Drinking Water Scarcity in Ghaghra Panchayat",
        "description": "Ghaghra panchayat villagers have contaminated tube wells with brown silt and fluoride. Seeking filtration kiosks and solar pump installation.",
        "category": "Water",
        "subCategory": "Drinking Water",
        "location": "Ghaghra Block, Gumla",
        "district": "Gumla",
        "state": "Jharkhand",
        "latitude": 23.398,
        "longitude": 84.412,
        "current_latitude": 23.395,
        "current_longitude": 84.41,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Needs Verification",
        "is_duplicate": true,
        "duplicate_score": 0.84,
        "duplicate_of_id": "SCP-1006",
        "duplicate_status": "Reported Anyway",
        "support_count": 2,
        "priority": "Medium",
        "status": "Needs Verification",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1008",
        "title": "Finger Millet (Ragi) Processing & Packaging Unit for Tribal SHGs",
        "description": "Gumla is a leading producer of nutritious ragi millets, but lack of de-hulling and packaging machinery reduces farmer income by 50%.",
        "category": "Agriculture",
        "subCategory": "Agri-Processing",
        "location": "Raidih Block, Gumla",
        "district": "Gumla",
        "state": "Jharkhand",
        "latitude": 23.045,
        "longitude": 84.412,
        "current_latitude": 23.048,
        "current_longitude": 84.41,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 6,
        "priority": "Medium",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1009",
        "title": "Child Malnutrition Screening & Poshan Telemedicine Kits",
        "description": "Anganwadi centers in remote forested pockets of Gumla require digital MUAC biometric bands and telehealth link to pediatrician.",
        "category": "Healthcare",
        "subCategory": "Maternal & Child Health",
        "location": "Chainpur, Gumla",
        "district": "Gumla",
        "state": "Jharkhand",
        "latitude": 23.112,
        "longitude": 84.234,
        "current_latitude": 23.11,
        "current_longitude": 84.236,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 3,
        "priority": "High",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1010",
        "title": "Solar Powered Bilingual E-Classrooms in Forest Schools",
        "description": "Off-grid tribal primary schools in Gumla require rugged solar tablets with Kurukh and Hindi foundational literacy modules.",
        "category": "Education",
        "subCategory": "Digital Classrooms",
        "location": "Palkot Block, Gumla",
        "district": "Gumla",
        "state": "Jharkhand",
        "latitude": 22.88,
        "longitude": 84.645,
        "current_latitude": 22.882,
        "current_longitude": 84.64,
        "distance_km": 0.6,
        "mismatch_distance_km": 0.6,
        "location_status": "verified",
        "suspicion_score": 0.06,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 2,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1011",
        "title": "Industrial Steel Slag Valorization & Eco-Brick Manufacturing",
        "description": "Heavy metallurgical slag dumping causes environmental dusting and land loss in Dhanbad coal belt. Need geopolymer compression recipes.",
        "category": "Environment",
        "subCategory": "Slag Recycling",
        "location": "Jharia & Katras, Dhanbad",
        "district": "Dhanbad",
        "state": "Jharkhand",
        "latitude": 23.742,
        "longitude": 86.415,
        "current_latitude": 23.74,
        "current_longitude": 86.412,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 7,
        "priority": "Medium",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1012",
        "title": "Continuous Drone Telemetry for Coal Mine Dust & Particulate Emissions",
        "description": "Open-cast mines generate heavy PM2.5 and PM10 plumes. IoT telemetry and mist dispersal drones needed to monitor buffer zones.",
        "category": "Environment",
        "subCategory": "Air Quality",
        "location": "Katras Area, Dhanbad",
        "district": "Dhanbad",
        "state": "Jharkhand",
        "latitude": 23.812,
        "longitude": 86.295,
        "current_latitude": 23.36,
        "current_longitude": 85.33,
        "distance_km": 142.6,
        "mismatch_distance_km": 142.6,
        "location_status": "Location Mismatch",
        "suspicion_score": 0.92,
        "verification_status": "Needs Verification",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 1,
        "priority": "High",
        "status": "Needs Verification",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1013",
        "title": "Occupational Respiratory Health Surveillance & Mobile Spirometry Kiosk",
        "description": "Coal mining and transport workers require regular pneumoconiosis and silicosis pulmonary function screening with AI chest X-ray evaluation.",
        "category": "Healthcare",
        "subCategory": "Occupational Health",
        "location": "Sindri Road, Dhanbad",
        "district": "Dhanbad",
        "state": "Jharkhand",
        "latitude": 23.655,
        "longitude": 86.502,
        "current_latitude": 23.652,
        "current_longitude": 86.505,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 5,
        "priority": "High",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1014",
        "title": "Coal Mine Pit Water Neutralization for Agricultural Irrigation",
        "description": "Abandoned opencast quarry pits contain millions of gallons of acidic water. Low-cost lime dosing and bio-filtration can irrigate 400 hectares.",
        "category": "Water",
        "subCategory": "Mine Water Treatment",
        "location": "Nirsa Block, Dhanbad",
        "district": "Dhanbad",
        "state": "Jharkhand",
        "latitude": 23.785,
        "longitude": 86.72,
        "current_latitude": 23.782,
        "current_longitude": 86.722,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 3,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1015",
        "title": "Vocational Mining Safety & Heavy Equipment VR Simulation Lab",
        "description": "Youth in Dhanbad need immersive virtual reality simulators to learn heavy earth-moving machinery operation and underground safety protocols.",
        "category": "Education",
        "subCategory": "Vocational Training",
        "location": "Govindpur, Dhanbad",
        "district": "Dhanbad",
        "state": "Jharkhand",
        "latitude": 23.835,
        "longitude": 86.52,
        "current_latitude": 23.832,
        "current_longitude": 86.524,
        "distance_km": 0.5,
        "mismatch_distance_km": 0.5,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 2,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1016",
        "title": "Smart Micro-Drip Irrigation & Soil Moisture Telemetry in Undulating Red Soil",
        "description": "Farmers in Deoghar plateau region experience falling groundwater tables and crop losses. Need affordable IoT soil sensors and smart drip kits.",
        "category": "Agriculture",
        "subCategory": "Drip Irrigation",
        "location": "Mohanpur Block, Deoghar",
        "district": "Deoghar",
        "state": "Jharkhand",
        "latitude": 24.482,
        "longitude": 86.702,
        "current_latitude": 24.48,
        "current_longitude": 86.7,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 9,
        "priority": "High",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1017",
        "title": "IoT Soil Health Sensor Nodes for Plateau Farmlands",
        "description": "Precision farming IoT sensor deployment for monitoring NPK, pH, and soil moisture across undulating tribal farmlands.",
        "category": "Agriculture",
        "subCategory": "Precision Farming",
        "location": "Devipur Block, Deoghar",
        "district": "Deoghar",
        "state": "Jharkhand",
        "latitude": 24.44,
        "longitude": 86.62,
        "current_latitude": 24.442,
        "current_longitude": 86.618,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Needs Verification",
        "is_duplicate": true,
        "duplicate_score": 0.81,
        "duplicate_of_id": "SCP-1016",
        "duplicate_status": "Reported Anyway",
        "support_count": 2,
        "priority": "Medium",
        "status": "Needs Verification",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1018",
        "title": "Rainwater Harvesting & Talab Renovation for Drought Mitigation",
        "description": "Seasonal drought in Sarath block leaves smallholders without irrigation. Community pond desilting and geotextile lining needed.",
        "category": "Water",
        "subCategory": "Rainwater Harvesting",
        "location": "Sarath Block, Deoghar",
        "district": "Deoghar",
        "state": "Jharkhand",
        "latitude": 24.235,
        "longitude": 86.85,
        "current_latitude": 24.238,
        "current_longitude": 86.848,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 4,
        "priority": "High",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1019",
        "title": "Pilgrimage Corridor Emergency First-Aid & Telemedicine Support",
        "description": "During Shravani Mela, millions of pilgrims travel on foot through Deoghar. Portable emergency vital-sign telemedicine kits needed.",
        "category": "Healthcare",
        "subCategory": "Emergency Health",
        "location": "Baidyanath Dham, Deoghar",
        "district": "Deoghar",
        "state": "Jharkhand",
        "latitude": 24.492,
        "longitude": 86.7,
        "current_latitude": 24.49,
        "current_longitude": 86.702,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 4,
        "priority": "High",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1020",
        "title": "Slag Waste Geopolymerization & Dust Emission Control",
        "description": "Industrial buffer zones in Bokaro require slag dust suppression and geopolymer road paving blocks for rural roads.",
        "category": "Environment",
        "subCategory": "Industrial Ecology",
        "location": "Chas, Bokaro",
        "district": "Bokaro",
        "state": "Jharkhand",
        "latitude": 23.635,
        "longitude": 86.18,
        "current_latitude": 23.632,
        "current_longitude": 86.182,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 3,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1021",
        "title": "Community Water Filtration Kiosks for Chas Outskirts",
        "description": "Heavy industrial discharge near Chas has affected shallow tube-wells with turbidity and iron. Multi-stage filtration units needed.",
        "category": "Water",
        "subCategory": "Water Purification",
        "location": "Chas Sub-division, Bokaro",
        "district": "Bokaro",
        "state": "Jharkhand",
        "latitude": 23.64,
        "longitude": 86.175,
        "current_latitude": 23.638,
        "current_longitude": 86.178,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.05,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 3,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1022",
        "title": "Robotics & Advanced Welding Training for Industrial Youth",
        "description": "Local youth around Bokaro steel industrial cluster need certified automation and robotic welding skill centers.",
        "category": "Education",
        "subCategory": "Vocational Training",
        "location": "Sector 4, Bokaro Steel City",
        "district": "Bokaro",
        "state": "Jharkhand",
        "latitude": 23.665,
        "longitude": 86.15,
        "current_latitude": 23.662,
        "current_longitude": 86.152,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 2,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1023",
        "title": "Bilingual STEM Curriculum Tablets in Santhali & Hindi",
        "description": "Secondary schools in Shikaripara suffer from severe shortage of science educators. Offline bilingual digital learning tablets required.",
        "category": "Education",
        "subCategory": "Digital Learning",
        "location": "Shikaripara, Dumka",
        "district": "Dumka",
        "state": "Jharkhand",
        "latitude": 24.26,
        "longitude": 87.52,
        "current_latitude": 24.258,
        "current_longitude": 87.522,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 5,
        "priority": "High",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1024",
        "title": "Check Dam & Water Table Recharging for Tribal Farmers",
        "description": "Undulating hilly streams in Dumka dry up within 2 months of monsoon. Sand-filled geo-bag check dams can conserve water.",
        "category": "Water",
        "subCategory": "Water Harvesting",
        "location": "Jama Block, Dumka",
        "district": "Dumka",
        "state": "Jharkhand",
        "latitude": 24.35,
        "longitude": 87.31,
        "current_latitude": 24.348,
        "current_longitude": 87.312,
        "distance_km": 0.3,
        "mismatch_distance_km": 0.3,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 4,
        "priority": "Medium",
        "status": "Pending",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1025",
        "title": "Decentralized Solar-Biomass Hybrid Microgrid for Forest Tribal Villages",
        "description": "Villages deep inside Betla National Park corridor in Latehar cannot be connected to high-tension power grid. Need 25kW hybrid microgrid.",
        "category": "Environment",
        "subCategory": "Clean Energy",
        "location": "Mahuadanr, Latehar",
        "district": "Latehar",
        "state": "Jharkhand",
        "latitude": 23.745,
        "longitude": 84.498,
        "current_latitude": 23.36,
        "current_longitude": 85.33,
        "distance_km": 94.2,
        "mismatch_distance_km": 94.2,
        "location_status": "Location Mismatch",
        "suspicion_score": 0.79,
        "verification_status": "Needs Verification",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 4,
        "priority": "High",
        "status": "Needs Verification",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    },
    {
        "id": "SCP-1026",
        "title": "Mobile Sickle-Cell & Malaria Diagnostic Kits for Dense Forest Hamlets",
        "description": "Remote tribal forest villages in Goilkera are 35km away from healthcare centers. Portable blood testing kits and satellite link needed.",
        "category": "Healthcare",
        "subCategory": "Diagnostics",
        "location": "Goilkera, West Singhbhum",
        "district": "West Singhbhum",
        "state": "Jharkhand",
        "latitude": 22.512,
        "longitude": 85.385,
        "current_latitude": 22.51,
        "current_longitude": 85.388,
        "distance_km": 0.4,
        "mismatch_distance_km": 0.4,
        "location_status": "verified",
        "suspicion_score": 0.04,
        "verification_status": "Verified",
        "is_duplicate": false,
        "duplicate_score": 0.0,
        "duplicate_of_id": "",
        "duplicate_status": "Original",
        "support_count": 6,
        "priority": "High",
        "status": "In Progress",
        "requiredSkills": [
            "IoT",
            "Data Analytics"
        ],
        "requiredAcademicDomains": [
            "Engineering",
            "Environmental Sciences"
        ],
        "requiredTechnology": [
            "Sensors",
            "Telemetry"
        ],
        "requiredResources": [
            "Field Lab",
            "Testing Equipment"
        ],
        "estimatedImpact": "Estimated ~10,000 local beneficiaries",
        "submittedBy": "Local Community Council",
        "submittedAt": "2026-09-14 10:00 AM"
    }
];

const INITIAL_COLLABORATIONS = [
    {
        id: "COL-2026-001",
        problemId: "SCP-1001",
        partnerType: "University",
        partnerId: "bit-mesra",
        partnerName: "Birla Institute of Technology (BIT), Mesra",
        projectTitle: "Solar IoT Water Quality Telemetry Network",
        scopeSummary: "Deployment of multi-parameter water sensor buoys and real-time dashboard monitoring in Bishunpur.",
        status: "In Collaboration",
        progressPercentage: 55,
        timeline: "3 - 6 Months",
        contactEmail: "iot.lab@bitmesra.ac.in",
        createdAt: "2026-09-12"
    },
    {
        id: "COL-2026-002",
        problemId: "SCP-1001",
        partnerType: "Industry",
        partnerId: "water-management",
        partnerName: "Water Management & Sanitation Solutions",
        projectTitle: "Jal Jeevan Bishunpur Community RO Filtration Kiosks",
        scopeSummary: "CSR grant funding (INR 18 Lakhs) and turnkey installation of 2 solar-powered filtration stations.",
        status: "Prototype",
        progressPercentage: 40,
        timeline: "1 - 3 Months",
        contactEmail: "csr@watermanagement.org",
        createdAt: "2026-09-12"
    },
    {
        id: "COL-2026-003",
        problemId: "SCP-1002",
        partnerType: "University",
        partnerId: "bau",
        partnerName: "Birsa Agricultural University (BAU)",
        projectTitle: "Deoghar Plateau Climate-Smart Micro-Irrigation Field Trials",
        scopeSummary: "Agronomy team designing low-pressure drip irrigation layout with soil fertility restoration.",
        status: "Accepted",
        progressPercentage: 35,
        timeline: "3 - 6 Months",
        contactEmail: "rabi.director@bau.ac.in",
        createdAt: "2026-09-13"
    },
    {
        id: "COL-2026-004",
        problemId: "SCP-1005",
        partnerType: "University",
        partnerId: "iit-ism",
        partnerName: "IIT (Indian School of Mines), Dhanbad",
        projectTitle: "Slag Geopolymer Eco-Brick Technology Transfer",
        scopeSummary: "Centre for Mining Environment testing compressive strength and non-leaching properties of slag bricks.",
        status: "Testing",
        progressPercentage: 80,
        timeline: "6 - 12 Months",
        contactEmail: "texmin@iitism.ac.in",
        createdAt: "2026-09-14"
    }
];

const INITIAL_NOTIFICATIONS = [
    {
        id: 1,
        recipientType: "Admin",
        problemId: "SCP-1001",
        title: "Top AI Matches Identified",
        message: "BIT Mesra (94%) and Water Management & Sanitation (91%) recommended for Drinking Water Shortage in Gumla.",
        isRead: false,
        timeAgo: "10 mins ago"
    },
    {
        id: 2,
        recipientType: "University",
        problemId: "SCP-1001",
        title: "Societal Match Recommendation",
        message: "BIT Mesra faculty has been recommended to partner on Bishunpur Drinking Water filtration project.",
        isRead: false,
        timeAgo: "2 hours ago"
    },
    {
        id: 3,
        recipientType: "Industry",
        problemId: "SCP-1002",
        title: "AgriTech CSR Opportunity",
        message: "New problem submitted in Deoghar: Smart Irrigation Requirement. High technology match for AgriTech partners.",
        isRead: true,
        timeAgo: "1 day ago"
    }
];


/* --------------------------------------------------------------------------
   5. STORAGE PERSISTENCE HELPERS
   -------------------------------------------------------------------------- */

const STORAGE_KEYS = {
    PROBLEMS: "samadhan_problems_store",
    COLLABORATIONS: "samadhan_collaborations_store",
    NOTIFICATIONS: "samadhan_notifications_store",
    MATCHES_CACHE: "samadhan_matches_cache"
};

function getStoredProblems() {
    try {
        const data = localStorage.getItem(STORAGE_KEYS.PROBLEMS);
        if (data) {
            const parsed = JSON.parse(data);
            if (Array.isArray(parsed) && parsed.length >= SAMPLE_PROBLEMS.length) {
                return parsed.map(p => ({
                    ...p,
                    district: p.district || "Ranchi",
                    verification_status: p.verification_status || "Verified",
                    location_status: p.location_status || "verified",
                    suspicion_score: p.suspicion_score !== undefined ? p.suspicion_score : 5,
                    is_duplicate: p.is_duplicate || false,
                    duplicate_score: p.duplicate_score || 0,
                    support_count: p.support_count || 1
                }));
            }
        }
    } catch (e) {}
    localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(SAMPLE_PROBLEMS));
    return SAMPLE_PROBLEMS;
}

function saveSubmittedProblem(title, description, analysis) {
    const list = getStoredProblems();
    const newId = `SCP-${1001 + list.length}`;
    const newProb = {
        id: newId,
        title: title,
        description: description,
        category: analysis.category,
        subCategory: analysis.subCategory,
        location: analysis.location,
        district: analysis.district,
        state: analysis.state || "Jharkhand",
        latitude: analysis.latitude || null,
        longitude: analysis.longitude || null,
        current_latitude: analysis.current_latitude || null,
        current_longitude: analysis.current_longitude || null,
        location_status: analysis.location_status || "GPS Unavailable",
        mismatch_distance_km: analysis.mismatch_distance_km !== undefined ? analysis.mismatch_distance_km : null,
        suspicion_score: analysis.suspicion_score || 0,
        is_duplicate: analysis.is_duplicate || false,
        duplicate_score: analysis.duplicate_score || 0,
        duplicate_of_id: analysis.duplicate_of_id || null,
        duplicate_action: analysis.duplicate_action || "None",
        support_count: analysis.support_count || 1,
        priority: analysis.priority,
        status: (analysis.location_status === "Location Mismatch" || analysis.is_duplicate) ? "Needs Verification" : "Pending",
        requiredSkills: analysis.requiredSkills,
        requiredAcademicDomains: analysis.requiredAcademicDomains,
        requiredTechnology: analysis.requiredTechnology,
        requiredResources: analysis.requiredResources,
        estimatedImpact: analysis.estimatedImpact,
        submittedBy: "Citizen Portal User",
        submittedAt: "Just now"
    };

    list.unshift(newProb);
    try {
        localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(list));
    } catch (e) {}

    // Add alert notification tailored for integrity status
    let notifMessage = `Automatic AI analysis completed for '${title}'. Recommended universities & industries are ready for review.`;
    if (newProb.location_status === "Location Mismatch") {
        notifMessage = `[Location Mismatch Shield] Problem #${newId} reported ${newProb.mismatch_distance_km ? newProb.mismatch_distance_km.toFixed(1) + 'km' : 'distant'} from citizen GPS. Flagged for manual verification.`;
    } else if (newProb.is_duplicate) {
        notifMessage = `[Duplicate Report Radar] Problem #${newId} has ${Math.round(newProb.duplicate_score * 100)}% overlap with #${newProb.duplicate_of_id}. Marked as '${newProb.duplicate_action}'.`;
    }

    addNotification(
        "Admin",
        newId,
        `New Problem Submitted: #${newId}`,
        notifMessage
    );

    // Update Problem cards in Problems page if present
    renderProblemsList();

    if (typeof updateIntegrityDashboardStats === "function") {
        updateIntegrityDashboardStats();
    }
    if (typeof updateDomainStatistics === "function") {
        updateDomainStatistics();
    }

    return newProb;
}

function getStoredCollaborations() {
    try {
        const data = localStorage.getItem(STORAGE_KEYS.COLLABORATIONS);
        if (data) {
            const parsed = JSON.parse(data);
            if (Array.isArray(parsed) && parsed.length > 0) return parsed;
        }
    } catch (e) {}
    localStorage.setItem(STORAGE_KEYS.COLLABORATIONS, JSON.stringify(INITIAL_COLLABORATIONS));
    return INITIAL_COLLABORATIONS;
}

function saveCollaboration(collab) {
    const list = getStoredCollaborations();
    list.unshift(collab);
    try {
        localStorage.setItem(STORAGE_KEYS.COLLABORATIONS, JSON.stringify(list));
    } catch (e) {}
}

function getStoredNotifications() {
    try {
        const data = localStorage.getItem(STORAGE_KEYS.NOTIFICATIONS);
        if (data) {
            const parsed = JSON.parse(data);
            if (Array.isArray(parsed)) return parsed;
        }
    } catch (e) {}
    localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(INITIAL_NOTIFICATIONS));
    return INITIAL_NOTIFICATIONS;
}

function addNotification(recipientType, problemId, title, message) {
    const notifs = getStoredNotifications();
    const newNotif = {
        id: Date.now(),
        recipientType: recipientType || "Admin",
        problemId: problemId || "",
        title: title,
        message: message,
        isRead: false,
        timeAgo: "Just now"
    };
    notifs.unshift(newNotif);
    try {
        localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(notifs));
    } catch (e) {}
    updateNotificationBadge();
    if (typeof renderNotificationsPage === "function") {
        renderNotificationsPage();
    }
}

function updateNotificationBadge() {
    const notifs = getStoredNotifications();
    const unreadCount = notifs.filter(n => !n.isRead).length;
    const badges = document.querySelectorAll(".notification-count");
    badges.forEach(b => {
        b.textContent = unreadCount;
        b.style.display = unreadCount > 0 ? "inline-flex" : "none";
    });
    const unreadPill = document.getElementById("notifDropdownUnreadPill");
    if (unreadPill) {
        unreadPill.textContent = unreadCount > 0 ? `${unreadCount} New` : `All Caught Up`;
    }
}


/* --------------------------------------------------------------------------
   6. AI PROBLEM ANALYZER & METADATA EXTRACTION
   -------------------------------------------------------------------------- */

function analyzeProblem(title, description, categoryHint = "", district = "Ranchi", area = "") {
    const fullText = `${title} ${description}`.toLowerCase();

    // 1. Category Detection
    let category = categoryHint;
    if (!category || !MATCHING_TAXONOMY[category]) {
        let bestScore = 0;
        let detected = "Water";
        for (const [catName, meta] of Object.entries(MATCHING_TAXONOMY)) {
            let score = 0;
            if (fullText.includes(catName.toLowerCase())) score += 4;
            meta.skills.forEach(s => { if (fullText.includes(s.toLowerCase())) score += 2; });
            meta.domains.forEach(d => { if (fullText.includes(d.toLowerCase())) score += 2; });
            meta.subcategories.forEach(sub => { if (fullText.includes(sub.toLowerCase())) score += 3; });
            if (score > bestScore) {
                bestScore = score;
                detected = catName;
            }
        }
        category = detected;
    }

    const catMeta = MATCHING_TAXONOMY[category] || MATCHING_TAXONOMY["Water"];

    // 2. Sub-Category
    let subCategory = catMeta.subcategories[0];
    for (const sub of catMeta.subcategories) {
        if (fullText.includes(sub.toLowerCase())) {
            subCategory = sub;
            break;
        }
    }

    // 3. Required Skills Extraction
    const matchedSkills = [];
    catMeta.skills.forEach(s => {
        if (fullText.includes(s.toLowerCase()) || matchedSkills.length < 3) {
            matchedSkills.push(s);
        }
    });
    const requiredSkills = [...new Set(matchedSkills)].slice(0, 4);

    // 4. Required Academic Domains
    const matchedDomains = [];
    catMeta.domains.forEach(d => {
        if (fullText.includes(d.toLowerCase()) || matchedDomains.length < 3) {
            matchedDomains.push(d);
        }
    });
    const requiredAcademicDomains = [...new Set(matchedDomains)].slice(0, 3);

    // 5. Required Technology & Resources
    const requiredTechnology = catMeta.technology.slice(0, 3);
    const requiredResources = catMeta.resources.slice(0, 3);

    // 6. Priority / Severity calculation
    const highKeywords = ["emergency", "death", "danger", "critical", "severe", "no water", "contamination", "poison", "flood", "outbreak", "acute"];
    const mediumKeywords = ["problem", "shortage", "lack", "difficulty", "issue", "poor", "needed"];
    let priority = "Low";
    if (highKeywords.some(w => fullText.includes(w))) {
        priority = "High";
    } else if (mediumKeywords.some(w => fullText.includes(w))) {
        priority = "Medium";
    }

    // 7. Community impact
    const locStr = area ? `${area}, ${district}` : `${district}, Jharkhand`;
    const estimatedImpact = `Estimated ~5,000 to 20,000 community members in ${district}`;

    return {
        title,
        description,
        category,
        subCategory,
        location: locStr,
        district: district || "Ranchi",
        priority,
        requiredSkills,
        requiredAcademicDomains,
        requiredTechnology,
        requiredResources,
        estimatedImpact
    };
}


/* --------------------------------------------------------------------------
   7. UNIVERSITY MATCHING ENGINE (EXACT WEIGHTS)
   -------------------------------------------------------------------------- */

function calculateUniversityMatch(problem, university) {
    const probTokens = tokenizeText(`${problem.title} ${problem.description} ${(problem.requiredSkills || []).join(' ')}`);
    const probVec = computeTermFreq(probTokens);

    // 1. Domain Match = 30%
    const uniDomains = university.academicDomains || university.researchStreams || [];
    const reqDomains = problem.requiredAcademicDomains || [];
    let domainSim = calculateJaccardIndex(reqDomains, uniDomains);
    const deptTokens = tokenizeText((university.departments || []).join(' ') + ' ' + uniDomains.join(' '));
    const deptVec = computeTermFreq(deptTokens);
    domainSim = Math.max(domainSim, calculateCosineSimilarity(probVec, deptVec));
    if (reqDomains.some(rd => uniDomains.some(ud => ud.toLowerCase().includes(rd.toLowerCase()) || rd.toLowerCase().includes(ud.toLowerCase())))) {
        domainSim = Math.max(domainSim, 0.88);
    }
    const domainScore = Math.min(1.0, domainSim) * 30.0;

    // 2. Skill Match = 25%
    const uniSkills = university.studentSkills || university.facultyExpertise || [];
    const reqSkills = problem.requiredSkills || [];
    let skillSim = calculateJaccardIndex(reqSkills, uniSkills);
    const skillVec = computeTermFreq(tokenizeText(uniSkills.join(' ')));
    skillSim = Math.max(skillSim, calculateCosineSimilarity(probVec, skillVec));
    if (reqSkills.some(rs => uniSkills.some(us => us.toLowerCase().includes(rs.toLowerCase())))) {
        skillSim = Math.max(skillSim, 0.82);
    }
    const skillScore = Math.min(1.0, skillSim) * 25.0;

    // 3. Research Expertise = 20%
    const uniResearch = university.researchAreas || university.researchStreams || [];
    const resVec = computeTermFreq(tokenizeText(uniResearch.join(' ') + ' ' + (university.description || '')));
    let resSim = calculateCosineSimilarity(probVec, resVec);
    if (reqDomains.some(rd => uniResearch.some(ur => ur.toLowerCase().includes(rd.toLowerCase())))) {
        resSim = Math.max(resSim, 0.78);
    }
    const researchScore = Math.min(1.0, Math.max(0.3, resSim)) * 20.0;

    // 4. Location/Regional Relevance = 10%
    const probDist = (problem.district || "").toLowerCase();
    const uniLoc = (university.location || "").toLowerCase();
    let locationScore = 5.0;
    if (probDist && uniLoc.includes(probDist)) {
        locationScore = 10.0;
    } else if (uniLoc.includes("ranchi")) {
        locationScore = 7.5; // State capital outreach
    }

    // 5. Facilities & Labs = 10%
    const facTokens = tokenizeText((university.facilities || []).join(' '));
    let facSim = calculateCosineSimilarity(probVec, computeTermFreq(facTokens));
    if (probTokens.some(t => (university.facilities || []).some(f => f.toLowerCase().includes(t)))) {
        facSim = Math.max(facSim, 0.75);
    }
    const facilityScore = Math.min(1.0, Math.max(0.4, facSim)) * 10.0;

    // 6. Previous Projects = 5%
    const projTokens = tokenizeText((university.previousProjects || []).join(' '));
    let projSim = calculateCosineSimilarity(probVec, computeTermFreq(projTokens));
    if (probTokens.some(t => (university.previousProjects || []).some(p => p.toLowerCase().includes(t)))) {
        projSim = Math.max(projSim, 0.75);
    }
    const projectScore = Math.min(1.0, Math.max(0.3, projSim)) * 5.0;

    let totalScore = Math.round((domainScore + skillScore + researchScore + locationScore + facilityScore + projectScore) * 10) / 10;
    totalScore = Math.min(99, Math.max(20, totalScore));

    // Explainable Reasons Generator
    const reasons = [];
    const matchedDomains = uniDomains.filter(ud => reqDomains.some(rd => ud.toLowerCase().includes(rd.toLowerCase()) || rd.toLowerCase().includes(ud.toLowerCase())));
    if (matchedDomains.length > 0) {
        reasons.push(`Domain expertise: ${matchedDomains.slice(0, 2).join(", ")}`);
    } else {
        reasons.push(`Multidisciplinary faculty: ${uniDomains[0] || "Applied Sciences"}`);
    }

    const matchedSkills = uniSkills.filter(us => reqSkills.some(rs => us.toLowerCase().includes(rs.toLowerCase())));
    if (matchedSkills.length > 0) {
        reasons.push(`Required technical skills: ${matchedSkills.slice(0, 2).join(", ")}`);
    } else if (reqSkills.length > 0) {
        reasons.push(`Student cohort available for ${reqSkills[0]} implementation`);
    }

    if (university.facilities && university.facilities.length > 0) {
        reasons.push(`Lab infrastructure: ${university.facilities[0]}`);
    }

    if (probDist && uniLoc.includes(probDist)) {
        reasons.push(`Direct regional presence in ${problem.district}`);
    } else {
        reasons.push(`Statewide operational mandate from ${university.location || 'Jharkhand'}`);
    }

    if (university.previousProjects && university.previousProjects.length > 0) {
        reasons.push(`Previous project: ${university.previousProjects[0]}`);
    }

    return {
        universityId: university.id || university.link,
        name: university.name,
        location: university.location,
        district: university.district || "Ranchi",
        matchScore: totalScore,
        breakdown: {
            domainScore: Math.round(domainScore * 10) / 10,
            skillScore: Math.round(skillScore * 10) / 10,
            researchScore: Math.round(researchScore * 10) / 10,
            locationScore: Math.round(locationScore * 10) / 10,
            facilityScore: Math.round(facilityScore * 10) / 10,
            projectScore: Math.round(projectScore * 10) / 10
        },
        reasons,
        relevantDepartment: (university.departments && university.departments[0]) || "Engineering & Science",
        relevantResearch: (university.researchAreas && university.researchAreas[0]) || "Community Innovation",
        matchedSkills: matchedSkills.length > 0 ? matchedSkills.slice(0, 3) : reqSkills.slice(0, 2),
        facilities: university.facilities || [],
        emoji: university.emoji || "🎓"
    };
}


/* --------------------------------------------------------------------------
   8. INDUSTRY MATCHING ENGINE (EXACT WEIGHTS)
   -------------------------------------------------------------------------- */

function calculateIndustryMatch(problem, industry) {
    const probTokens = tokenizeText(`${problem.title} ${problem.description} ${(problem.requiredTechnology || []).join(' ')}`);
    const probVec = computeTermFreq(probTokens);

    // 1. Technology Match = 30%
    const indTech = industry.technologies || industry.focusAreas || [];
    const reqTech = problem.requiredTechnology || [];
    let techSim = calculateJaccardIndex(reqTech, indTech);
    const techVec = computeTermFreq(tokenizeText(indTech.join(' ')));
    techSim = Math.max(techSim, calculateCosineSimilarity(probVec, techVec));
    if (reqTech.some(rt => indTech.some(it => it.toLowerCase().includes(rt.toLowerCase()) || rt.toLowerCase().includes(it.toLowerCase())))) {
        techSim = Math.max(techSim, 0.88);
    }
    const technologyScore = Math.min(1.0, techSim) * 30.0;

    // 2. Problem Domain Match = 25%
    const sectorStr = `${industry.sector || ''} ${industry.name || ''}`.toLowerCase();
    let domainSim = calculateCosineSimilarity(probVec, computeTermFreq(tokenizeText(sectorStr)));
    const probCat = (problem.category || "").toLowerCase();
    if (probCat && sectorStr.includes(probCat)) {
        domainSim = Math.max(domainSim, 0.90);
    }
    const domainScore = Math.min(1.0, domainSim) * 25.0;

    // 3. CSR / Impact Alignment = 20%
    const csrAreas = industry.csrFocusAreas || industry.focusAreas || [];
    const csrVec = computeTermFreq(tokenizeText(csrAreas.join(' ')));
    let csrSim = calculateCosineSimilarity(probVec, csrVec);
    if (csrAreas.some(ca => ca.toLowerCase().includes(probCat) || probTokens.some(t => ca.toLowerCase().includes(t)))) {
        csrSim = Math.max(csrSim, 0.85);
    }
    const csrScore = Math.min(1.0, Math.max(0.35, csrSim)) * 20.0;

    // 4. Resources / Funding = 10%
    const fundingCap = industry.fundingCapability || "Medium";
    let resourceScore = 7.0;
    if (fundingCap === "High") resourceScore = 10.0;
    else if (fundingCap === "Medium") resourceScore = 8.0;

    // 5. Location = 10%
    const probDist = (problem.district || "").toLowerCase();
    const indLoc = (industry.location || "").toLowerCase();
    let locationScore = 7.0;
    if (probDist && indLoc.includes(probDist)) {
        locationScore = 10.0;
    }

    // 6. Previous Experience = 5%
    const expTokens = tokenizeText((industry.previousCollaborations || []).join(' '));
    let expSim = calculateCosineSimilarity(probVec, computeTermFreq(expTokens));
    if (probTokens.some(t => (industry.previousCollaborations || []).some(c => c.toLowerCase().includes(t)))) {
        expSim = Math.max(expSim, 0.80);
    }
    const experienceScore = Math.min(1.0, Math.max(0.3, expSim)) * 5.0;

    let totalScore = Math.round((technologyScore + domainScore + csrScore + resourceScore + locationScore + experienceScore) * 10) / 10;
    totalScore = Math.min(99, Math.max(20, totalScore));

    // Explainable Reasons Generator
    const reasons = [];
    const matchedTech = indTech.filter(it => reqTech.some(rt => it.toLowerCase().includes(rt.toLowerCase()) || rt.toLowerCase().includes(it.toLowerCase())));
    if (matchedTech.length > 0) {
        reasons.push(`Technology capability: ${matchedTech.slice(0, 2).join(", ")}`);
    } else {
        reasons.push(`Sector domain: ${industry.sector || "Industry Innovation"}`);
    }

    reasons.push(`CSR alignment: ${csrAreas[0] || "Community Impact"}`);
    reasons.push(`Resources & funding: ${fundingCap} funding capability for pilot and manufacturing`);

    if (probDist && indLoc.includes(probDist)) {
        reasons.push(`Local deployment base in ${problem.district}`);
    } else {
        reasons.push(`Statewide deployment network across Jharkhand`);
    }

    if (industry.previousCollaborations && industry.previousCollaborations.length > 0) {
        reasons.push(`Previous project: ${industry.previousCollaborations[0]}`);
    }

    return {
        industryId: industry.id || industry.link,
        name: industry.name,
        sector: industry.sector,
        location: industry.location,
        matchScore: totalScore,
        breakdown: {
            technologyScore: Math.round(technologyScore * 10) / 10,
            domainScore: Math.round(domainScore * 10) / 10,
            csrScore: Math.round(csrScore * 10) / 10,
            resourceScore: Math.round(resourceScore * 10) / 10,
            locationScore: Math.round(locationScore * 10) / 10,
            experienceScore: Math.round(experienceScore * 10) / 10
        },
        reasons,
        techResources: indTech.slice(0, 3),
        csrFocus: csrAreas.slice(0, 2),
        fundingTier: fundingCap,
        icon: industry.icon || "🏢"
    };
}


/* --------------------------------------------------------------------------
   9. SMART MATCHING STATE & UI CONTROLLER
   -------------------------------------------------------------------------- */

let currentActiveProblemId = "SCP-1001";
let activeMatchingTab = "all"; // 'all', 'unis', 'inds', 'collabs'
let matchingFilters = {
    keyword: "",
    category: "",
    district: "",
    minScore: 50,
    sort: "score"
};

// Execute Auto-Matching for a Problem
function runAutoMatchingForProblem(problemId) {
    const problems = getStoredProblems();
    const problem = problems.find(p => p.id === problemId) || problems[0];
    if (!problem) return { universities: [], industries: [] };

    // Calculate university matches
    const uniMatches = universities.map(u => calculateUniversityMatch(problem, u));
    uniMatches.sort((a, b) => b.matchScore - a.matchScore);

    // Calculate industry matches
    const indMatches = industries.map(i => calculateIndustryMatch(problem, i));
    indMatches.sort((a, b) => b.matchScore - a.matchScore);

    // Cache results
    try {
        const cache = JSON.parse(localStorage.getItem(STORAGE_KEYS.MATCHES_CACHE) || "{}");
        cache[problemId] = {
            problemId,
            timestamp: Date.now(),
            universities: uniMatches,
            industries: indMatches
        };
        localStorage.setItem(STORAGE_KEYS.MATCHES_CACHE, JSON.stringify(cache));
    } catch (e) {}

    return { universities: uniMatches, industries: indMatches };
}

function getMatchesForProblem(problemId) {
    try {
        const cache = JSON.parse(localStorage.getItem(STORAGE_KEYS.MATCHES_CACHE) || "{}");
        if (cache[problemId]) {
            return cache[problemId];
        }
    } catch (e) {}
    return runAutoMatchingForProblem(problemId);
}

// Master Render for Smart Matching View
function renderMatchingPage() {
    const problems = getStoredProblems();
    if (!problems || problems.length === 0) return;

    // Ensure active problem exists
    let activeProb = problems.find(p => p.id === currentActiveProblemId);
    if (!activeProb) {
        activeProb = problems[0];
        currentActiveProblemId = activeProb.id;
    }

    // 1. Populate Problem Selector Dropdown
    const selector = document.getElementById("activeProblemSelect");
    if (selector) {
        selector.innerHTML = problems.map(p => `
            <option value="${p.id}" ${p.id === currentActiveProblemId ? 'selected' : ''}>
                #${p.id} - ${escapeHtml(p.title.length > 40 ? p.title.substring(0, 37) + '...' : p.title)} (${p.district})
            </option>
        `).join("");
    }

    // 2. Render Active Problem Analysis Card
    renderProblemAnalysisCard(activeProb);

    // 3. Compute or Fetch Matches
    const matchData = getMatchesForProblem(currentActiveProblemId);
    let uniList = matchData.universities || [];
    let indList = matchData.industries || [];

    // 4. Apply Filters & Sorting
    uniList = filterAndSortMatches(uniList, "uni", activeProb);
    indList = filterAndSortMatches(indList, "ind", activeProb);

    // 5. Render Lists
    renderUniversityMatchesGrid(uniList, activeProb);
    renderIndustryMatchesGrid(indList, activeProb);
    renderCollaborationsTracker();

    // 6. Update Tab Badges & Fallback Banner
    const totalMatches = uniList.length + indList.length;
    const badgeAll = document.getElementById("badgeCountAll");
    const badgeUnis = document.getElementById("badgeCountUnis");
    const badgeInds = document.getElementById("badgeCountInds");
    const badgeCollabs = document.getElementById("badgeCountCollabs");

    if (badgeAll) badgeAll.textContent = totalMatches;
    if (badgeUnis) badgeUnis.textContent = uniList.length;
    if (badgeInds) badgeInds.textContent = indList.length;
    if (badgeCollabs) {
        const collabs = getStoredCollaborations().filter(c => c.problemId === currentActiveProblemId || activeMatchingTab === "collabs");
        badgeCollabs.textContent = collabs.length;
    }

    // Check Fallback Banner
    const banner = document.getElementById("broadenSearchBanner");
    if (banner) {
        if (totalMatches === 0 && activeMatchingTab !== "collabs") {
            banner.style.display = "block";
        } else {
            banner.style.display = "none";
        }
    }

    // 7. Update KPIs
    updateMatchingKPIs();
}

function filterAndSortMatches(list, type, activeProb) {
    const q = matchingFilters.keyword.trim().toLowerCase();
    const cat = matchingFilters.category.trim();
    const dist = matchingFilters.district.trim().toLowerCase();
    const min = Number(matchingFilters.minScore) || 0;

    let filtered = list.filter(item => {
        // Min Score
        if (item.matchScore < min) return false;

        // Category filter
        if (cat && activeProb.category !== cat) return false;

        // District filter
        if (dist) {
            const loc = (item.location || "").toLowerCase();
            const itDist = (item.district || "").toLowerCase();
            if (!loc.includes(dist) && !itDist.includes(dist)) return false;
        }

        // Keyword search
        if (q) {
            const nameMatch = item.name.toLowerCase().includes(q);
            const reasonsMatch = (item.reasons || []).some(r => r.toLowerCase().includes(q));
            const specMatch = type === "uni"
                ? (item.relevantDepartment || "").toLowerCase().includes(q) || (item.matchedSkills || []).some(s => s.toLowerCase().includes(q))
                : (item.sector || "").toLowerCase().includes(q) || (item.techResources || []).some(t => t.toLowerCase().includes(q));
            return nameMatch || reasonsMatch || specMatch;
        }

        return true;
    });

    // Sorting
    if (matchingFilters.sort === "score") {
        filtered.sort((a, b) => b.matchScore - a.matchScore);
    } else if (matchingFilters.sort === "name") {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else if (matchingFilters.sort === "location") {
        const pDist = (activeProb.district || "").toLowerCase();
        filtered.sort((a, b) => {
            const aLocal = (a.location || "").toLowerCase().includes(pDist) ? 1 : 0;
            const bLocal = (b.location || "").toLowerCase().includes(pDist) ? 1 : 0;
            return bLocal - aLocal || b.matchScore - a.matchScore;
        });
    }

    return filtered;
}

// Render Problem Analysis Card
function renderProblemAnalysisCard(prob) {
    const card = document.getElementById("activeProblemCard");
    if (!card) return;

    const priorityClass = (prob.priority || "Medium").toLowerCase();
    const skillsHtml = (prob.requiredSkills || []).map(s => `<span class="meta-tag primary">${escapeHtml(s)}</span>`).join("");
    const domainsHtml = (prob.requiredAcademicDomains || []).map(d => `<span class="meta-tag">${escapeHtml(d)}</span>`).join("");
    const techHtml = (prob.requiredTechnology || []).map(t => `<span class="meta-tag success">${escapeHtml(t)}</span>`).join("");
    const resHtml = (prob.requiredResources || []).map(r => `<span class="meta-tag">${escapeHtml(r)}</span>`).join("");

    card.innerHTML = `
        <div class="analysis-header">
            <div class="analysis-title-group">
                <div class="analysis-badges-row" style="margin-bottom: 8px;">
                    <span class="badge ${priorityClass}">${escapeHtml(prob.priority || 'Medium')} Priority</span>
                    <span class="badge primary">#${escapeHtml(prob.id)}</span>
                    <span class="badge" style="background: rgba(124, 58, 237, 0.1); color: #7c3aed; border: 1px solid rgba(124, 58, 237, 0.2);">
                        <i class="ri-folder-line"></i> ${escapeHtml(prob.category)} • ${escapeHtml(prob.subCategory || 'Community Need')}
                    </span>
                    <span class="badge" style="background: var(--bg-primary); color: var(--text-muted); border: 1px solid var(--border-color);">
                        <i class="ri-map-pin-line"></i> ${escapeHtml(prob.location)}
                    </span>
                </div>
                <h2>${escapeHtml(prob.title)}</h2>
                <p>${escapeHtml(prob.description)}</p>
                <div style="margin-top: 10px; font-size: 0.85rem; color: #059669; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <i class="ri-user-heart-line"></i> Community Impact: ${escapeHtml(prob.estimatedImpact || 'Estimated regional community')}
                </div>
            </div>
        </div>

        <div class="extracted-meta-grid">
            <div class="meta-block">
                <div class="meta-block-title"><i class="ri-cpu-line"></i> Required Technical Skills</div>
                <div class="meta-tag-list">${skillsHtml || '<span class="meta-tag">General Engineering</span>'}</div>
            </div>

            <div class="meta-block">
                <div class="meta-block-title"><i class="ri-school-line"></i> Academic Domains</div>
                <div class="meta-tag-list">${domainsHtml || '<span class="meta-tag">Applied Sciences</span>'}</div>
            </div>

            <div class="meta-block">
                <div class="meta-block-title"><i class="ri-tools-line"></i> Required Technology</div>
                <div class="meta-tag-list">${techHtml || '<span class="meta-tag">Field Hardware</span>'}</div>
            </div>

            <div class="meta-block">
                <div class="meta-block-title"><i class="ri-building-4-line"></i> Infrastructure & Labs</div>
                <div class="meta-tag-list">${resHtml || '<span class="meta-tag">Testing Facility</span>'}</div>
            </div>
        </div>
    `;
}

// Render Universities Grid
function renderUniversityMatchesGrid(matches, activeProb) {
    const grid = document.getElementById("universityMatchesGrid");
    if (!grid) return;

    if (matches.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 30px; text-align: center; color: var(--text-muted);">
                <i class="ri-school-line" style="font-size: 2.5rem; color: var(--border-color); display: block; margin-bottom: 8px;"></i>
                No universities found meeting current filter criteria (${matchingFilters.minScore}%+ match).
            </div>
        `;
        return;
    }

    grid.innerHTML = matches.map((m, idx) => {
        const scoreClass = m.matchScore >= 85 ? "high" : m.matchScore >= 70 ? "good" : "moderate";
        const reasonsHtml = m.reasons.map(r => `
            <div class="match-reason-item">
                <i class="ri-checkbox-circle-fill"></i>
                <span>${escapeHtml(r)}</span>
            </div>
        `).join("");

        const tagsHtml = (m.matchedSkills || []).map(s => `<span class="match-tag-pill"><i class="ri-flashlight-line"></i> ${escapeHtml(s)}</span>`).join("");

        return `
            <div class="match-card" id="match-uni-${escapeQuotes(m.universityId)}">
                <div>
                    <div class="match-card-top">
                        <div class="match-org-identity">
                            <div class="match-org-icon">${m.emoji || '🎓'}</div>
                            <div class="match-org-details">
                                <h3>${escapeHtml(m.name)}</h3>
                                <div class="match-org-location">
                                    <i class="ri-map-pin-line"></i> ${escapeHtml(m.location)}
                                </div>
                            </div>
                        </div>

                        <div class="match-score-badge ${scoreClass}" title="Weighted multi-factor match score">
                            <div class="match-score-num">${m.matchScore}%</div>
                            <div class="match-score-label">Match</div>
                        </div>
                    </div>

                    <div class="score-breakdown-row">
                        <span>Domain Fit: ${m.breakdown.domainScore}/30</span>
                        <div class="score-mini-progress">
                            <div class="score-mini-fill" style="width: ${(m.breakdown.domainScore / 30) * 100}%"></div>
                        </div>
                        <span>Skill: ${m.breakdown.skillScore}/25</span>
                    </div>

                    <div class="match-reasons-box">
                        <div class="match-reasons-title">
                            <i class="ri-sparkling-fill" style="color: #10b981;"></i> Why this HEI matches
                        </div>
                        ${reasonsHtml}
                    </div>

                    <div class="match-tags-row">
                        <span class="match-tag-pill" style="font-weight: 600;"><i class="ri-book-read-line"></i> ${escapeHtml(m.relevantDepartment)}</span>
                        ${tagsHtml}
                    </div>
                </div>

                <div class="match-card-actions">
                    <button class="secondary-btn" onclick="openMatchingUniModal('${escapeQuotes(m.universityId)}')">
                        <i class="ri-information-line"></i> View Details
                    </button>
                    <button class="primary-btn" onclick="openCollaborationModal('University', '${escapeQuotes(m.universityId)}')">
                        <i class="ri-handshake-line"></i> Express Interest
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

// Render Industry Grid
function renderIndustryMatchesGrid(matches, activeProb) {
    const grid = document.getElementById("industryMatchesGrid");
    if (!grid) return;

    if (matches.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 30px; text-align: center; color: var(--text-muted);">
                <i class="ri-building-line" style="font-size: 2.5rem; color: var(--border-color); display: block; margin-bottom: 8px;"></i>
                No industry partners found meeting current filter criteria (${matchingFilters.minScore}%+ match).
            </div>
        `;
        return;
    }

    grid.innerHTML = matches.map((m, idx) => {
        const scoreClass = m.matchScore >= 85 ? "high" : m.matchScore >= 70 ? "good" : "moderate";
        const reasonsHtml = m.reasons.map(r => `
            <div class="match-reason-item">
                <i class="ri-checkbox-circle-fill"></i>
                <span>${escapeHtml(r)}</span>
            </div>
        `).join("");

        const tagsHtml = (m.techResources || []).map(t => `<span class="match-tag-pill"><i class="ri-tools-line"></i> ${escapeHtml(t)}</span>`).join("");

        return `
            <div class="match-card" id="match-ind-${escapeQuotes(m.industryId)}">
                <div>
                    <div class="match-card-top">
                        <div class="match-org-identity">
                            <div class="match-org-icon" style="background: rgba(124, 58, 237, 0.08);">${m.icon || '🏢'}</div>
                            <div class="match-org-details">
                                <h3>${escapeHtml(m.name)}</h3>
                                <div class="match-org-location">
                                    <i class="ri-briefcase-line"></i> ${escapeHtml(m.sector)}
                                </div>
                            </div>
                        </div>

                        <div class="match-score-badge ${scoreClass}" title="Weighted industry alignment score">
                            <div class="match-score-num">${m.matchScore}%</div>
                            <div class="match-score-label">Match</div>
                        </div>
                    </div>

                    <div class="score-breakdown-row">
                        <span>Tech Fit: ${m.breakdown.technologyScore}/30</span>
                        <div class="score-mini-progress">
                            <div class="score-mini-fill" style="width: ${(m.breakdown.technologyScore / 30) * 100}%"></div>
                        </div>
                        <span>CSR: ${m.breakdown.csrScore}/20</span>
                    </div>

                    <div class="match-reasons-box">
                        <div class="match-reasons-title">
                            <i class="ri-sparkling-fill" style="color: #7c3aed;"></i> Why this partner matches
                        </div>
                        ${reasonsHtml}
                    </div>

                    <div class="match-tags-row">
                        <span class="match-tag-pill" style="font-weight: 600; background: rgba(16, 185, 129, 0.08); color: #059669;">
                            <i class="ri-funds-line"></i> ${escapeHtml(m.fundingTier)} Funding Tier
                        </span>
                        ${tagsHtml}
                    </div>
                </div>

                <div class="match-card-actions">
                    <button class="secondary-btn" onclick="openMatchingIndModal('${escapeQuotes(m.industryId)}')">
                        <i class="ri-information-line"></i> View Details
                    </button>
                    <button class="primary-btn" onclick="openCollaborationModal('Industry', '${escapeQuotes(m.industryId)}')">
                        <i class="ri-handshake-line"></i> Express Interest
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

// Render Collaborations Tracker
function renderCollaborationsTracker() {
    const container = document.getElementById("collaborationsList");
    if (!container) return;

    const collabs = getStoredCollaborations();
    if (collabs.length === 0) {
        container.innerHTML = `
            <div style="padding: 40px; text-align: center; color: var(--text-muted); background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px;">
                <i class="ri-handshake-line" style="font-size: 3rem; color: var(--border-color); display: block; margin-bottom: 10px;"></i>
                <h3>No active collaborations initiated yet</h3>
                <p>Click "Express Interest" on any recommended university or industry partner to initiate a solution collaboration.</p>
            </div>
        `;
        return;
    }

    const STAGES = [
        "Recommended", "Interested", "Accepted", "In Collaboration", "Prototype", "Testing", "Deployed", "Completed"
    ];

    container.innerHTML = collabs.map(c => {
        const currentStageIndex = STAGES.indexOf(c.status);
        const activeIdx = currentStageIndex >= 0 ? currentStageIndex : 1;

        const stepperHtml = STAGES.map((s, idx) => {
            let stateClass = "";
            if (idx < activeIdx) stateClass = "completed";
            else if (idx === activeIdx) stateClass = "current";
            return `
                <div class="stepper-step ${stateClass}">
                    ${idx < activeIdx ? '✓' : idx + 1}. ${escapeHtml(s)}
                </div>
            `;
        }).join("");

        const partnerBadgeClass = c.partnerType === "University" ? "university" : "industry";
        const partnerIcon = c.partnerType === "University" ? "ri-school-line" : "ri-building-line";

        return `
            <div class="collab-card" id="collab-card-${escapeQuotes(c.id)}">
                <div class="collab-card-header">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                            <span class="collab-partner-badge ${partnerBadgeClass}">
                                <i class="${partnerIcon}"></i> ${escapeHtml(c.partnerType)} Partner
                            </span>
                            <span class="badge primary">#${escapeHtml(c.problemId)}</span>
                            <span class="badge ${c.progressPercentage >= 80 ? 'green' : 'orange'}">${escapeHtml(c.status)} (${c.progressPercentage}%)</span>
                        </div>
                        <h3 style="font-size: 1.15rem; color: var(--text-primary); margin-bottom: 4px;">${escapeHtml(c.projectTitle)}</h3>
                        <p style="color: var(--text-muted); font-size: 0.88rem;">
                            Partner: <strong>${escapeHtml(c.partnerName)}</strong> • Timeline: ${escapeHtml(c.timeline || '3 - 6 Months')} • Contact: ${escapeHtml(c.contactEmail || 'Nodal Officer')}
                        </p>
                    </div>

                    <div style="display: flex; align-items: center; gap: 8px;">
                        <button class="secondary-btn" onclick="advanceCollaborationStatus('${escapeQuotes(c.id)}')" title="Advance collaboration to next project stage">
                            <i class="ri-arrow-right-line"></i> Advance Stage
                        </button>
                    </div>
                </div>

                <div class="collab-stepper">
                    ${stepperHtml}
                </div>

                <p style="font-size: 0.85rem; color: var(--text-secondary); background: var(--bg-primary); padding: 10px 14px; border-radius: 8px; margin-top: 10px; border: 1px solid var(--border-color);">
                    <strong>Scope & Deliverables:</strong> ${escapeHtml(c.scopeSummary || 'Cooperative research, prototyping, and community validation.')}
                </p>
            </div>
        `;
    }).join("");
}

function updateMatchingKPIs() {
    const problems = getStoredProblems();
    const collabs = getStoredCollaborations();

    const pElem = document.getElementById("kpiProblemsMatched");
    const uElem = document.getElementById("kpiUnisRecommended");
    const iElem = document.getElementById("kpiIndustriesRecommended");
    const cElem = document.getElementById("kpiActiveCollabs");

    if (pElem) pElem.textContent = problems.length;
    if (uElem) uElem.textContent = universities.length;
    if (iElem) iElem.textContent = industries.length;
    if (cElem) cElem.textContent = collabs.length;
}


/* --------------------------------------------------------------------------
   10. TAB & FILTER EVENT HANDLERS
   -------------------------------------------------------------------------- */

function switchMatchingTab(tabName) {
    activeMatchingTab = tabName;

    // Update active tab buttons
    const btnAll = document.getElementById("tabBtnAll");
    const btnUnis = document.getElementById("tabBtnUnis");
    const btnInds = document.getElementById("tabBtnInds");
    const btnCollabs = document.getElementById("tabBtnCollabs");

    if (btnAll) btnAll.classList.toggle("active", tabName === "all");
    if (btnUnis) btnUnis.classList.toggle("active", tabName === "unis");
    if (btnInds) btnInds.classList.toggle("active", tabName === "inds");
    if (btnCollabs) btnCollabs.classList.toggle("active", tabName === "collabs");

    // Toggle content panels
    const viewUnis = document.getElementById("tabContentUnis");
    const viewInds = document.getElementById("tabContentInds");
    const viewCollabs = document.getElementById("tabContentCollabs");

    if (viewUnis) viewUnis.style.display = (tabName === "all" || tabName === "unis") ? "block" : "none";
    if (viewInds) viewInds.style.display = (tabName === "all" || tabName === "inds") ? "block" : "none";
    if (viewCollabs) viewCollabs.style.display = (tabName === "collabs") ? "block" : "none";

    renderMatchingPage();
}

function handleMatchingFilterChange() {
    matchingFilters.keyword = document.getElementById("matchingKeywordSearch")?.value || "";
    matchingFilters.category = document.getElementById("matchingCategoryFilter")?.value || "";
    matchingFilters.district = document.getElementById("matchingDistrictFilter")?.value || "";
    matchingFilters.sort = document.getElementById("matchingSortOrder")?.value || "score";

    renderMatchingPage();
}

function handleMinScoreSlider(val) {
    matchingFilters.minScore = Number(val);
    const badge = document.getElementById("matchingScoreSliderVal");
    if (badge) badge.textContent = `${val}%+`;
    handleMatchingFilterChange();
}

function resetMatchingFilters() {
    matchingFilters = {
        keyword: "",
        category: "",
        district: "",
        minScore: 50,
        sort: "score"
    };

    const sIn = document.getElementById("matchingKeywordSearch");
    const sCat = document.getElementById("matchingCategoryFilter");
    const sDist = document.getElementById("matchingDistrictFilter");
    const sSort = document.getElementById("matchingSortOrder");
    const sSlide = document.getElementById("matchingMinScoreSlider");
    const sBadge = document.getElementById("matchingScoreSliderVal");

    if (sIn) sIn.value = "";
    if (sCat) sCat.value = "";
    if (sDist) sDist.value = "";
    if (sSort) sSort.value = "score";
    if (sSlide) sSlide.value = 50;
    if (sBadge) sBadge.textContent = "50%+";

    renderMatchingPage();
    showToast("Filters reset to default view.");
}

function broadenSearchCriteria() {
    matchingFilters.minScore = 30;
    matchingFilters.category = "";
    matchingFilters.district = "";
    matchingFilters.keyword = "";

    const sIn = document.getElementById("matchingKeywordSearch");
    const sCat = document.getElementById("matchingCategoryFilter");
    const sDist = document.getElementById("matchingDistrictFilter");
    const sSlide = document.getElementById("matchingMinScoreSlider");
    const sBadge = document.getElementById("matchingScoreSliderVal");

    if (sIn) sIn.value = "";
    if (sCat) sCat.value = "";
    if (sDist) sDist.value = "";
    if (sSlide) sSlide.value = 30;
    if (sBadge) sBadge.textContent = "30%+";

    renderMatchingPage();
    showToast("Broadened search: expanded criteria across all Jharkhand institutions & sectors!");
}

function handleProblemSelectionChange(problemId) {
    currentActiveProblemId = problemId;
    renderMatchingPage();
    showToast(`Switched active problem to #${problemId}`);
}

function refreshMatchingForActiveProblem() {
    try {
        const cache = JSON.parse(localStorage.getItem(STORAGE_KEYS.MATCHES_CACHE) || "{}");
        delete cache[currentActiveProblemId];
        localStorage.setItem(STORAGE_KEYS.MATCHES_CACHE, JSON.stringify(cache));
    } catch (e) {}

    runAutoMatchingForProblem(currentActiveProblemId);
    renderMatchingPage();
    showToast("Refreshed AI match scores with latest profile data!");
}

function setActiveProblemAndMatch(problemId) {
    currentActiveProblemId = problemId;
    renderMatchingPage();
}


/* --------------------------------------------------------------------------
   11. MODAL DIALOGS & COLLABORATION WORKFLOW
   -------------------------------------------------------------------------- */

let currentCollabPartner = null;

function openMatchingUniModal(uniId) {
    const uni = universities.find(u => u.id === uniId || u.link === uniId);
    if (!uni) return;

    const problems = getStoredProblems();
    const prob = problems.find(p => p.id === currentActiveProblemId) || problems[0];
    const match = calculateUniversityMatch(prob, uni);

    const mEmoji = document.getElementById("modalMatchUniEmoji");
    const mName = document.getElementById("modalMatchUniName");
    const mLoc = document.getElementById("modalMatchUniLocation");
    const mScore = document.getElementById("modalMatchUniScore");
    const mDesc = document.getElementById("modalMatchUniDesc");
    const mDepts = document.getElementById("modalMatchUniDepartments");
    const mFacs = document.getElementById("modalMatchUniFacilities");
    const mSkills = document.getElementById("modalMatchUniSkills");
    const mProjs = document.getElementById("modalMatchUniProjects");
    const mBtn = document.getElementById("modalMatchUniActionBtn");

    if (mEmoji) mEmoji.textContent = uni.emoji || "🎓";
    if (mName) mName.textContent = uni.name;
    if (mLoc) mLoc.innerHTML = `<i class="ri-map-pin-line"></i> ${escapeHtml(uni.location)}`;
    if (mScore) mScore.textContent = `${match.matchScore}% Match`;
    if (mDesc) mDesc.textContent = uni.description || "";

    if (mDepts) mDepts.innerHTML = (uni.departments || []).map(d => `<span>${escapeHtml(d)}</span>`).join("");
    if (mFacs) mFacs.innerHTML = (uni.facilities || []).map(f => `<span>${escapeHtml(f)}</span>`).join("");
    if (mSkills) mSkills.innerHTML = (uni.studentSkills || []).map(s => `<span>${escapeHtml(s)}</span>`).join("");
    if (mProjs) mProjs.innerHTML = (uni.previousProjects || []).map(p => `<span>${escapeHtml(p)}</span>`).join("");

    if (mBtn) {
        mBtn.onclick = () => {
            closeMatchingModal("matchingUniModal");
            openCollaborationModal("University", uni.id);
        };
    }

    const modal = document.getElementById("matchingUniModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function openMatchingIndModal(indId) {
    const ind = industries.find(i => i.id === indId || i.link === indId);
    if (!ind) return;

    const problems = getStoredProblems();
    const prob = problems.find(p => p.id === currentActiveProblemId) || problems[0];
    const match = calculateIndustryMatch(prob, ind);

    const mIcon = document.getElementById("modalMatchIndIcon");
    const mName = document.getElementById("modalMatchIndName");
    const mSector = document.getElementById("modalMatchIndSector");
    const mScore = document.getElementById("modalMatchIndScore");
    const mBadge = document.getElementById("modalMatchIndFundingBadge");
    const mDesc = document.getElementById("modalMatchIndDesc");
    const mTech = document.getElementById("modalMatchIndTech");
    const mCsr = document.getElementById("modalMatchIndCsr");
    const mCollabs = document.getElementById("modalMatchIndCollabs");
    const mBtn = document.getElementById("modalMatchIndActionBtn");

    if (mIcon) mIcon.textContent = ind.icon || "🏢";
    if (mName) mName.textContent = ind.name;
    if (mSector) mSector.innerHTML = `<i class="ri-briefcase-line"></i> ${escapeHtml(ind.sector)}`;
    if (mScore) mScore.textContent = `${match.matchScore}% Match`;
    if (mBadge) mBadge.textContent = `${ind.fundingCapability || 'Medium'} CSR Funding Tier`;
    if (mDesc) mDesc.textContent = ind.description || "";

    if (mTech) mTech.innerHTML = (ind.technologies || ind.focusAreas || []).map(t => `<span>${escapeHtml(t)}</span>`).join("");
    if (mCsr) mCsr.innerHTML = (ind.csrFocusAreas || []).map(c => `<span>${escapeHtml(c)}</span>`).join("");
    if (mCollabs) mCollabs.innerHTML = (ind.previousCollaborations || []).map(p => `<span>${escapeHtml(p)}</span>`).join("");

    if (mBtn) {
        mBtn.onclick = () => {
            closeMatchingModal("matchingIndModal");
            openCollaborationModal("Industry", ind.id);
        };
    }

    const modal = document.getElementById("matchingIndModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function closeMatchingModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
}

function handleMatchingModalOverlayClick(event, modalId) {
    if (event.target && event.target.id === modalId) {
        closeMatchingModal(modalId);
    }
}

function openCollaborationModal(partnerType, partnerId, mode = "partner") {
    const problems = getStoredProblems();
    const prob = problems.find(p => p.id === currentActiveProblemId) || problems[0];

    let partnerName = "General Partner";
    if (partnerType === "University") {
        const u = universities.find(x => x.id === partnerId || x.link === partnerId);
        if (u) partnerName = u.name;
    } else if (partnerType === "Industry") {
        const i = industries.find(x => x.id === partnerId || x.link === partnerId);
        if (i) partnerName = i.name;
    }

    currentCollabPartner = {
        partnerType: partnerType || "University",
        partnerId: partnerId || "open",
        partnerName: partnerName
    };

    const fProb = document.getElementById("collabFormProblemTitle");
    const fPart = document.getElementById("collabFormPartnerName");
    const fTitle = document.getElementById("collabProjectTitle");
    const fScope = document.getElementById("collabScopeDesc");

    if (fProb) fProb.value = `#${prob.id} - ${prob.title}`;
    if (fPart) fPart.value = partnerName;
    if (fTitle) fTitle.value = `Joint Solution for ${prob.subCategory || prob.category} (#${prob.id})`;
    if (fScope) fScope.value = `Collaborative research, prototype engineering, and localized field demonstration to resolve community challenges in ${prob.district}.`;

    const modal = document.getElementById("collaborationModal");
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function handleCollaborationSubmit(event) {
    if (event) event.preventDefault();

    const problems = getStoredProblems();
    const prob = problems.find(p => p.id === currentActiveProblemId) || problems[0];

    const projectTitle = document.getElementById("collabProjectTitle")?.value.trim() || `Solution for ${prob.title}`;
    const scope = document.getElementById("collabScopeDesc")?.value.trim() || "Collaborative implementation.";
    const timeline = document.getElementById("collabTimeline")?.value || "3 - 6 Months";
    const email = document.getElementById("collabContactEmail")?.value.trim() || "contact@partner.org";

    const newCollab = {
        id: `COL-2026-${String(Date.now()).slice(-3)}`,
        problemId: prob.id,
        partnerType: currentCollabPartner?.partnerType || "University",
        partnerId: currentCollabPartner?.partnerId || "org",
        partnerName: currentCollabPartner?.partnerName || "Partner Organization",
        projectTitle: projectTitle,
        scopeSummary: scope,
        status: "Interested",
        progressPercentage: 20,
        timeline: timeline,
        contactEmail: email,
        createdAt: "Just now"
    };

    saveCollaboration(newCollab);

    // Add alert notification
    addNotification(
        "Admin",
        prob.id,
        `Expression of Interest: ${newCollab.partnerName}`,
        `${newCollab.partnerName} submitted expression of interest for problem #${prob.id} (${prob.title}).`
    );

    closeMatchingModal("collaborationModal");

    // Switch to collaborations tab to show the new project
    switchMatchingTab("collabs");
    showToast(`✓ Collaboration proposal created for ${newCollab.partnerName}!`);
}

function advanceCollaborationStatus(collabId) {
    const STAGES = [
        { status: "Recommended", prog: 10 },
        { status: "Interested", prog: 20 },
        { status: "Accepted", prog: 35 },
        { status: "In Collaboration", prog: 50 },
        { status: "Prototype", prog: 65 },
        { status: "Testing", prog: 80 },
        { status: "Deployed", prog: 95 },
        { status: "Completed", prog: 100 }
    ];

    const collabs = getStoredCollaborations();
    const collab = collabs.find(c => c.id === collabId);
    if (!collab) return;

    const currentIdx = STAGES.findIndex(s => s.status === collab.status);
    const nextIdx = Math.min(STAGES.length - 1, currentIdx + 1);
    const nextStage = STAGES[nextIdx];

    collab.status = nextStage.status;
    collab.progressPercentage = nextStage.prog;

    try {
        localStorage.setItem(STORAGE_KEYS.COLLABORATIONS, JSON.stringify(collabs));
    } catch (e) {}

    addNotification(
        "Admin",
        collab.problemId,
        `Collaboration Stage Advanced`,
        `Project '${collab.projectTitle}' advanced to '${collab.status}' (${collab.progressPercentage}%).`
    );

    renderCollaborationsTracker();
    showToast(`Collaboration advanced to ${collab.status} (${collab.progressPercentage}%)`);
}


/* --------------------------------------------------------------------------
   12. NOTIFICATION CENTER & DROPDOWN SYSTEM (UNIFIED DATA SOURCE & SYNC)
   -------------------------------------------------------------------------- */

function toggleNotificationDropdown(event) {
    if (event) {
        event.stopPropagation();
    }
    const dropdown = document.getElementById("notificationDropdown");
    if (!dropdown) return;
    
    const isOpen = dropdown.classList.contains("active");
    if (isOpen) {
        dropdown.classList.remove("active");
    } else {
        dropdown.classList.add("active");
        renderNotificationDropdown();
    }
}

function closeNotificationDropdown() {
    const dropdown = document.getElementById("notificationDropdown");
    if (dropdown) {
        dropdown.classList.remove("active");
    }
}

function goToNotificationsPage(event) {
    if (event) event.stopPropagation();
    closeNotificationDropdown();
    showPage("notifications", document.getElementById("sidebarNotifLink"));
}

function renderNotificationDropdown() {
    const listContainer = document.getElementById("notifDropdownList");
    const unreadPill = document.getElementById("notifDropdownUnreadPill");
    if (!listContainer) return;

    const notifs = getStoredNotifications();
    const unreadCount = notifs.filter(n => !n.isRead).length;

    if (unreadPill) {
        unreadPill.textContent = unreadCount > 0 ? `${unreadCount} New` : `All Caught Up`;
    }

    if (notifs.length === 0) {
        listContainer.innerHTML = `
            <div class="notif-dropdown-empty">
                <i class="ri-notification-off-line"></i>
                <h4>No notifications</h4>
                <p>You're all caught up on platform updates.</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = notifs.map(n => {
        const iconClass = n.recipientType === 'University' ? 'ri-school-line' : 
                          n.recipientType === 'Industry' ? 'ri-building-line' : 
                          'ri-sparkling-fill';
        return `
            <div class="notif-dropdown-item ${n.isRead ? '' : 'unread'}" onclick="handleNotificationItemClick(${n.id}, '${escapeQuotes(n.problemId || '')}', event)">
                <div class="notif-dropdown-icon ${n.isRead ? '' : 'success'}">
                    <i class="${iconClass}"></i>
                </div>
                <div class="notif-dropdown-content">
                    <h4>${escapeHtml(n.title)}</h4>
                    <p>${escapeHtml(n.message)}</p>
                    <div class="notif-dropdown-meta">
                        <span class="notif-dropdown-time"><i class="ri-time-line"></i> ${escapeHtml(n.timeAgo || 'Recently')}</span>
                        ${n.problemId ? `<button type="button" class="notif-dropdown-action" onclick="openProblemFromNotif('${escapeQuotes(n.problemId)}', ${n.id}, event)">Review Matches →</button>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

function handleNotificationItemClick(id, problemId, event) {
    markNotificationRead(id);
    if (problemId) {
        openProblemMatches(problemId);
        closeNotificationDropdown();
    }
}

function openProblemFromNotif(problemId, notifId, event) {
    if (event) event.stopPropagation();
    if (notifId) markNotificationRead(notifId);
    closeNotificationDropdown();
    openProblemMatches(problemId);
}

function markNotificationRead(id) {
    const notifs = getStoredNotifications();
    const target = notifs.find(n => n.id === id);
    if (target) {
        target.isRead = true;
        try {
            localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(notifs));
        } catch (e) {}
        updateNotificationBadge();
        renderNotificationsPage();
        renderNotificationDropdown();
        
        // Sync with backend if active
        if (typeof MatchingAPI !== "undefined" && MatchingAPI.isBackendLive) {
            fetch(`${MatchingAPI.backendBaseUrl}/api/notifications/${id}/read`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" }
            }).catch(() => {});
        }
    }
}

function renderNotificationsPage() {
    const container = document.getElementById("notificationsContainer");
    if (!container) return;

    const notifs = getStoredNotifications();
    if (notifs.length === 0) {
        container.innerHTML = `
            <div style="padding: 40px; text-align: center; color: var(--text-muted); background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px;">
                <i class="ri-notification-off-line" style="font-size: 3rem; color: var(--border-color); display: block; margin-bottom: 10px;"></i>
                <h3>No notifications</h3>
                <p>You are all caught up on problem matches, system alerts, and collaboration updates.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = notifs.map(n => `
        <div class="notification-item-card ${n.isRead ? '' : 'unread'}" onclick="markNotificationRead(${n.id})">
            <div class="notif-icon-circle ${n.isRead ? '' : 'success'}">
                <i class="${n.recipientType === 'University' ? 'ri-school-line' : n.recipientType === 'Industry' ? 'ri-building-line' : 'ri-sparkling-fill'}"></i>
            </div>
            <div class="notif-body" style="flex: 1;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                    <h4>${escapeHtml(n.title)}</h4>
                    ${!n.isRead ? `<span style="font-size: 0.72rem; background: var(--primary-light); color: var(--primary); border: 1px solid rgba(0,118,168,0.25); padding: 2px 6px; border-radius: 10px; font-weight: 600;">Unread</span>` : ''}
                </div>
                <p>${escapeHtml(n.message)}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="notif-time"><i class="ri-time-line"></i> ${escapeHtml(n.timeAgo || 'Recently')}</span>
                    ${n.problemId ? `<button class="text-btn" onclick="openProblemMatches('${escapeQuotes(n.problemId)}')">Review Matches →</button>` : ''}
                </div>
            </div>
        </div>
    `).join("");

    updateNotificationBadge();
}

function markAllNotificationsRead(event) {
    if (event) event.stopPropagation();
    const notifs = getStoredNotifications();
    notifs.forEach(n => { n.isRead = true; });
    try {
        localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(notifs));
    } catch (e) {}
    updateNotificationBadge();
    renderNotificationsPage();
    renderNotificationDropdown();
    showToast("All notifications marked as read.");

    // Sync with backend if active
    if (typeof MatchingAPI !== "undefined" && MatchingAPI.isBackendLive) {
        fetch(`${MatchingAPI.backendBaseUrl}/api/notifications/read-all`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        }).catch(() => {});
    }
}

function clearAllNotifications(event) {
    if (event) event.stopPropagation();
    const notifs = getStoredNotifications().filter(n => !n.isRead);
    try {
        localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(notifs));
    } catch (e) {}
    updateNotificationBadge();
    renderNotificationsPage();
    renderNotificationDropdown();
    showToast("Read notifications cleared.");

    // Sync with backend if active
    if (typeof MatchingAPI !== "undefined" && MatchingAPI.isBackendLive) {
        fetch(`${MatchingAPI.backendBaseUrl}/api/notifications/clear-read`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        }).catch(() => {});
    }
}


/* --------------------------------------------------------------------------
   13. DYNAMIC PROBLEMS LIST RENDERING (SYNCED WITH COMMUNITY SUBMISSIONS)
   -------------------------------------------------------------------------- */

function renderProblemsList() {
    const cardsContainer = document.getElementById("problemCards");
    if (!cardsContainer) return;

    const problems = getStoredProblems();
    cardsContainer.innerHTML = problems.map(p => {
        const priorityClass = (p.priority || "Medium").toLowerCase();
        const statusClass = (p.status || "Pending").toLowerCase().replace(/\s+/g, '-');

        // Location verification integrity badge
        let verificationBadge = "";
        const suspicion = p.suspicion_score !== undefined ? p.suspicion_score : 0;
        const distKm = (p.mismatch_distance_km !== undefined && p.mismatch_distance_km !== null) ? p.mismatch_distance_km : null;
        if (p.location_status === "Location Mismatch" || suspicion >= 70) {
            verificationBadge = `<span class="badge mismatch" title="GPS Mismatch: ${distKm !== null ? distKm.toFixed(1) + 'km' : 'Suspicious distance'}"><i class="ri-alert-line"></i> Mismatch${distKm !== null ? ' (' + distKm.toFixed(0) + 'km)' : ''}</span>`;
        } else if (p.location_status === "Needs Verification" || suspicion >= 35) {
            verificationBadge = `<span class="badge warning" title="Manual verification recommended"><i class="ri-shield-user-line"></i> Needs Verification</span>`;
        } else if (p.location_status === "Location Verified" || p.location_status === "Verified") {
            verificationBadge = `<span class="badge verified" title="GPS Verified location within radius"><i class="ri-check-line"></i> GPS Verified</span>`;
        } else if (p.location_status === "Acceptable" || p.location_status === "Acceptable Local Distance") {
            verificationBadge = `<span class="badge info" title="Local community radius"><i class="ri-map-pin-2-line"></i> Local (${distKm !== null ? distKm.toFixed(1) + 'km' : 'Vicinity'})</span>`;
        } else {
            verificationBadge = `<span class="badge neutral" title="Citizen manual submission"><i class="ri-map-pin-line"></i> Manual Report</span>`;
        }

        // Duplicate report indicator badge
        let duplicateBadge = "";
        if (p.is_duplicate || (p.duplicate_score && p.duplicate_score >= 0.60)) {
            const pct = Math.round((p.duplicate_score || 0.6) * 100);
            duplicateBadge = `<span class="badge duplicate" title="Linked duplicate of ${p.duplicate_of_id || 'existing issue'} (${pct}%)"><i class="ri-file-copy-line"></i> Duplicate (${pct}%)</span>`;
        }

        const supports = p.support_count || 1;

        return `
            <div class="problem-card" data-category="${escapeHtml(p.category)}" data-status="${escapeHtml(p.status || 'Pending')}" data-locstatus="${escapeHtml(p.location_status || '')}" data-isdup="${p.is_duplicate ? 'true' : 'false'}">
                <div class="card-top">
                    <span class="badge ${priorityClass}">
                        ${escapeHtml(p.priority || 'Medium')} Priority
                    </span>
                    <div style="display: flex; gap: 4px; flex-wrap: wrap; align-items: center;">
                        ${verificationBadge}
                        ${duplicateBadge}
                        <span style="font-size: 0.8rem; font-weight: 600; color: var(--muted);">#${escapeHtml(p.id)}</span>
                    </div>
                </div>

                <h3>${escapeHtml(p.title)}</h3>

                <p>${escapeHtml(p.description.length > 120 ? p.description.substring(0, 117) + '...' : p.description)}</p>

                <div class="card-meta">
                    <span>📍 ${escapeHtml(p.district || p.location || 'Jharkhand')}</span>
                    <span>${escapeHtml(p.category)}</span>
                    <span style="display: inline-flex; align-items: center; gap: 3px; font-weight: 600; color: #10b981;" title="Citizen Community Support Count">
                        <i class="ri-thumb-up-fill"></i> ${supports} ${supports === 1 ? 'Support' : 'Supports'}
                    </span>
                </div>

                <div class="card-footer">
                    <span class="status ${statusClass}">
                        ${escapeHtml(p.status || 'Pending')}
                    </span>

                    <div class="card-actions">
                        <button type="button" class="primary-btn ai-matches-btn" onclick="openProblemMatches('${escapeQuotes(p.id)}')">
                            <i class="ri-cpu-line"></i> AI Matches
                        </button>
                        <button type="button" class="details-btn" onclick="viewProblem('${escapeQuotes(p.id)}')">
                            Details →
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}


/* --------------------------------------------------------------------------
   14. DUAL-MODE API BRIDGE (CLIENT + PYTHON BACKEND)
   -------------------------------------------------------------------------- */

const MatchingAPI = {
    backendBaseUrl: "http://localhost:8000",
    isBackendLive: false,

    async checkBackend() {
        try {
            const res = await fetch(`${this.backendBaseUrl}/api/health`, { method: "GET", headers: { "Accept": "application/json" } });
            if (res.ok) {
                this.isBackendLive = true;
                console.log("[Samadhan 24/7] Connected to live Python REST API Server at http://localhost:8000");
                await this.syncProblems();
                this.syncNotifications();
                updateIntegrityDashboardStats();
                updateDomainStatistics();
                return true;
            }
        } catch (e) {
            this.isBackendLive = false;
        }
        return false;
    },

    async syncProblems() {
        if (!this.isBackendLive) return;
        try {
            const res = await fetch(`${this.backendBaseUrl}/api/problems`);
            if (res.ok) {
                const data = await res.json();
                if (data && Array.isArray(data.data) && data.data.length > 0) {
                    const localProblems = getStoredProblems();
                    const localMap = new Map(localProblems.map(p => [p.id, p]));
                    
                    const merged = data.data.map(bp => {
                        const local = localMap.get(bp.id);
                        return {
                            id: bp.id,
                            title: bp.title,
                            description: bp.description,
                            category: bp.category,
                            subCategory: bp.sub_category || "",
                            location: bp.location || "",
                            district: bp.district || "Ranchi",
                            state: bp.state || "Jharkhand",
                            latitude: bp.latitude,
                            longitude: bp.longitude,
                            current_latitude: bp.current_latitude,
                            current_longitude: bp.current_longitude,
                            distance_km: bp.distance_km,
                            mismatch_distance_km: bp.distance_km,
                            location_status: bp.location_status || "verified",
                            suspicion_score: bp.suspicion_score || 0,
                            verification_status: bp.verification_status || "Verified",
                            is_duplicate: Boolean(bp.is_duplicate || (bp.duplicate_score && bp.duplicate_score >= 0.60) || bp.duplicate_status === "Reported Anyway"),
                            duplicate_score: bp.duplicate_score || 0,
                            duplicate_of_id: bp.duplicate_of_report_id || "",
                            duplicate_status: bp.duplicate_status || "Original",
                            support_count: bp.support_count || (local ? local.support_count : 1),
                            priority: bp.priority || "Medium",
                            status: bp.status || "Pending",
                            submittedBy: bp.submitted_by || "Citizen Portal User",
                            submittedAt: bp.created_at || "Recently"
                        };
                    });

                    localProblems.forEach(lp => {
                        if (!merged.some(m => m.id === lp.id)) {
                            merged.unshift(lp);
                        }
                    });

                    localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(merged));
                    if (typeof renderProblemsList === "function") renderProblemsList();
                    updateIntegrityDashboardStats();
                    updateDomainStatistics();
                }
            }
        } catch (e) {
            console.warn("Problems sync notice:", e);
        }
    },

    async fetchDomainStats(district) {
        if (this.isBackendLive) {
            try {
                const q = encodeURIComponent(district || "All Districts");
                const res = await fetch(`${this.backendBaseUrl}/api/reports/domain-stats?district=${q}`);
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend domain stats fetch notice:", e);
            }
        }
        return null;
    },

    async verifyReport(reportId) {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/reports/${encodeURIComponent(reportId)}/verify`, {
                    method: "POST"
                });
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend verify failed:", e);
            }
        }
        return null;
    },

    async rejectReport(reportId) {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/reports/${encodeURIComponent(reportId)}/reject`, {
                    method: "POST"
                });
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend reject failed:", e);
            }
        }
        return null;
    },

    async resolveDuplicate(reportId) {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/reports/${encodeURIComponent(reportId)}/resolve-duplicate`, {
                    method: "POST"
                });
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend resolve duplicate failed:", e);
            }
        }
        return null;
    },

    async syncNotifications() {
        if (!this.isBackendLive) return;
        try {
            const res = await fetch(`${this.backendBaseUrl}/api/notifications`);
            if (res.ok) {
                const data = await res.json();
                if (data && Array.isArray(data.data) && data.data.length > 0) {
                    const localNotifs = getStoredNotifications();
                    const localMap = new Map(localNotifs.map(n => [n.id, n]));
                    data.data.forEach(bn => {
                        if (localMap.has(bn.id)) {
                            localMap.get(bn.id).isRead = Boolean(bn.is_read);
                        } else {
                            localNotifs.unshift({
                                id: bn.id,
                                recipientType: bn.recipient_type || "Admin",
                                problemId: bn.problem_id || "",
                                title: bn.title || "Notification",
                                message: bn.message || "",
                                isRead: Boolean(bn.is_read),
                                timeAgo: "Recently"
                            });
                        }
                    });
                    localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(localNotifs));
                    updateNotificationBadge();
                    if (typeof renderNotificationsPage === "function") renderNotificationsPage();
                }
            }
        } catch (e) {}
    },

    async fetchMatches(problemId) {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/matching/problem/${encodeURIComponent(problemId)}`);
                if (res.ok) {
                    const data = await res.json();
                    return data;
                }
            } catch (e) {
                console.warn("Backend fetch failed, using local matching engine", e);
            }
        }
        return getMatchesForProblem(problemId);
    },

    async verifyLocation(payload) {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/reports/location-verification`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend location verification failed:", e);
            }
        }
        return null;
    },

    async checkDuplicate(payload) {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/reports/check-duplicate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend duplicate check failed:", e);
            }
        }
        return null;
    },

    async supportProblem(problemId) {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/reports/${encodeURIComponent(problemId)}/support`, {
                    method: "POST"
                });
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend support action failed:", e);
            }
        }
        return null;
    },

    async fetchStats() {
        if (this.isBackendLive) {
            try {
                const res = await fetch(`${this.backendBaseUrl}/api/reports/stats`);
                if (res.ok) return await res.json();
            } catch (e) {
                console.warn("Backend stats fetch failed:", e);
            }
        }
        return null;
    }
};


/* --------------------------------------------------------------------------
   15. MASTER SMART MATCHING INITIALIZATION
   -------------------------------------------------------------------------- */

function initializeSmartMatching() {
    // 1. Ensure initial sample problems, collaborations, and notifications exist
    getStoredProblems();
    getStoredCollaborations();
    getStoredNotifications();

    // 2. Precompute initial matches for sample problems
    SAMPLE_PROBLEMS.forEach(p => {
        runAutoMatchingForProblem(p.id);
    });

    // 3. Render matching page
    renderMatchingPage();

    // 4. Render problems page with live AI badges
    renderProblemsList();

    // 5. Update notification badge
    updateNotificationBadge();

    // 6. Test backend live connection asynchronously
    MatchingAPI.checkBackend();
}


/* --------------------------------------------------------------------------
   GLOBAL ESCAPE LISTENER (ENHANCED FOR MATCHING MODALS)
   -------------------------------------------------------------------------- */

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        if (typeof closeNotificationDropdown === "function") closeNotificationDropdown();
        if (typeof closeUniversityProfileModal === "function") closeUniversityProfileModal();
        if (typeof closeIndustryProfileModal === "function") closeIndustryProfileModal();
        closeMatchingModal("matchingUniModal");
        closeMatchingModal("matchingIndModal");
        closeMatchingModal("collaborationModal");
        closeEditProfileModal();
        closeLogoutModal();
        closeResetSettingsModal();
    }
});

// Click outside listener to close notification dropdown
document.addEventListener("click", (event) => {
    const wrapper = document.getElementById("notifDropdownWrapper");
    const dropdown = document.getElementById("notificationDropdown");
    if (dropdown && dropdown.classList.contains("active")) {
        if (wrapper && !wrapper.contains(event.target)) {
            closeNotificationDropdown();
        }
    }
});


/* --------------------------------------------------------------------------
   16. REAL-TIME FRAUD & DUPLICATE DETECTION SUBSYSTEM (FEATURES 1 & 2)
   -------------------------------------------------------------------------- */

// Global state for live GPS, verification analysis, and duplicate check
window.userCurrentGps = null;
window.currentLocationVerification = null;
window.currentDuplicateResult = null;
window.overrideDuplicateReport = false;
let duplicateDetectionTimer = null;

/**
 * Configurable thresholds for location consistency and fraud risk assessment
 */
const LOCATION_RISK_THRESHOLDS = {
    consistentMeters: 100,
    minorDifferenceMeters: 1000,
    mismatchMeters: 5000
};
window.LOCATION_RISK_THRESHOLDS = LOCATION_RISK_THRESHOLDS;

/**
 * Calculate the great-circle geographic distance between two points using the Haversine formula.
 * Returns distance in meters.
 * @param {number} currentLatitude
 * @param {number} currentLongitude
 * @param {number} reportedLatitude
 * @param {number} reportedLongitude
 * @returns {number|null} Distance in meters
 */
function calculateHaversineDistance(currentLatitude, currentLongitude, reportedLatitude, reportedLongitude) {
    if (currentLatitude === null || currentLatitude === undefined || isNaN(currentLatitude) ||
        currentLongitude === null || currentLongitude === undefined || isNaN(currentLongitude) ||
        reportedLatitude === null || reportedLatitude === undefined || isNaN(reportedLatitude) ||
        reportedLongitude === null || reportedLongitude === undefined || isNaN(reportedLongitude)) {
        return null;
    }
    const R = 6371000.0; // Earth mean radius in meters
    const toRad = (deg) => (deg * Math.PI) / 180.0;
    const dLat = toRad(reportedLatitude - currentLatitude);
    const dLon = toRad(reportedLongitude - currentLongitude);
    const lat1 = toRad(currentLatitude);
    const lat2 = toRad(reportedLatitude);

    const a = Math.sin(dLat / 2.0) * Math.sin(dLat / 2.0) +
              Math.cos(lat1) * Math.cos(lat2) *
              Math.sin(dLon / 2.0) * Math.sin(dLon / 2.0);
    const c = 2.0 * Math.atan2(Math.sqrt(a), Math.sqrt(Math.max(0.0, 1.0 - a)));
    return R * c;
}

/**
 * Haversine formula returning distance in kilometers with 2 decimal precision
 */
function calculateHaversineDistanceKm(lat1, lon1, lat2, lon2) {
    const meters = calculateHaversineDistance(lat1, lon1, lat2, lon2);
    if (meters === null) return null;
    return parseFloat((meters / 1000.0).toFixed(2));
}

/**
 * Primary Controller: updates location verification card via real-time telemetry
 */
async function verifyLocationConsistencyUI() {
    const latField = document.getElementById("latitude");
    const lonField = document.getElementById("longitude");
    const districtSelect = document.getElementById("district");
    const stateInput = document.getElementById("state");

    let repLat = latField && latField.value ? parseFloat(latField.value) : null;
    let repLon = lonField && lonField.value ? parseFloat(lonField.value) : null;
    const district = districtSelect ? districtSelect.value : "Ranchi";
    const state = stateInput ? stateInput.value : "Jharkhand";

    // If coordinates not directly set, look up district centroid
    if ((repLat === null || isNaN(repLat) || repLon === null || isNaN(repLon)) && district) {
        const dCoord = JHARKHAND_DISTRICTS.find(d => d.name.toLowerCase() === district.toLowerCase());
        if (dCoord) {
            repLat = dCoord.lat;
            repLon = dCoord.lon;
        }
    }

    const curGps = window.userCurrentGps || {};
    const curLat = (curGps.latitude !== undefined && curGps.latitude !== null && !isNaN(curGps.latitude)) ? curGps.latitude : null;
    const curLon = (curGps.longitude !== undefined && curGps.longitude !== null && !isNaN(curGps.longitude)) ? curGps.longitude : null;
    const curAcc = (curGps.accuracy !== undefined && curGps.accuracy !== null && !isNaN(curGps.accuracy)) ? curGps.accuracy : 10;

    // 1. Instant local verification conforming to exact configurable thresholds and GPS accuracy
    const localRes = performLocalLocationVerification(curLat, curLon, curAcc, repLat, repLon, district);
    renderLocationVerificationCard(localRes, curLat, curLon, repLat, repLon, district);

    // 2. Asynchronously notify backend REST API if active
    if (typeof MatchingAPI !== "undefined" && MatchingAPI.isBackendLive) {
        MatchingAPI.verifyLocation({
            current_latitude: curLat,
            current_longitude: curLon,
            current_accuracy: curAcc,
            reported_latitude: repLat,
            reported_longitude: repLon,
            district: district,
            state: state
        });
    }
}

/**
 * Local Location Verification algorithm conforming to exact project thresholds,
 * GPS accuracy radius comparison, and transparent multi-signal fraud scoring.
 */
function performLocalLocationVerification(curLat, curLon, curAcc, repLat, repLon, district) {
    const repAcc = 10;
    const source = (selectedLocationDetails && selectedLocationDetails.source) || (curLat ? "browser_geolocation" : "manual");

    // EDGE CASE 1: Current GPS unavailable
    if (curLat === null || curLat === undefined || curLon === null || curLon === undefined || isNaN(curLat) || isNaN(curLon)) {
        return {
            currentGps: { latitude: null, longitude: null, accuracy: null, timestamp: null },
            reportedLocation: { latitude: repLat, longitude: repLon, accuracy: repAcc, source: source },
            distanceMeters: null,
            distanceKm: null,
            locationRiskScore: 0,
            suspicionRisk: 0,
            locationStatus: "Current GPS not available",
            verificationStatus: "Manual Location Accepted",
            statusCode: "gps_unavailable",
            isMismatch: false,
            recommendedAction: "Normal Processing",
            riskTierLabel: "LOW RISK",
            riskBreakdown: {
                locationPoints: 0,
                duplicatePoints: 0,
                userDiscount: -15,
                reportConsistencyDiscount: -10,
                travelPoints: 0
            },
            message: "Current GPS not available. Complaint accepted with manual location without penalty."
        };
    }

    // EDGE CASE 2: Reported location not selected
    if (repLat === null || repLat === undefined || repLon === null || repLon === undefined || isNaN(repLat) || isNaN(repLon)) {
        return {
            currentGps: { latitude: curLat, longitude: curLon, accuracy: curAcc, timestamp: (window.userCurrentGps && window.userCurrentGps.timestamp) || Date.now() },
            reportedLocation: { latitude: null, longitude: null, accuracy: null, source: "none" },
            distanceMeters: null,
            distanceKm: null,
            locationRiskScore: 0,
            suspicionRisk: 0,
            locationStatus: "Reported location not selected",
            verificationStatus: "Awaiting Location Pin",
            statusCode: "reported_location_missing",
            isMismatch: false,
            recommendedAction: "Awaiting Selection",
            riskTierLabel: "LOW RISK",
            riskBreakdown: {
                locationPoints: 0,
                duplicatePoints: 0,
                userDiscount: 0,
                reportConsistencyDiscount: 0,
                travelPoints: 0
            },
            message: "Problem coordinates not yet chosen. Please drop a pin or select district on the map."
        };
    }

    // REAL HAVERSINE DISTANCE CALCULATION
    const distMeters = calculateHaversineDistance(curLat, curLon, repLat, repLon);
    const distKm = parseFloat((distMeters / 1000.0).toFixed(2));
    const accuracyRadius = (curAcc !== undefined && curAcc !== null && !isNaN(curAcc)) ? curAcc : 10;
    const isWithinAccuracy = distMeters <= accuracyRadius;
    const isPoorAccuracy = accuracyRadius > 100;

    // LOCATION RISK CONTRIBUTION & STATUS DETERMINATION
    let locationRiskScore = 0;
    let locationStatus = "🟢 Location Consistent";
    let verificationStatus = "Automatically Verified";
    let statusCode = "consistent";
    let isMismatch = false;
    let accuracyNote = "";

    if (isWithinAccuracy) {
        // TEST 5: Within GPS accuracy range -> do NOT flag as suspicious
        locationRiskScore = 0;
        locationStatus = "🟢 Location Consistent";
        verificationStatus = "Automatically Verified";
        statusCode = "consistent";
        accuracyNote = "Within GPS accuracy range";
        isMismatch = false;
    } else if (distMeters <= LOCATION_RISK_THRESHOLDS.consistentMeters) {
        // 0–100m: LOCATION CONSISTENT
        locationRiskScore = 0;
        locationStatus = "🟢 Location Consistent";
        verificationStatus = "Automatically Verified";
        statusCode = "consistent";
        accuracyNote = "Within standard demo threshold (100m)";
        isMismatch = false;
    } else if (distMeters <= LOCATION_RISK_THRESHOLDS.minorDifferenceMeters) {
        // 100m–1km: MINOR LOCATION DIFFERENCE
        locationRiskScore = 10;
        locationStatus = "🟡 Minor Location Difference";
        verificationStatus = "Manual Verification Recommended";
        statusCode = "minor_difference";
        accuracyNote = "Moderate local vicinity deviation";
        isMismatch = false;
    } else if (distMeters <= LOCATION_RISK_THRESHOLDS.mismatchMeters) {
        // 1km–5km: LOCATION MISMATCH
        locationRiskScore = 30;
        locationStatus = "🟠 Location Mismatch";
        verificationStatus = "Additional Verification Required";
        statusCode = "mismatch";
        accuracyNote = "Reported location differs from GPS by >1 km";
        isMismatch = true;
    } else {
        // >5km: HIGH LOCATION DIFFERENCE / HIGH VERIFICATION RISK
        locationRiskScore = 50;
        locationStatus = "🔴 High Location Difference";
        verificationStatus = "Human Review Recommended";
        statusCode = "high_risk";
        accuracyNote = "Reported location differs from GPS by >5 km";
        isMismatch = true;
    }

    // MULTI-SIGNAL RISK SCORING
    // baseRisk = 0, distance contribution = +0, +10, +30, or +50
    // duplicate (+20), travel (+20), inconsistent (+15), verified user (-15), report consistency (-10)
    const isDup = window.currentDuplicateResult && window.currentDuplicateResult.duplicate_score >= 0.60;
    const duplicatePoints = isDup ? 20 : 0;
    const travelPoints = 0;
    const inconsistentPoints = 0;
    const userDiscount = -15; // Logged-in verified citizen session

    const titleEl = document.getElementById("problemTitle");
    const descEl = document.getElementById("description");
    const hasDetailedText = (titleEl && titleEl.value.trim().length >= 8) || (descEl && descEl.value.trim().length >= 25);
    const reportConsistencyDiscount = hasDetailedText ? -10 : -5;

    // Map each status tier transparently to the prompt status bands:
    // 0–20: LOW RISK (Consistent / within GPS accuracy)
    // 21–40: LOW-MODERATE RISK (Minor Location Difference)
    // 41–70: REVIEW RECOMMENDED (Location Mismatch)
    // 71–100: HIGH VERIFICATION RISK (High Location Difference)
    let calculatedRisk = 0;
    if (statusCode === "consistent") {
        calculatedRisk = Math.max(0, 5 + duplicatePoints + travelPoints + inconsistentPoints);
    } else if (statusCode === "minor_difference") {
        calculatedRisk = 25 + duplicatePoints + travelPoints + inconsistentPoints;
    } else if (statusCode === "mismatch") {
        calculatedRisk = 45 + duplicatePoints + travelPoints + inconsistentPoints;
    } else {
        calculatedRisk = 75 + duplicatePoints + travelPoints + inconsistentPoints;
    }

    const finalRisk = Math.max(0, Math.min(100, calculatedRisk));

    let riskTierLabel = "LOW RISK";
    let recommendedAction = "Normal Processing";
    if (finalRisk <= 20) {
        riskTierLabel = "LOW RISK";
        recommendedAction = "Normal Processing";
        if (statusCode === "consistent") {
            locationStatus = "🟢 Location Consistent";
            verificationStatus = "Automatically Verified";
        }
    } else if (finalRisk <= 40) {
        riskTierLabel = "LOW-MODERATE RISK";
        recommendedAction = "Manual Verification Recommended";
        if (statusCode !== "mismatch" && statusCode !== "high_risk") {
            locationStatus = "🟡 Minor Location Difference";
            verificationStatus = "Manual Verification Recommended";
        }
    } else if (finalRisk <= 70) {
        riskTierLabel = "REVIEW RECOMMENDED";
        recommendedAction = "Additional Verification Required";
        if (statusCode !== "high_risk") {
            locationStatus = "🟠 Location Mismatch";
            verificationStatus = "Additional Verification Required";
        }
    } else {
        riskTierLabel = "HIGH VERIFICATION RISK";
        recommendedAction = "Human Review Recommended";
        locationStatus = "🔴 High Location Difference";
        verificationStatus = "Human Review Recommended";
    }

    let message = "";
    if (isMismatch) {
        message = "Location differs from current GPS — verification may be required.";
    } else if (isWithinAccuracy) {
        message = "Within GPS accuracy range — automatically verified.";
    } else {
        message = "Location consistent with device GPS.";
    }

    return {
        currentGps: {
            latitude: curLat,
            longitude: curLon,
            accuracy: accuracyRadius,
            timestamp: (window.userCurrentGps && window.userCurrentGps.timestamp) || Date.now()
        },
        reportedLocation: {
            latitude: repLat,
            longitude: repLon,
            accuracy: repAcc,
            source: source
        },
        distanceMeters: distMeters,
        distanceKm: distKm,
        locationRiskScore: locationRiskScore,
        suspicionRisk: finalRisk,
        locationStatus: locationStatus,
        verificationStatus: verificationStatus,
        statusCode: statusCode,
        isMismatch: isMismatch,
        isWithinAccuracy: isWithinAccuracy,
        isPoorAccuracy: isPoorAccuracy,
        accuracyNote: accuracyNote,
        riskTierLabel: riskTierLabel,
        recommendedAction: recommendedAction,
        riskBreakdown: {
            locationPoints: locationRiskScore,
            duplicatePoints: duplicatePoints,
            userDiscount: userDiscount,
            reportConsistencyDiscount: reportConsistencyDiscount,
            travelPoints: travelPoints
        },
        message: message
    };
}

/**
 * Render location verification card into DOM
 */
function renderLocationVerificationCard(data, curLat, curLon, repLat, repLon, district) {
    window.locationVerification = data;
    window.currentLocationVerification = data;

    const curGpsText = document.getElementById("locCurrentGpsText");
    const repLocText = document.getElementById("locReportedLocationText");
    const distText = document.getElementById("locDistanceText");
    const suspicionText = document.getElementById("locSuspicionText");
    const consistencyText = document.getElementById("locConsistencyText");
    const verificationText = document.getElementById("locVerificationText");
    const statusPill = document.getElementById("locationStatusPill");
    const statusBadge = document.getElementById("locStatusBadge");
    const alertBanner = document.getElementById("locAlertBanner");
    const alertIcon = document.getElementById("locAlertIcon");
    const alertTitle = document.getElementById("locAlertTitle");
    const alertMsg = document.getElementById("locAlertMsg");

    // 1. Current GPS Display
    if (curGpsText) {
        if (curLat !== null && curLon !== null && !isNaN(curLat) && !isNaN(curLon)) {
            curGpsText.textContent = `${curLat.toFixed(4)}, ${curLon.toFixed(4)}`;
        } else {
            curGpsText.textContent = "Not detected yet";
        }
    }

    // 2. Reported Location Display
    if (repLocText) {
        if (repLat !== null && repLon !== null && !isNaN(repLat) && !isNaN(repLon)) {
            const curLocSub = district ? ` (${district})` : "";
            repLocText.textContent = `${repLat.toFixed(4)}, ${repLon.toFixed(4)}${curLocSub}`;
        } else if (district) {
            repLocText.textContent = district;
        } else {
            repLocText.textContent = "Not selected";
        }
    }

    // 3. Haversine Distance
    if (distText) {
        if (data.distanceKm !== null && data.distanceKm !== undefined) {
            distText.textContent = `${data.distanceKm.toFixed(2)} km`;
        } else {
            distText.textContent = "-- km";
        }
    }

    // 4. Suspicion Risk Display
    if (suspicionText) {
        const score = data.suspicionRisk !== undefined ? data.suspicionRisk : 0;
        const tier = data.riskTierLabel || (score <= 20 ? "LOW RISK" : (score <= 40 ? "LOW-MODERATE RISK" : (score <= 70 ? "REVIEW RECOMMENDED" : "HIGH VERIFICATION RISK")));
        let color = "#10b981";
        if (score > 70) color = "#ef4444";
        else if (score > 40) color = "#f97316";
        else if (score > 20) color = "#f59e0b";

        suspicionText.innerHTML = `<span style="color: ${color}; font-weight: 700;">${score}%</span> <small style="color: var(--muted); font-size: 0.75rem;">(${tier})</small>`;
    }

    // 5. Location Consistency Text
    if (consistencyText) {
        if (data.statusCode === "gps_unavailable") {
            consistencyText.textContent = "Current GPS not available";
            consistencyText.style.color = "#64748b";
        } else if (data.statusCode === "reported_location_missing") {
            consistencyText.textContent = "Reported location not selected";
            consistencyText.style.color = "#64748b";
        } else if (data.isWithinAccuracy) {
            consistencyText.textContent = "🟢 Consistent (Within GPS accuracy range)";
            consistencyText.style.color = "#10b981";
        } else {
            consistencyText.textContent = data.locationStatus;
            if (data.statusCode === "consistent") consistencyText.style.color = "#10b981";
            else if (data.statusCode === "minor_difference") consistencyText.style.color = "#f59e0b";
            else if (data.statusCode === "mismatch") consistencyText.style.color = "#f97316";
            else consistencyText.style.color = "#ef4444";
        }
    }

    // 6. Verification Status Text
    if (verificationText) {
        verificationText.textContent = data.verificationStatus || "Automatically Verified";
        if (data.verificationStatus === "Automatically Verified") {
            verificationText.style.color = "#059669";
        } else if (data.verificationStatus === "Manual Verification Recommended") {
            verificationText.style.color = "#d97706";
        } else if (data.verificationStatus === "Additional Verification Required") {
            verificationText.style.color = "#ea580c";
        } else {
            verificationText.style.color = "#dc2626";
        }
    }

    // 7. Status Pill & Badge
    if (statusPill) {
        statusPill.className = "status-pill";
        if (data.statusCode === "consistent" || data.isWithinAccuracy) {
            statusPill.classList.add("status-pill-success");
            statusPill.innerHTML = '<i class="ri-checkbox-circle-fill"></i> LOCATION CONSISTENT';
        } else if (data.statusCode === "minor_difference") {
            statusPill.classList.add("status-pill-warning");
            statusPill.innerHTML = '<i class="ri-alert-line"></i> MINOR LOCATION DIFFERENCE';
        } else if (data.statusCode === "mismatch") {
            statusPill.classList.add("status-pill-warning");
            statusPill.innerHTML = '<i class="ri-error-warning-line"></i> LOCATION MISMATCH';
        } else if (data.statusCode === "high_risk") {
            statusPill.classList.add("status-pill-danger");
            statusPill.innerHTML = '<i class="ri-error-warning-fill"></i> HIGH VERIFICATION RISK';
        } else {
            statusPill.classList.add("status-pill-neutral");
            statusPill.innerHTML = '<i class="ri-radar-line"></i> Citizen Manual Report';
        }
    }

    if (statusBadge) {
        statusBadge.textContent = `✓ ${data.verificationStatus || "Awaiting Check"}`;
        if (data.statusCode === "consistent" || data.isWithinAccuracy) statusBadge.style.color = "#10b981";
        else if (data.statusCode === "minor_difference") statusBadge.style.color = "#f59e0b";
        else if (data.statusCode === "mismatch") statusBadge.style.color = "#f97316";
        else if (data.statusCode === "high_risk") statusBadge.style.color = "#ef4444";
        else statusBadge.style.color = "#64748b";
    }

    // 8. Warning Banner (Never calls citizen report fraud!)
    if (alertBanner) {
        if (data.isMismatch || data.statusCode === "high_risk" || data.statusCode === "mismatch") {
            alertBanner.style.display = "flex";
            alertBanner.className = data.statusCode === "high_risk" ? "loc-alert-banner danger" : "loc-alert-banner warning";
            if (alertIcon) alertIcon.innerHTML = '<i class="ri-alert-line"></i>';
            if (alertTitle) alertTitle.textContent = "Location Verification Notice";
            if (alertMsg) {
                alertMsg.textContent = "Location differs from current GPS — verification may be required. Citizens reporting for remote villages or family members are fully permitted without penalty.";
            }
        } else {
            alertBanner.style.display = "none";
        }
    }

    // 9. Details Breakdown inside #locExplainDrawer
    updateDetailsDrawerTelemetry(data, curLat, curLon, repLat, repLon);
}

/**
 * Update telemetry details and risk signal breakdown in View Details drawer
 */
function updateDetailsDrawerTelemetry(data, curLat, curLon, repLat, repLon) {
    const detCur = document.getElementById("detCurrentGps");
    const detRep = document.getElementById("detReportedLoc");
    const detGpsAcc = document.getElementById("detGpsAccuracy");
    const detRepAcc = document.getElementById("detReportedAccuracy");
    const detDist = document.getElementById("detDistance");
    const detLocStatus = document.getElementById("detLocationStatus");
    const detLocRisk = document.getElementById("detLocRisk");
    const detDupSignal = document.getElementById("detDupSignal");
    const detUserSignal = document.getElementById("detUserSignal");
    const detReportConsistency = document.getElementById("detReportConsistency");
    const detTravelSignal = document.getElementById("detTravelSignal");
    const detFinalRisk = document.getElementById("detFinalRisk");
    const detRecommendedAction = document.getElementById("detRecommendedAction");

    const gpsAcc = (data.currentGps && data.currentGps.accuracy) || 10;
    const repAcc = (data.reportedLocation && data.reportedLocation.accuracy) || 10;
    const bd = data.riskBreakdown || {};

    if (detCur) detCur.textContent = (curLat !== null && curLon !== null) ? `${curLat.toFixed(5)}, ${curLon.toFixed(5)}` : "Unavailable";
    if (detRep) detRep.textContent = (repLat !== null && repLon !== null) ? `${repLat.toFixed(5)}, ${repLon.toFixed(5)}` : "Not selected";
    if (detGpsAcc) detGpsAcc.textContent = (curLat !== null && curLon !== null) ? `±${Math.round(gpsAcc)} meters` : "N/A";
    if (detRepAcc) detRepAcc.textContent = (repLat !== null && repLon !== null) ? `±${Math.round(repAcc)} meters` : "N/A";
    if (detDist) {
        if (data.distanceKm !== null && data.distanceMeters !== null) {
            detDist.textContent = `${data.distanceKm.toFixed(2)} km (${Math.round(data.distanceMeters)} meters)`;
        } else {
            detDist.textContent = "N/A";
        }
    }
    if (detLocStatus) {
        let statusStr = data.locationStatus || "Pending";
        if (data.isWithinAccuracy) statusStr += " (Within GPS accuracy range)";
        if (data.isPoorAccuracy) statusStr += " [Low GPS accuracy]";
        detLocStatus.textContent = statusStr;
    }
    if (detLocRisk) detLocRisk.textContent = `+${bd.locationPoints !== undefined ? bd.locationPoints : (data.locationRiskScore || 0)} pts`;
    if (detDupSignal) detDupSignal.textContent = `${(bd.duplicatePoints || 0) > 0 ? '+20 pts (Similar report)' : '0 pts (No match)'}`;
    if (detUserSignal) detUserSignal.textContent = `${bd.userDiscount || -15} pts (Verified citizen session)`;
    if (detReportConsistency) detReportConsistency.textContent = `${bd.reportConsistencyDiscount || -10} pts (Report text consistency)`;
    if (detTravelSignal) detTravelSignal.textContent = `${bd.travelPoints || 0} pts (Feasible local range)`;
    if (detFinalRisk) {
        const score = data.suspicionRisk !== undefined ? data.suspicionRisk : 0;
        const tier = data.riskTierLabel || "LOW RISK";
        detFinalRisk.textContent = `${score}% (${tier})`;
    }
    if (detRecommendedAction) detRecommendedAction.textContent = data.recommendedAction || "Normal Processing";
}

/**
 * Reset Location Verification Card UI to default empty state
 */
function resetLocationVerificationCardUI() {
    window.locationVerification = null;
    window.currentLocationVerification = null;
    const curGpsText = document.getElementById("locCurrentGpsText");
    const repLocText = document.getElementById("locReportedLocationText");
    const distText = document.getElementById("locDistanceText");
    const suspicionText = document.getElementById("locSuspicionText");
    const consistencyText = document.getElementById("locConsistencyText");
    const verificationText = document.getElementById("locVerificationText");
    const statusPill = document.getElementById("locationStatusPill");
    const statusBadge = document.getElementById("locStatusBadge");
    const alertBanner = document.getElementById("locAlertBanner");

    if (curGpsText) curGpsText.textContent = "Not detected yet";
    if (repLocText) repLocText.textContent = "Not selected";
    if (distText) distText.textContent = "-- km";
    if (suspicionText) suspicionText.textContent = "0% (LOW RISK)";
    if (consistencyText) {
        consistencyText.textContent = "🟢 Location Consistent";
        consistencyText.style.color = "#10b981";
    }
    if (verificationText) {
        verificationText.textContent = "Automatically Verified";
        verificationText.style.color = "#059669";
    }
    if (statusPill) {
        statusPill.className = "status-pill status-pill-neutral";
        statusPill.innerHTML = '<i class="ri-radar-line"></i> Awaiting GPS Coordinates';
    }
    if (statusBadge) {
        statusBadge.style.color = "#10b981";
        statusBadge.textContent = "✓ Awaiting Check";
    }
    if (alertBanner) alertBanner.style.display = "none";
}

/**
 * Toggle explanation drawer in Location Verification Card
 */
function toggleLocationExplanation() {
    const drawer = document.getElementById("locExplainDrawer");
    const toggleText = document.getElementById("locDetailsToggleText");
    if (!drawer) return;

    if (drawer.style.display === "none" || !drawer.style.display) {
        drawer.style.display = "block";
        if (toggleText) toggleText.textContent = "Hide Details";
    } else {
        drawer.style.display = "none";
        if (toggleText) toggleText.textContent = "View Details";
    }
}

// Global window bindings for cross-scope and automated verification
window.performLocalLocationVerification = performLocalLocationVerification;
window.renderLocationVerificationCard = renderLocationVerificationCard;
window.verifyLocationConsistencyUI = verifyLocationConsistencyUI;
window.toggleLocationExplanation = toggleLocationExplanation;
window.resetLocationVerificationCardUI = resetLocationVerificationCardUI;

/**
 * Debounced trigger for duplicate detection across title, desc, category & location
 */
function triggerDuplicateDetectionDebounced() {
    clearTimeout(duplicateDetectionTimer);
    duplicateDetectionTimer = setTimeout(async () => {
        const titleInput = document.getElementById("problemTitle");
        const descInput = document.getElementById("description");
        const catSelect = document.getElementById("category");
        const districtSelect = document.getElementById("district");
        const latField = document.getElementById("latitude");
        const lonField = document.getElementById("longitude");

        const title = titleInput ? titleInput.value.trim() : "";
        const desc = descInput ? descInput.value.trim() : "";
        const category = catSelect ? catSelect.value : "";
        const district = districtSelect ? districtSelect.value : "Ranchi";
        let repLat = latField && latField.value ? parseFloat(latField.value) : null;
        let repLon = lonField && lonField.value ? parseFloat(lonField.value) : null;

        if (!repLat && district) {
            const dCoord = JHARKHAND_DISTRICTS.find(d => d.name.toLowerCase() === district.toLowerCase());
            if (dCoord) {
                repLat = dCoord.lat;
                repLon = dCoord.lon;
            }
        }

        if (!title || title.length < 5) {
            renderDuplicateWarningCard({ is_duplicate: false });
            return;
        }

        // 1. Try Live Python REST Backend
        const backendRes = await MatchingAPI.checkDuplicate({
            title: title,
            description: desc,
            category: category,
            district: district,
            latitude: repLat,
            longitude: repLon
        });

        if (backendRes) {
            renderDuplicateWarningCard(backendRes);
            return;
        }

        // 2. Local Fallback Duplicate Engine
        const localRes = performLocalDuplicateDetection(title, desc, category, district, repLat, repLon);
        renderDuplicateWarningCard(localRes);
    }, 380);
}

/**
 * Local duplicate detection algorithm using multi-signal scoring
 */
function performLocalDuplicateDetection(title, description, category, district, repLat, repLon) {
    if (!title || title.length < 5) {
        return { is_duplicate: false, duplicate_score: 0.0, best_match: null, reasons: [] };
    }

    const problems = getStoredProblems();
    let bestMatch = null;
    let highestScore = 0.0;
    let bestReasons = [];

    const normTitle = title.toLowerCase();
    const titleWords = new Set(normTitle.split(/\W+/).filter(w => w.length > 2));

    for (const prob of problems) {
        const probTitle = (prob.title || "").toLowerCase();
        const probWords = new Set(probTitle.split(/\W+/).filter(w => w.length > 2));

        // 1. Title token overlap
        let overlap = 0;
        titleWords.forEach(w => { if (probWords.has(w)) overlap++; });
        const unionSize = new Set([...titleWords, ...probWords]).size;
        const titleSim = unionSize > 0 ? (overlap / unionSize) : 0.0;

        // 2. Category match
        let catSim = 0.0;
        if (prob.category && category && prob.category.toLowerCase() === category.toLowerCase()) {
            catSim = 1.0;
        } else if (prob.subCategory && category && prob.subCategory.toLowerCase().includes(category.toLowerCase())) {
            catSim = 0.5;
        }

        // 3. Geographic proximity
        let proxSim = 0.0;
        let dist = null;
        let probLat = prob.latitude;
        let probLon = prob.longitude;
        if ((!probLat || !probLon) && prob.district) {
            const dCoord = JHARKHAND_DISTRICTS.find(d => d.name.toLowerCase() === prob.district.toLowerCase());
            if (dCoord) {
                probLat = dCoord.lat;
                probLon = dCoord.lon;
            }
        }

        if (repLat && repLon && probLat && probLon) {
            dist = calculateHaversineDistanceKm(repLat, repLon, probLat, probLon);
            if (dist !== null) {
                if (dist <= 1.0) proxSim = 1.0;
                else if (dist <= 5.0) proxSim = 0.8;
                else if (dist <= 15.0) proxSim = 0.5;
                else if (dist <= 50.0) proxSim = 0.2;
                else proxSim = 0.0;
            }
        } else if (prob.district && district && prob.district.toLowerCase() === district.toLowerCase()) {
            proxSim = 0.4;
        }

        // 4. Status factor
        let statusFactor = 1.0;
        if (prob.status && prob.status.toLowerCase() === "solved") {
            statusFactor = 0.5;
        }

        // 5. Combined duplicate score
        let score = (0.35 * titleSim + 0.25 * (catSim > 0.5 ? 0.8 : 0.0) + 0.20 * catSim + 0.20 * proxSim) * statusFactor;

        // Cap score if geographically very distant (> 25 km)
        if (dist !== null && dist > 25.0 && score >= 0.60) {
            score = 0.59;
        }

        score = parseFloat(Math.min(0.98, score).toFixed(2));

        if (score > highestScore) {
            highestScore = score;
            bestMatch = {
                ...prob,
                distance_km: dist
            };
            bestReasons = [];
            if (titleSim >= 0.5) bestReasons.push(`High text similarity (${Math.round(titleSim * 100)}%)`);
            else if (titleSim >= 0.25) bestReasons.push(`Moderate title overlap (${Math.round(titleSim * 100)}%)`);
            if (catSim >= 0.8) bestReasons.push(`Identical category: ${prob.category}`);
            if (dist !== null) {
                if (dist <= 1.0) bestReasons.push(`Immediate vicinity (${Math.round(dist * 1000)} meters)`);
                else if (dist <= 10.0) bestReasons.push(`Nearby location (${dist.toFixed(1)} km)`);
            } else if (prob.district && district && prob.district.toLowerCase() === district.toLowerCase()) {
                bestReasons.push(`Same district (${district})`);
            }
            if (prob.status && prob.status.toLowerCase() !== "solved") {
                bestReasons.push(`Active unresolved community issue (Status: ${prob.status})`);
            }
        }
    }

    return {
        is_duplicate: highestScore >= 0.60,
        duplicate_score: highestScore,
        best_match: bestMatch,
        reasons: bestReasons
    };
}

/**
 * Render duplicate warning card into DOM
 */
function renderDuplicateWarningCard(data) {
    const card = document.getElementById("aiDuplicateCard");
    if (!card) return;

    if (!data || !data.is_duplicate || !data.best_match) {
        card.style.display = "none";
        window.currentDuplicateResult = null;
        return;
    }

    window.currentDuplicateResult = {
        id: data.best_match.id,
        title: data.best_match.title,
        category: data.best_match.category,
        district: data.best_match.district || data.best_match.location,
        duplicate_score: data.duplicate_score,
        distance_km: data.best_match.distance_km,
        reasons: data.reasons
    };

    card.style.display = "block";

    const pill = document.getElementById("duplicateStatusPill");
    if (pill) {
        pill.innerHTML = `<i class="ri-alert-fill"></i> Similarity: ${Math.round(data.duplicate_score * 100)}%`;
    }

    const exId = document.getElementById("dupExistingId");
    if (exId) exId.textContent = `#${data.best_match.id}`;

    const exCat = document.getElementById("dupExistingCategory");
    if (exCat) exCat.textContent = data.best_match.category || "--";

    const exLoc = document.getElementById("dupExistingLocation");
    if (exLoc) exLoc.textContent = data.best_match.district || data.best_match.location || "Jharkhand";

    const exDist = document.getElementById("dupExistingDistance");
    if (exDist) {
        if (data.best_match.distance_km !== undefined && data.best_match.distance_km !== null) {
            exDist.textContent = data.best_match.distance_km < 1
                ? `${Math.round(data.best_match.distance_km * 1000)} m`
                : `${data.best_match.distance_km.toFixed(1)} km`;
        } else {
            exDist.textContent = "Same District";
        }
    }

    const exTitle = document.getElementById("dupExistingTitle");
    if (exTitle) exTitle.textContent = data.best_match.title;

    const chipsWrap = document.getElementById("dupReasonsChips");
    if (chipsWrap) {
        const reasons = data.reasons && data.reasons.length > 0
            ? data.reasons
            : ["Text similarity", "Same Category", "Nearby District"];
        chipsWrap.innerHTML = reasons.map(r => `<span class="reason-chip">${escapeHtml(r)}</span>`).join("");
    }
}

/**
 * Interactive Action 1: Citizen chooses to Support Existing Problem instead of submitting a duplicate
 */
async function supportExistingProblemAction() {
    if (!window.currentDuplicateResult || !window.currentDuplicateResult.id) {
        showToast("No active duplicate report selected.");
        return;
    }

    const dupId = window.currentDuplicateResult.id;
    const problems = getStoredProblems();
    const prob = problems.find(p => p.id === dupId);

    if (prob) {
        prob.support_count = (prob.support_count || 1) + 1;
        try {
            localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(problems));
        } catch (e) {}
    }

    // Call live REST API
    await MatchingAPI.supportProblem(dupId);

    showToast(`✓ Thank you! You added community support to #${dupId}. Total supports: ${prob ? prob.support_count : 2}. Priority boosted!`);

    addNotification(
        "Admin",
        dupId,
        `Community Support Boosted for #${dupId}`,
        `A citizen supported existing problem #${dupId} instead of submitting a duplicate.`
    );

    renderProblemsList();
    updateIntegrityDashboardStats();

    // Reset form and view problem
    setTimeout(() => {
        const form = document.getElementById("problemForm");
        if (form) form.reset();
        resetProblemMapAndAI();
        showPage("problems");
    }, 1200);
}

/**
 * Interactive Action 2: Citizen chooses to Report Anyway
 */
function reportAnywayAction() {
    if (!window.currentDuplicateResult) return;
    window.overrideDuplicateReport = true;
    showToast(`Proceeding: Your problem will be submitted and linked as a duplicate of #${window.currentDuplicateResult.id} for administrative verification.`);
    const pill = document.getElementById("duplicateStatusPill");
    if (pill) {
        pill.className = "status-pill status-pill-neutral";
        pill.innerHTML = '<i class="ri-check-line"></i> Marked: Report Anyway';
    }
}

/**
 * Interactive Action 3: View Existing Duplicate details
 */
function viewExistingDuplicateModal() {
    if (!window.currentDuplicateResult || !window.currentDuplicateResult.id) return;
    openProblemMatches(window.currentDuplicateResult.id);
}

/**
 * Normalize category string to one of the 5 core dashboard domains
 */
function normalizeProblemDomain(category) {
    if (!category) return "Other";
    const cat = String(category).trim().toLowerCase();
    if (cat.includes("educat") || cat.includes("school") || cat.includes("skill") || cat.includes("learn")) {
        return "Education";
    }
    if (cat.includes("health") || cat.includes("medic") || cat.includes("clinic") || cat.includes("sanitat") || cat.includes("hospit")) {
        return "Healthcare";
    }
    if (cat.includes("agri") || cat.includes("farm") || cat.includes("crop") || cat.includes("soil") || cat.includes("irrigat")) {
        return "Agriculture";
    }
    if (cat.includes("water") || cat.includes("jal") || cat.includes("drink")) {
        return "Water";
    }
    if (cat.includes("environ") || cat.includes("forest") || cat.includes("waste") || cat.includes("pollution") || cat.includes("energy") || cat.includes("solar") || cat.includes("climate")) {
        return "Environment";
    }
    return "Other";
}

/**
 * Reusable domain statistics calculation and district filtering engine
 */
function getDomainStatistics(reports, selectedDistrict) {
    const list = Array.isArray(reports) ? reports : [];
    let filtered = list;

    if (selectedDistrict && selectedDistrict !== "All Districts") {
        const selNorm = selectedDistrict.trim().toLowerCase();
        filtered = list.filter(r => (r.district || "").trim().toLowerCase() === selNorm);
    }

    const counts = {
        Education: 0,
        Healthcare: 0,
        Agriculture: 0,
        Water: 0,
        Environment: 0
    };

    filtered.forEach(r => {
        const dom = normalizeProblemDomain(r.category);
        if (counts[dom] !== undefined) {
            counts[dom]++;
        }
    });

    const maxCount = Math.max(counts.Education, counts.Healthcare, counts.Agriculture, counts.Water, counts.Environment);
    const percentages = {};
    for (const key of Object.keys(counts)) {
        percentages[key] = maxCount > 0 ? Math.round((counts[key] / maxCount) * 100) : 0;
    }

    return {
        district: selectedDistrict || "All Districts",
        total: filtered.length,
        counts: counts,
        maxCount: maxCount,
        percentages: percentages
    };
}

/**
 * Dynamic updater for Problems by Domain Section (Red Section)
 */
async function updateDomainStatistics(selectedDistrict = null) {
    const distSelect = document.getElementById("dashboardDistrictFilter");
    if (!selectedDistrict && distSelect) {
        selectedDistrict = distSelect.value;
    }
    if (!selectedDistrict) selectedDistrict = "All Districts";

    let stats = null;

    // 1. Try Backend Domain Stats if online
    if (MatchingAPI && MatchingAPI.isBackendLive) {
        stats = await MatchingAPI.fetchDomainStats(selectedDistrict);
    }

    // 2. Fallback to Local Dataset if backend offline or null
    if (!stats || !stats.counts) {
        const reports = getStoredProblems();
        stats = getDomainStatistics(reports, selectedDistrict);
    }

    const counts = stats.counts || { Education: 0, Healthcare: 0, Agriculture: 0, Water: 0, Environment: 0 };
    const percentages = stats.percentages || {};

    const eduEl = document.getElementById("domainCountEducation");
    const eduBar = document.getElementById("domainBarEducation");
    const heaEl = document.getElementById("domainCountHealthcare");
    const heaBar = document.getElementById("domainBarHealthcare");
    const agrEl = document.getElementById("domainCountAgriculture");
    const agrBar = document.getElementById("domainBarAgriculture");
    const watEl = document.getElementById("domainCountWater");
    const watBar = document.getElementById("domainBarWater");
    const envEl = document.getElementById("domainCountEnvironment");
    const envBar = document.getElementById("domainBarEnvironment");

    if (eduEl) eduEl.textContent = counts.Education;
    if (eduBar) eduBar.style.width = (percentages.Education || 0) + "%";

    if (heaEl) heaEl.textContent = counts.Healthcare;
    if (heaBar) heaBar.style.width = (percentages.Healthcare || 0) + "%";

    if (agrEl) agrEl.textContent = counts.Agriculture;
    if (agrBar) agrBar.style.width = (percentages.Agriculture || 0) + "%";

    if (watEl) watEl.textContent = counts.Water;
    if (watBar) watBar.style.width = (percentages.Water || 0) + "%";

    if (envEl) envEl.textContent = counts.Environment;
    if (envBar) envBar.style.width = (percentages.Environment || 0) + "%";
}

/**
 * Sync and Update Dashboard Integrity Overview Stats (Blue Section)
 */
async function updateIntegrityDashboardStats() {
    let stats = null;

    // 1. Try Live Backend Stats
    if (MatchingAPI && MatchingAPI.isBackendLive) {
        const backendRes = await MatchingAPI.fetchStats();
        if (backendRes) {
            stats = backendRes.stats ? backendRes.stats : backendRes;
        }
    }

    // 2. Local Fallback Stats from localStorage
    if (!stats) {
        const problems = getStoredProblems();
        const total = problems.length;
        const verified = problems.filter(p => p.verification_status === "Verified" || p.location_status === "verified" || p.location_status === "Location Verified" || (p.suspicion_score !== undefined && p.suspicion_score <= 15 && p.location_status !== "Location Mismatch")).length;
        const mismatches = problems.filter(p => p.location_status === "Location Mismatch" || p.location_status === "mismatch" || (p.distance_km && p.distance_km > 50) || (p.mismatch_distance_km && p.mismatch_distance_km > 50) || (p.suspicion_score && p.suspicion_score >= 0.40)).length;
        const dups = problems.filter(p => p.is_duplicate || p.duplicate_status === "Reported Anyway" || p.duplicate_status === "Duplicate Supported" || (p.duplicate_score && p.duplicate_score >= 0.60)).length;
        const underReview = problems.filter(p => p.verification_status === "Needs Verification" || p.status === "Needs Verification" || p.location_status === "Needs Verification" || p.location_status === "moderate_concern").length;

        stats = {
            total_reports: total,
            verified_reports: verified,
            location_mismatches: mismatches,
            duplicate_reports: dups,
            under_verification: underReview
        };
    }

    const tEl = document.getElementById("dashStatTotalReports");
    const vEl = document.getElementById("dashStatVerifiedReports");
    const mEl = document.getElementById("dashStatMismatchReports");
    const dEl = document.getElementById("dashStatDuplicateReports");
    const uEl = document.getElementById("dashStatUnderVerification");

    const totalVal = stats.total_reports !== undefined ? stats.total_reports : "--";
    const verifiedVal = stats.verified_reports !== undefined ? stats.verified_reports : "--";
    const mismatchVal = stats.location_mismatches !== undefined ? stats.location_mismatches : (stats.location_mismatch_reports !== undefined ? stats.location_mismatch_reports : "--");
    const duplicateVal = stats.duplicate_reports !== undefined ? stats.duplicate_reports : "--";
    const underVal = stats.under_verification !== undefined ? stats.under_verification : (stats.reports_under_verification !== undefined ? stats.reports_under_verification : "--");

    if (tEl) tEl.textContent = totalVal;
    if (vEl) vEl.textContent = verifiedVal;
    if (mEl) mEl.textContent = mismatchVal;
    if (dEl) dEl.textContent = duplicateVal;
    if (uEl) uEl.textContent = underVal;
}

/* ==========================================================================
   REVIEW SUSPICIOUS & REVIEW DUPLICATES ADMIN INTERFACES
   ========================================================================== */

function openSuspiciousReviewModal() {
    const modal = document.getElementById("suspiciousReportsModal");
    if (!modal) return;
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
    renderSuspiciousReportsTable();
}

function closeSuspiciousReviewModal() {
    const modal = document.getElementById("suspiciousReportsModal");
    if (modal) modal.classList.remove("active");
    document.body.style.overflow = "";
}

function renderSuspiciousReportsTable() {
    const tbody = document.getElementById("suspiciousReportsTableBody");
    const badge = document.getElementById("suspiciousReportsModalCountBadge");
    if (!tbody) return;

    const problems = getStoredProblems();
    const suspicious = problems.filter(p =>
        p.location_status === "Location Mismatch" ||
        p.location_status === "mismatch" ||
        (p.distance_km && p.distance_km > 50) ||
        (p.mismatch_distance_km && p.mismatch_distance_km > 50) ||
        (p.suspicion_score && p.suspicion_score >= 0.40) ||
        p.verification_status === "Needs Verification"
    );

    if (badge) {
        badge.textContent = `${suspicious.length} Suspicious ${suspicious.length === 1 ? 'Report' : 'Reports'}`;
    }

    if (suspicious.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 32px; color: var(--muted);">
                    <i class="ri-checkbox-circle-fill" style="color: #10b981; font-size: 1.8rem; display: block; margin-bottom: 6px;"></i>
                    <strong>All clear!</strong> No reports currently exceed the 50km threshold or require fraud review.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = suspicious.map(p => {
        const distVal = p.distance_km !== undefined && p.distance_km !== null ? p.distance_km : p.mismatch_distance_km;
        const distStr = distVal !== undefined && distVal !== null ? `${Number(distVal).toFixed(1)} km` : "N/A";
        const isMismatch = (distVal && distVal > 50) || p.location_status === "Location Mismatch" || p.location_status === "mismatch";
        const distBadge = isMismatch ?
            `<span class="badge mismatch" style="font-size: 0.72rem; padding: 2px 6px;"><i class="ri-alert-line"></i> ${distStr} (&gt;50km)</span>` :
            `<span class="badge info" style="font-size: 0.72rem; padding: 2px 6px;">${distStr}</span>`;

        const reason = isMismatch ?
            `Distance > 50km (${distStr})` :
            `Suspicion score ${(p.suspicion_score ? (p.suspicion_score > 1 ? p.suspicion_score : Math.round(p.suspicion_score * 100)) + '%' : 'Pending Review')}`;

        const curGps = (p.current_latitude && p.current_longitude) ?
            `${Number(p.current_latitude).toFixed(3)}, ${Number(p.current_longitude).toFixed(3)}` :
            "GPS Captured";

        const repLoc = (p.latitude && p.longitude) ?
            `${p.location || p.district} (${Number(p.latitude).toFixed(3)}, ${Number(p.longitude).toFixed(3)})` :
            (p.location || p.district || "Jharkhand");

        return `
            <tr>
                <td><strong>#${escapeHtml(p.id)}</strong></td>
                <td>
                    <div style="font-weight: 600; color: var(--text-dark); max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(p.title)}">
                        ${escapeHtml(p.title)}
                    </div>
                </td>
                <td><span>${escapeHtml(p.district || 'Jharkhand')}</span></td>
                <td><small style="color: var(--muted);">${escapeHtml(repLoc)}</small></td>
                <td><small style="color: var(--muted); font-family: monospace;">${escapeHtml(curGps)}</small></td>
                <td>${distBadge}</td>
                <td><span style="font-size: 0.75rem; color: #b91c1c; font-weight: 600;">${escapeHtml(reason)}</span></td>
                <td>
                    <span class="badge ${p.verification_status === 'Verified' ? 'verified' : 'warning'}" style="font-size: 0.72rem;">
                        ${escapeHtml(p.verification_status || 'Needs Verification')}
                    </span>
                </td>
                <td style="text-align: center; white-space: nowrap;">
                    <button type="button" class="primary-btn" style="padding: 4px 8px; font-size: 0.75rem; background: #10b981; border-color: #10b981; margin-right: 4px;" onclick="adminVerifyReport('${escapeQuotes(p.id)}')">
                        <i class="ri-check-line"></i> Verify
                    </button>
                    <button type="button" class="secondary-btn" style="padding: 4px 8px; font-size: 0.75rem; color: #dc2626; margin-right: 4px;" onclick="adminRejectReport('${escapeQuotes(p.id)}')">
                        <i class="ri-close-line"></i> Reject
                    </button>
                    <button type="button" class="secondary-btn" style="padding: 4px 6px; font-size: 0.75rem;" onclick="viewProblem('${escapeQuotes(p.id)}'); closeSuspiciousReviewModal();">
                        <i class="ri-eye-line"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function openDuplicatesReviewModal() {
    const modal = document.getElementById("duplicateReportsModal");
    if (!modal) return;
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
    renderDuplicatesReportsTable();
}

function closeDuplicatesReviewModal() {
    const modal = document.getElementById("duplicateReportsModal");
    if (modal) modal.classList.remove("active");
    document.body.style.overflow = "";
}

function renderDuplicatesReportsTable() {
    const tbody = document.getElementById("duplicateReportsTableBody");
    const badge = document.getElementById("duplicateReportsModalCountBadge");
    if (!tbody) return;

    const problems = getStoredProblems();
    const duplicates = problems.filter(p =>
        p.is_duplicate ||
        (p.duplicate_score && p.duplicate_score >= 0.60) ||
        p.duplicate_status === "Reported Anyway" ||
        p.duplicate_status === "Duplicate Supported"
    );

    if (badge) {
        badge.textContent = `${duplicates.length} ${duplicates.length === 1 ? 'Duplicate' : 'Duplicates'} Flagged`;
    }

    if (duplicates.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 32px; color: var(--muted);">
                    <i class="ri-checkbox-circle-fill" style="color: #10b981; font-size: 1.8rem; display: block; margin-bottom: 6px;"></i>
                    <strong>No duplicates flagged!</strong> All complaints are distinct and verified.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = duplicates.map(p => {
        const score = p.duplicate_score ? (p.duplicate_score > 1 ? p.duplicate_score : Math.round(p.duplicate_score * 100)) : 80;
        const dupOf = p.duplicate_of_id || p.duplicate_of_report_id || "Existing Issue";
        const reason = `${score}% Multi-Signal Match`;

        return `
            <tr>
                <td><strong>#${escapeHtml(p.id)}</strong></td>
                <td>
                    <div style="font-weight: 600; color: var(--text-dark); max-width: 180px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(p.title)}">
                        ${escapeHtml(p.title)}
                    </div>
                </td>
                <td><span class="badge info" style="font-size: 0.72rem;">${escapeHtml(p.category)}</span></td>
                <td><span>${escapeHtml(p.district || 'Jharkhand')}</span></td>
                <td><small style="color: var(--muted);">${escapeHtml(p.submittedAt || 'Recently')}</small></td>
                <td>
                    <a href="javascript:void(0)" onclick="viewProblem('${escapeQuotes(dupOf)}'); closeDuplicatesReviewModal();" style="font-weight: 600; color: var(--primary); text-decoration: underline;">
                        #${escapeHtml(dupOf)}
                    </a>
                </td>
                <td>
                    <span class="badge warning" style="font-size: 0.72rem; padding: 2px 6px;">
                        <i class="ri-radar-line"></i> ${escapeHtml(reason)}
                    </span>
                </td>
                <td>
                    <span class="badge ${p.duplicate_status === 'Original' ? 'verified' : 'neutral'}" style="font-size: 0.72rem;">
                        ${escapeHtml(p.duplicate_status || 'Reported Anyway')}
                    </span>
                </td>
                <td style="text-align: center; white-space: nowrap;">
                    <button type="button" class="primary-btn" style="padding: 4px 8px; font-size: 0.75rem; background: var(--primary); border-color: var(--primary); margin-right: 4px;" onclick="adminResolveDuplicate('${escapeQuotes(p.id)}')">
                        <i class="ri-shield-check-line"></i> Mark Original
                    </button>
                    <button type="button" class="secondary-btn" style="padding: 4px 8px; font-size: 0.75rem; color: #059669; margin-right: 4px;" onclick="adminSupportExistingFromModal('${escapeQuotes(dupOf)}')">
                        <i class="ri-thumb-up-line"></i> Boost #${escapeHtml(dupOf)}
                    </button>
                    <button type="button" class="secondary-btn" style="padding: 4px 6px; font-size: 0.75rem;" onclick="viewProblem('${escapeQuotes(p.id)}'); closeDuplicatesReviewModal();">
                        <i class="ri-eye-line"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

async function adminVerifyReport(reportId) {
    const list = getStoredProblems();
    const item = list.find(p => p.id === reportId);
    if (!item) return;

    item.verification_status = "Verified";
    item.location_status = "Location Verified";
    item.suspicion_score = 0.05;
    if (item.status === "Needs Verification") item.status = "Pending";

    localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(list));

    if (MatchingAPI && MatchingAPI.isBackendLive) {
        MatchingAPI.verifyReport(reportId);
    }

    showToast(`Report #${reportId} location and details successfully verified!`);
    renderSuspiciousReportsTable();
    updateIntegrityDashboardStats();
    updateDomainStatistics();
    if (typeof renderProblemsList === "function") renderProblemsList();
}

async function adminRejectReport(reportId) {
    if (!confirm(`Are you sure you want to flag and reject Report #${reportId} as invalid submission?`)) {
        return;
    }

    const list = getStoredProblems();
    const item = list.find(p => p.id === reportId);
    if (!item) return;

    item.verification_status = "Rejected";
    item.status = "Rejected";

    localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(list));

    if (MatchingAPI && MatchingAPI.isBackendLive) {
        MatchingAPI.rejectReport(reportId);
    }

    showToast(`Report #${reportId} flagged as invalid/rejected.`);
    renderSuspiciousReportsTable();
    updateIntegrityDashboardStats();
    updateDomainStatistics();
    if (typeof renderProblemsList === "function") renderProblemsList();
}

async function adminResolveDuplicate(reportId) {
    const list = getStoredProblems();
    const item = list.find(p => p.id === reportId);
    if (!item) return;

    item.is_duplicate = false;
    item.duplicate_status = "Resolved - Original";
    item.duplicate_score = 0.0;
    item.verification_status = "Verified";

    localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(list));

    if (MatchingAPI && MatchingAPI.isBackendLive) {
        MatchingAPI.resolveDuplicate(reportId);
    }

    showToast(`Report #${reportId} duplicate flag resolved. Marked as independent report.`);
    renderDuplicatesReportsTable();
    updateIntegrityDashboardStats();
    updateDomainStatistics();
    if (typeof renderProblemsList === "function") renderProblemsList();
}

async function adminSupportExistingFromModal(targetId) {
    if (!targetId) return;
    if (MatchingAPI && MatchingAPI.isBackendLive) {
        await MatchingAPI.supportProblem(targetId);
    }
    const list = getStoredProblems();
    const target = list.find(p => p.id === targetId);
    if (target) {
        target.support_count = (target.support_count || 1) + 1;
        localStorage.setItem(STORAGE_KEYS.PROBLEMS, JSON.stringify(list));
    }
    showToast(`Endorsement added! Existing problem #${targetId} community support boosted.`);
    renderDuplicatesReportsTable();
    updateIntegrityDashboardStats();
    updateDomainStatistics();
    if (typeof renderProblemsList === "function") renderProblemsList();
}


/* --------------------------------------------------------------------------
   APPLICATION DOM READY LISTENER & SUBMISSION EVENT BINDING
   -------------------------------------------------------------------------- */

function initProblemSubmitListeners() {
    const titleInput = document.getElementById("problemTitle");
    const descInput = document.getElementById("description");
    const catSelect = document.getElementById("category");
    const districtSelect = document.getElementById("district");
    const areaInput = document.getElementById("area");

    if (titleInput) {
        titleInput.addEventListener("input", handleProblemTextDebounced);
        titleInput.addEventListener("blur", runAICategoryDetection);
    }
    if (descInput) {
        descInput.addEventListener("input", handleProblemTextDebounced);
        descInput.addEventListener("blur", runAICategoryDetection);
    }
    if (catSelect) {
        catSelect.addEventListener("change", function () {
            if (this.value) {
                userManuallySelectedCategory = true;
                const hint = document.getElementById("categoryOverrideHint");
                if (hint) hint.style.display = "inline";
                const statusTag = document.getElementById("aiCatStatusTag");
                if (statusTag) {
                    statusTag.textContent = "✓ User Confirmed";
                    statusTag.style.background = "rgba(16, 185, 129, 0.15)";
                    statusTag.style.color = "#059669";
                }
            }
            triggerDuplicateDetectionDebounced();
        });
    }
    if (districtSelect) {
        districtSelect.addEventListener("change", function () {
            verifyLocationConsistencyUI();
            triggerDuplicateDetectionDebounced();
        });
    }
    if (areaInput) {
        areaInput.addEventListener("input", function () {
            triggerDuplicateDetectionDebounced();
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Sidebar collapsed state from storage
    if (typeof initSidebarState === "function") initSidebarState();

    // Render the data-driven Jharkhand Research Universities
    if (typeof renderMoreUniversities === "function") renderMoreUniversities();

    // Render the data-driven Jharkhand Industry Partners
    if (typeof renderMoreIndustries === "function") renderMoreIndustries();

    // Initialize Admin Settings & Theme System
    initializeSettings();

    // Initialize SIH 2026 Smart Matching Core
    initializeSmartMatching();

    // Initialize Problem Submission Listeners & Map
    initProblemSubmitListeners();
    initProblemLocationMap();

    // Initialize Location Verification baseline
    verifyLocationConsistencyUI();

    // Initialize Integrity Dashboard Overview Stats
    updateIntegrityDashboardStats();
    updateDomainStatistics();

    console.log("Samadhan 24/7 Platform, AI Category Detection, Location Fraud & Duplicate Shield Ready");
});


