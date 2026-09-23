import re

with open("my1.js", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update showPage to refresh dashboard stats when navigated
old_show_page_end = """    // Invalidate Leaflet map size when navigating to Submit Problem page
    if (pageId === "submit" && typeof invalidateProblemMap === "function") {
        setTimeout(invalidateProblemMap, 80);
        setTimeout(invalidateProblemMap, 260);
    }

}"""

new_show_page_end = """    // Invalidate Leaflet map size when navigating to Submit Problem page
    if (pageId === "submit" && typeof invalidateProblemMap === "function") {
        setTimeout(invalidateProblemMap, 80);
        setTimeout(invalidateProblemMap, 260);
    }

    if (pageId === "dashboard") {
        if (typeof updateIntegrityDashboardStats === "function") updateIntegrityDashboardStats();
        if (typeof updateDomainStatistics === "function") updateDomainStatistics();
    }

}"""

assert old_show_page_end in content, "old_show_page_end not found!"
content = content.replace(old_show_page_end, new_show_page_end, 1)

# 2. Update saveSubmittedProblem to trigger updateDomainStatistics
old_save_prob = """    if (typeof updateIntegrityDashboardStats === "function") {
        updateIntegrityDashboardStats();
    }

    return newProb;"""

new_save_prob = """    if (typeof updateIntegrityDashboardStats === "function") {
        updateIntegrityDashboardStats();
    }
    if (typeof updateDomainStatistics === "function") {
        updateDomainStatistics();
    }

    return newProb;"""

assert old_save_prob in content, "old_save_prob not found!"
content = content.replace(old_save_prob, new_save_prob, 1)

# 3. Update MatchingAPI in my1.js
old_matching_api = """const MatchingAPI = {
    backendBaseUrl: "http://localhost:8000",
    isBackendLive: false,

    async checkBackend() {
        try {
            const res = await fetch(`${this.backendBaseUrl}/api/health`, { method: "GET", headers: { "Accept": "application/json" } });
            if (res.ok) {
                this.isBackendLive = true;
                console.log("[Samadhan 24/7] Connected to live Python REST API Server at http://localhost:8000");
                updateIntegrityDashboardStats();
                this.syncNotifications();
                return true;
            }
        } catch (e) {
            this.isBackendLive = false;
        }
        return false;
    },"""

new_matching_api = """const MatchingAPI = {
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
    },"""

assert old_matching_api in content, "old_matching_api not found!"
content = content.replace(old_matching_api, new_matching_api, 1)

# 4. Replace updateIntegrityDashboardStats and add domain stats & review modal functions
old_stats_block = """/**
 * Sync and Update Dashboard Integrity Overview Stats
 */
async function updateIntegrityDashboardStats() {
    let stats = null;

    // 1. Try Live Backend Stats
    const backendRes = await MatchingAPI.fetchStats();
    if (backendRes) {
        stats = backendRes.stats ? backendRes.stats : backendRes;
    } else {
        // 2. Local Fallback Stats from localStorage
        const problems = getStoredProblems();
        const total = problems.length;
        const verified = problems.filter(p => p.location_status === "Verified" || p.location_status === "Location Verified" || (p.suspicion_score !== undefined && p.suspicion_score <= 15)).length;
        const mismatches = problems.filter(p => p.location_status === "Location Mismatch" || (p.suspicion_score && p.suspicion_score >= 70)).length;
        const dups = problems.filter(p => p.is_duplicate || (p.duplicate_score && p.duplicate_score >= 0.60)).length;
        const underReview = problems.filter(p => p.status === "Needs Verification" || p.location_status === "Needs Verification" || p.location_status === "Moderate Distance").length;

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
}"""

new_stats_block = """/**
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
                    <a href="javascript:void(0)" onclick="viewProblem('${escapeQuotes(dupOf)}'); closeDuplicatesReviewModal();" style="font-weight: 600; color: #2563eb; text-decoration: underline;">
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
                    <button type="button" class="primary-btn" style="padding: 4px 8px; font-size: 0.75rem; background: #2563eb; border-color: #2563eb; margin-right: 4px;" onclick="adminResolveDuplicate('${escapeQuotes(p.id)}')">
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
}"""

assert old_stats_block in content, "old_stats_block not found!"
content = content.replace(old_stats_block, new_stats_block, 1)

# 5. Update DOMContentLoaded call to initialize domain stats
old_dom_ready = """    // Initialize Integrity Dashboard Overview Stats
    updateIntegrityDashboardStats();"""

new_dom_ready = """    // Initialize Integrity Dashboard Overview Stats
    updateIntegrityDashboardStats();
    updateDomainStatistics();"""

assert old_dom_ready in content, "old_dom_ready not found!"
content = content.replace(old_dom_ready, new_dom_ready, 1)

with open("my1.js", "w", encoding="utf-8") as f:
    f.write(content)

print("my1.js successfully updated!")
