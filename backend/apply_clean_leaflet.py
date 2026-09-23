import sys

clean_section_5 = '''/* --------------------------------------------------------------------------
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
'''

with open('my1.js', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '/* --------------------------------------------------------------------------\n   5. GOOGLE MAPS JAVASCRIPT API & SMART LOCATION CONTROLLER'
end_marker = 'function reverseGeocodeLocation(lat, lon) {\n    reverseGeocodeLocationGoogle(lat, lon);\n}'

if start_marker not in content:
    print('ERROR: start_marker not found!')
    sys.exit(1)

if end_marker not in content:
    print('ERROR: end_marker not found!')
    sys.exit(1)

start_pos = content.find(start_marker)
end_pos = content.find(end_marker) + len(end_marker)

new_content = content[:start_pos] + clean_section_5 + content[end_pos:]

with open('my1.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('SUCCESS: Section 5 replaced with pure Leaflet implementation!')
