const KNOWN_LOCATIONS = {
  karachi: {
    Garden: [24.8665, 67.0235],
    Saddar: [24.855, 67.005],
    Clifton: [24.8325, 67.043],
    Gulshan: [24.877, 67.0412],
    "Gulshan-e-Iqbal": [24.91, 67.09],
    "North Nazimabad": [24.93, 67.04],
    PECHS: [24.89, 67.045],
    Lyari: [24.88, 66.98],
    Korangi: [24.83, 67.14],
    Malir: [24.9, 67.2],
    DHA: [24.81, 67.05],
    "Federal B Area": [24.92, 67.055],
    "Soldier Bazaar": [24.8681, 67.0261],
    "Garden East": [24.8662, 67.0239],
    "Garden West": [24.8648, 67.0207],
  },
  islamabad: {
    "Blue Area": [33.7167, 73.0587],
    "G-8": [33.6933, 73.0586],
    "G-9": [33.683, 73.06],
    "G-10": [33.672, 73.07],
    "G-11": [33.6675, 73.0007],
    "G-13": [33.65, 72.9639],
    "F-7": [33.724, 73.072],
    "F-8": [33.72, 73.065],
    "F-10": [33.695, 73.062],
    "F-11": [33.6844, 72.9886],
    "E-7": [33.728, 73.08],
    "E-11": [33.6994, 72.9744],
    "D-12": [33.7048, 72.9584],
    "H-8": [33.688, 73.065],
    "H-9": [33.6847, 73.0366],
    "H-11": [33.6622, 72.9995],
    "H-12": [33.6487, 72.995],
    "I-8": [33.71, 73.05],
    "I-9": [33.684, 73.045],
    "I-10": [33.698, 73.042],
    "I-11": [33.6715, 73.0078],
  },
  rawalpindi: {
    Saddar: [33.601, 73.051],
    "Rawalpindi Cantt": [33.598, 73.046],
    Westridge: [33.608, 73.038],
    "Committee Chowk": [33.612, 73.042],
    "Chandni Chowk": [33.605, 73.055],
    "Satellite Town": [33.618, 73.06],
    "Dhoke Choudharian": [33.596, 73.048],
    Lalazar: [33.61, 73.036],
  },
};

let mediaRecorder;
let audioChunks = [];
let activeMicStream = null;
let voiceAudioContext = null;
let voiceMeterFrame = null;
let currentLat = null;
let currentLng = null;
let activeMapView = "map";
let mapsApiKey = "";
let hasValidMapsKey = false;

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function isRtlText(text = "") {
  return /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/.test(text);
}

function setTextDirection(el, text) {
  if (!el) return;
  const rtl = isRtlText(text);
  el.dir = rtl ? "rtl" : "ltr";
  el.classList.toggle("rtl", rtl);
}

function activateView(viewName) {
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.dataset.view === viewName);
  });
  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.viewTarget === viewName);
  });
}

function heartbeatSvg(compact = false) {
  const height = compact ? 70 : 118;
  return `
    <svg class="heartbeat-svg" viewBox="0 0 960 ${height}" aria-hidden="true">
      <defs>
        <linearGradient id="haalatTrace${compact ? "Small" : "Large"}" x1="0%" x2="100%">
          <stop offset="0%" stop-color="#ff243d"/>
          <stop offset="46%" stop-color="#ff243d"/>
          <stop offset="54%" stop-color="#f8fafc"/>
          <stop offset="100%" stop-color="#1fff6e"/>
        </linearGradient>
      </defs>
      <path class="crescent-mark" d="M510 ${height / 2 - 29}c-22 9-38 30-38 55 0 28 19 51 46 58-43 7-82-25-82-68 0-41 36-72 74-65z"/>
      <path class="crescent-mark" d="M572 ${height / 2 + 3}l9 18 20 3-14 14 3 20-18-9-18 9 3-20-14-14 20-3z"/>
      <path class="trace" stroke="url(#haalatTrace${compact ? "Small" : "Large"})"
        d="M8 ${height / 2} H128 L155 ${height / 2} L177 ${height / 2 - 28} L205 ${height / 2 + 38} L235 ${height / 2 - 48} L268 ${height / 2} H420 C470 ${height / 2}, 500 ${height / 2}, 540 ${height / 2} H684 L710 ${height / 2 - 32} L738 ${height / 2 + 31} L772 ${height / 2 - 44} L812 ${height / 2} H952"/>
    </svg>`;
}

function severityTone(severity) {
  const n = Number(severity || 0);
  if (n >= 4) return "red";
  if (n >= 3) return "amber";
  return "green";
}

function severityLabel(severity) {
  const n = Number(severity || 0);
  if (n >= 5) return "Immediate Life Threat";
  if (n === 4) return "Critical Dispatch";
  if (n === 3) return "Urgent Warning";
  if (n === 2) return "Monitor Closely";
  return "Stable Advisory";
}

function initials(name = "Responder") {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "R";
}

function appendConsoleLine(rawLog, container) {
  if (!container) return;
  const line = document.createElement("div");
  line.className = "console-line";
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const firstColon = rawLog.indexOf(":");
  const agent = firstColon >= 0 ? rawLog.slice(0, firstColon + 1) : "SYSTEM:";
  const message = firstColon >= 0 ? rawLog.slice(firstColon + 1) : rawLog;
  line.innerHTML = `<span class="console-time">[${time}]</span> <span class="console-agent">${escapeHtml(agent)}</span> ${escapeHtml(message)}`;
  container.appendChild(line);
  container.scrollTop = container.scrollHeight;
}

function populateAreas(region) {
  const areaSelect = $("area-select");
  if (!areaSelect || !KNOWN_LOCATIONS[region]) return;
  areaSelect.innerHTML = "";
  Object.keys(KNOWN_LOCATIONS[region]).forEach((area) => {
    const option = document.createElement("option");
    option.value = area;
    option.textContent = area;
    areaSelect.appendChild(option);
  });
}

function locationCoords(region, area) {
  return KNOWN_LOCATIONS[region]?.[area] || null;
}

function setMap(region, area) {
  const frame = $("map-frame");
  if (!frame) return;
  let lat = $("lat-input")?.value;
  let lng = $("lng-input")?.value;
  const coords = locationCoords(region, area);
  if ((!lat || !lng) && coords) {
    lat = coords[0];
    lng = coords[1];
  }
  currentLat = lat ? Number(lat) : null;
  currentLng = lng ? Number(lng) : null;

  if (activeMapView === "street") {
    loadStreetView();
    return;
  }

  const params = new URLSearchParams({ region, area });
  if (lat && lng) {
    params.set("lat", lat);
    params.set("lng", lng);
  }
  frame.innerHTML = `<iframe title="Haalat operations map" src="/api/map?${params.toString()}"></iframe>`;
}

function loadStreetView() {
  const frame = $("map-frame");
  if (!frame) return;
  if (!currentLat || !currentLng) {
    frame.innerHTML = `<div style="height:100%;display:grid;place-items:center;color:var(--muted);padding:24px;text-align:center;">Select or detect a covered location to initialize Street View.</div>`;
    return;
  }
  const link = `https://www.google.com/maps?layer=c&cbll=${currentLat},${currentLng}`;
  if (hasValidMapsKey) {
    frame.innerHTML = `<iframe title="Google Street View" src="https://www.google.com/maps/embed/v1/streetview?key=${mapsApiKey}&location=${currentLat},${currentLng}"></iframe>`;
  } else {
    frame.innerHTML = `
      <div style="height:100%;display:grid;place-items:center;padding:24px;text-align:center;background:#080808;">
        <div>
          <div class="badge red">Street View Link Ready</div>
          <p style="color:var(--muted);line-height:1.6;">Google embed needs <code>GOOGLE_MAPS_API_KEY</code>. The operations map still works through Folium tiles.</p>
          <a class="secondary-cta" href="${link}" target="_blank" rel="noreferrer"><i class="fa-solid fa-location-arrow"></i> Open Google Maps</a>
        </div>
      </div>`;
  }
}

function updateLocationBadge(message, state = "verified") {
  const badge = $("location-badge");
  if (!badge) return;
  badge.className = `location-badge active ${state}`;
  badge.textContent = message;
}

function verifyCoordinates(lat, lng) {
  const inKarachi = lat >= 24.7 && lat <= 25.25 && lng >= 66.7 && lng <= 67.35;
  const inIslamabadRawalpindi = lat >= 33.45 && lat <= 33.8 && lng >= 72.8 && lng <= 73.25;
  if (!inKarachi && !inIslamabadRawalpindi) {
    updateLocationBadge(`Outside active coverage: ${lat.toFixed(4)}, ${lng.toFixed(4)}. Use manual override or call local emergency services.`, "error");
    return;
  }
  const regions = inKarachi ? ["karachi"] : ["islamabad", "rawalpindi"];
  let best = { region: regions[0], area: "", distance: Infinity };
  regions.forEach((region) => {
    Object.entries(KNOWN_LOCATIONS[region]).forEach(([area, coords]) => {
      const d = Math.hypot(lat - coords[0], lng - coords[1]);
      if (d < best.distance) best = { region, area, distance: d };
    });
  });
  $("region-select").value = best.region;
  populateAreas(best.region);
  $("area-select").value = best.area;
  updateLocationBadge(`Verified and routed to ${best.area}, ${best.region.toUpperCase()}.`, "verified");
  setMap(best.region, best.area);
}

async function fetchConfig() {
  try {
    const response = await fetch("/api/config");
    const data = await response.json();
    mapsApiKey = data.google_maps_api_key || "";
    hasValidMapsKey = Boolean(data.is_valid_key);
  } catch (error) {
    console.warn("Config unavailable", error);
  }
}

async function uploadAudio(blob) {
  const form = new FormData();
  const extension = blob.type.includes("webm") ? "webm" : blob.type.includes("mp4") ? "mp4" : "wav";
  form.append("file", blob, `recording.${extension}`);
  const response = await fetch("/api/upload-audio", { method: "POST", body: form });
  if (!response.ok) throw new Error("Audio upload failed");
  return response.json();
}

function startVoiceMeter(stream) {
  const meter = $("voice-monitor");
  if (!meter) return;
  const bars = Array.from(meter.querySelectorAll("span"));
  meter.classList.add("active");

  try {
    voiceAudioContext = new (window.AudioContext || window.webkitAudioContext)();
    const analyser = voiceAudioContext.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.72;
    const source = voiceAudioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    const data = new Uint8Array(analyser.frequencyBinCount);

    const tick = () => {
      analyser.getByteFrequencyData(data);
      const bucketSize = Math.max(1, Math.floor(data.length / bars.length));
      let total = 0;
      bars.forEach((bar, index) => {
        const start = index * bucketSize;
        const bucket = data.slice(start, start + bucketSize);
        const level = bucket.reduce((sum, value) => sum + value, 0) / Math.max(1, bucket.length);
        total += level;
        const height = Math.max(7, Math.min(38, 7 + (level / 255) * 42));
        bar.style.height = `${height}px`;
      });
      meter.classList.toggle("hot", total / bars.length > 88);
      voiceMeterFrame = requestAnimationFrame(tick);
    };
    tick();
  } catch (error) {
    meter.classList.add("active");
    bars.forEach((bar, index) => {
      bar.style.animation = `metronome ${0.5 + index * 0.03}s ease-in-out infinite`;
    });
  }
}

function stopVoiceMeter() {
  const meter = $("voice-monitor");
  if (voiceMeterFrame) cancelAnimationFrame(voiceMeterFrame);
  voiceMeterFrame = null;
  if (voiceAudioContext) {
    voiceAudioContext.close().catch(() => {});
  }
  voiceAudioContext = null;
  if (activeMicStream) {
    activeMicStream.getTracks().forEach((track) => track.stop());
  }
  activeMicStream = null;
  if (meter) {
    meter.classList.remove("active", "hot");
    meter.querySelectorAll("span").forEach((bar) => {
      bar.style.height = "";
      bar.style.animation = "";
    });
  }
}

async function streamReport(requestBody) {
  const response = await fetch("/api/report-stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  if (!response.ok || !response.body) throw new Error(`Report failed: ${response.status}`);

  const terminal = $("telemetry");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalPayload = null;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.trim()) continue;
      const event = JSON.parse(line);
      if (event.event === "telemetry") appendConsoleLine(event.message, terminal);
      if (event.event === "result") finalPayload = event.payload;
    }
  }
  if (buffer.trim()) {
    const event = JSON.parse(buffer);
    if (event.event === "telemetry") appendConsoleLine(event.message, terminal);
    if (event.event === "result") finalPayload = event.payload;
  }
  if (!finalPayload) throw new Error("No final payload returned");
  return finalPayload;
}

function renderDispatch(payload) {
  const resultPanel = $("result-panel");
  const sev = Number(payload.severity || 1);
  const tone = severityTone(sev);
  resultPanel.hidden = false;

  $("severity-card").className = `severity-card sev-${sev}`;
  $("severity-score").textContent = sev;
  $("severity-label").textContent = severityLabel(sev);
  $("classification").textContent = payload.type || "General Emergency";
  $("reasoning").textContent = payload.reasoning || payload.description || "Emergency classified and routed.";

  const service = payload.nearest_service || {};
  $("service-name").textContent = service.name || "Nearest emergency service";
  $("service-distance").textContent = `${service.distance_km || "---"} km`;
  $("service-phone").textContent = service.phone || "---";
  $("service-call").href = `tel:${service.phone || ""}`;

  const volunteer = payload.nearest_volunteer || {};
  $("volunteer-name").textContent = volunteer.name || "Nearest trained responder";
  $("volunteer-distance").textContent = `${volunteer.distance_km || "---"} km`;
  $("volunteer-skills").textContent = volunteer.skills || "First Aid";
  $("volunteer-call").href = `tel:${volunteer.phone || ""}`;
  $("volunteer-avatar").textContent = initials(volunteer.name);

  renderInstructionVisual(payload.instruction_visual, tone);
  renderTimeline(payload.lifecycle || []);
  renderRiskMemory(payload.risk_memory);
  renderCoach(payload);
  renderMassEvent(payload);

  document.body.classList.toggle("critical-mode", sev >= 4);
  loadIncidentHistory();
  loadResponderDashboard();
}

function renderInstructionVisual(visual, tone) {
  const frame = $("instruction-frame");
  const title = $("instruction-title");
  const img = $("instruction-img");
  if (!frame || !img || !visual) return;
  frame.className = `instruction-frame ${tone === "red" ? "critical" : tone === "green" ? "safe" : "warning"}`;
  title.textContent = visual.label || "Emergency Instruction Loop";
  img.alt = visual.alt || title.textContent;
  img.src = `${visual.gif_url || visual.url || "/instruction-assets/default-radar-alert.svg"}?v=${Date.now()}`;
}

function renderTimeline(timeline) {
  const box = $("timeline");
  if (!box) return;
  box.innerHTML = (timeline.length ? timeline : [{ label: "Standby", detail: "Awaiting report." }])
    .slice(0, 6)
    .map((step) => `
      <div class="timeline-step">
        <strong>${escapeHtml(step.label || "Status")}</strong>
        <span>${escapeHtml(step.detail || "")}</span>
        <span>${escapeHtml(step.time || "")}</span>
      </div>`)
    .join("");
}

function renderRiskMemory(memory) {
  const box = $("risk-memory");
  if (!box) return;
  if (!memory) {
    box.innerHTML = `<p class="reasoning">No pattern memory available yet.</p>`;
    return;
  }
  const tone = memory.risk_level === "high" ? "red" : memory.risk_level === "medium" ? "amber" : "green";
  box.innerHTML = `
    <span class="badge ${tone}">${escapeHtml(memory.risk_level || "watch")}</span>
    <p class="reasoning" style="margin-top:10px;">${escapeHtml(memory.summary || "City memory scan complete.")}</p>`;
}

function renderCoach(payload) {
  const coach = $("coach-panel");
  if (!coach) return;
  const severity = Number(payload.severity || 0);
  if (severity < 4) {
    coach.classList.remove("active");
    return;
  }
  const type = String(payload.type || "").toLowerCase();
  const isCardiac = type.includes("cardiac") || type.includes("heart");
  $("coach-step").textContent = isCardiac ? "01" : "01";
  $("coach-copy").textContent = firstAidHeadline(payload.first_aid_steps, isCardiac);
  $("coach-progress").textContent = isCardiac ? "Step 1 of 5 | 100-120 compressions per minute" : "Step 1 of 4 | Keep caller calm and follow prompts";
  $("metronome-label").textContent = isCardiac ? "110 BPM" : "LIVE";
  coach.classList.add("active");
}

function firstAidHeadline(text = "", cardiac = false) {
  if (cardiac) return "Start hard, fast chest compressions in the center of the chest. Let the chest fully rise between pushes.";
  const clean = String(text).replace(/\s+/g, " ").trim();
  return clean ? clean.split(/[.۔]/)[0].slice(0, 180) : "Move the person away from danger, call emergency services, and follow the next safest action.";
}

function renderMassEvent(payload) {
  const banner = $("mass-banner");
  if (!banner) return;
  if (!payload.is_mass_event) {
    banner.classList.remove("active");
    return;
  }
  $("sitrep-doc").textContent = payload.sitrep || "Civil Defense report generated and queued.";
  banner.classList.add("active");
}

async function loadIncidentHistory() {
  const table = $("incident-rows");
  const trend = $("trend-bars");
  if (!table && !trend) return;
  try {
    const response = await fetch("/api/incidents");
    const incidents = await response.json();
    if (table) {
      table.innerHTML = incidents.length
        ? incidents.slice().reverse().slice(0, 8).map((inc) => {
            const sev = Number(inc.severity || 1);
            const tone = severityTone(sev);
            return `<tr>
              <td>${escapeHtml(inc.time || "Live")}</td>
              <td>${escapeHtml(inc.area || "Unknown")}</td>
              <td>${escapeHtml(inc.type || "Emergency")}</td>
              <td><span class="badge ${tone}">S${sev}</span></td>
            </tr>`;
          }).join("")
        : `<tr><td colspan="4">No city-memory incidents logged yet.</td></tr>`;
    }
    if (trend) renderTrends(incidents, trend);
    updateStats(incidents);
  } catch (error) {
    console.warn("Incident history unavailable", error);
  }
}

function renderTrends(incidents, trend) {
  const counts = {};
  incidents.forEach((inc) => {
    const area = (inc.area || "Unknown").split(",")[0].trim();
    counts[area] = (counts[area] || 0) + 1;
  });
  const rows = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 7);
  const max = Math.max(1, ...rows.map(([, count]) => count));
  trend.innerHTML = rows.length
    ? rows.map(([area, count]) => `
      <div class="trend-row">
        <span>${escapeHtml(area)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${Math.max(8, (count / max) * 100)}%"></div></div>
        <strong>${count}</strong>
      </div>`).join("")
    : `<p class="reasoning">City Memory is waiting for live incidents.</p>`;
}

function updateStats(incidents) {
  const count = $("stat-incidents");
  const critical = $("stat-critical");
  const mass = $("stat-memory");
  if (count) count.textContent = incidents.length;
  if (critical) critical.textContent = incidents.filter((i) => Number(i.severity || 0) >= 4).length;
  if (mass) mass.textContent = new Set(incidents.map((i) => (i.area || "").split(",")[0].trim()).filter(Boolean)).size;
}

async function loadResponderDashboard() {
  try {
    const [volRes, alertRes] = await Promise.all([
      fetch("/api/admin/volunteers"),
      fetch("/api/admin/alerts").catch(() => ({ ok: false, json: async () => [] })),
    ]);
    const volunteers = await volRes.json();
    const alerts = alertRes.ok ? await alertRes.json() : [];
    renderRoster(volunteers);
    renderAlerts(alerts);
    const statVol = $("stat-volunteers");
    if (statVol) statVol.textContent = `${volunteers.filter((v) => v.availability === "available").length}/${volunteers.length}`;
  } catch (error) {
    console.warn("Responder dashboard unavailable", error);
  }
}

function renderRoster(volunteers) {
  const roster = $("volunteer-roster");
  if (!roster) return;
  roster.innerHTML = volunteers.map((vol) => {
    const available = vol.availability === "available";
    return `
      <div class="roster-item">
        <div class="avatar">${initials(vol.name)}</div>
        <div>
          <div class="roster-name">${escapeHtml(vol.name)}</div>
          <div style="color:var(--muted);font-size:.78rem;">${escapeHtml(vol.area)} | ${escapeHtml((vol.region || "").toUpperCase())} | ${vol.response_time_minutes || "--"} min</div>
          <div class="skill-tags">${(vol.skills || []).slice(0, 4).map((skill) => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join("")}</div>
        </div>
        <span class="badge ${available ? "green" : "amber"}">${available ? "Available" : "On Call"}</span>
      </div>`;
  }).join("");
}

function renderAlerts(alerts) {
  const table = $("alert-rows");
  if (!table) return;
  table.innerHTML = alerts.length
    ? alerts.slice().reverse().slice(0, 8).map((alert) => {
        const sev = Number(alert.severity || 1);
        return `<tr>
          <td>${escapeHtml(alert.id || "Alert")}</td>
          <td>${escapeHtml(alert.emergency_type || "Emergency")}<br><span style="color:var(--muted);">${escapeHtml(alert.area || "")}</span></td>
          <td>${escapeHtml(alert.volunteer_name || "Responder")}</td>
          <td><span class="badge ${severityTone(sev)}">${escapeHtml((alert.status || "alerted").replace("_", " "))}</span></td>
          <td class="admin-actions">
            <button class="mini-btn" data-alert="${escapeHtml(alert.id)}" data-status="accepted">Accept</button>
            <button class="mini-btn" data-alert="${escapeHtml(alert.id)}" data-status="en_route">En Route</button>
            <button class="mini-btn" data-alert="${escapeHtml(alert.id)}" data-status="arrived">Arrived</button>
            <button class="mini-btn danger" data-alert="${escapeHtml(alert.id)}" data-status="resolved">Resolve</button>
          </td>
        </tr>`;
      }).join("")
    : `<tr><td colspan="5">No active volunteer dispatches yet.</td></tr>`;
}

async function updateAlertStatus(alertId, status) {
  await fetch("/api/admin/update-alert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ alert_id: alertId, status }),
  });
  loadResponderDashboard();
}

function bindCoreUi() {
  document.querySelectorAll("[data-view-target]").forEach((tab) => {
    tab.addEventListener("click", (event) => {
      event.preventDefault();
      activateView(tab.dataset.viewTarget);
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  document.querySelectorAll("[data-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      activateView(button.dataset.jump);
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  $("heartbeat-slot")?.insertAdjacentHTML("beforeend", heartbeatSvg(false));
  $("top-heartbeat")?.insertAdjacentHTML("beforeend", heartbeatSvg(true));

  const region = $("region-select");
  const area = $("area-select");
  if (region && area) {
    populateAreas(region.value || "karachi");
    region.addEventListener("change", () => {
      populateAreas(region.value);
      setMap(region.value, area.value);
    });
    area.addEventListener("change", () => {
      $("lat-input").value = "";
      $("lng-input").value = "";
      setMap(region.value, area.value);
    });
    setMap(region.value, area.value);
  }

  $("detect-btn")?.addEventListener("click", () => {
    const frame = $("map-frame");
    frame?.classList.add("scanning");
    if (!navigator.geolocation) {
      frame?.classList.remove("scanning");
      updateLocationBadge("Browser geolocation is unavailable. Use manual sector selection.", "error");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        frame?.classList.remove("scanning");
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        $("lat-input").value = lat;
        $("lng-input").value = lng;
        verifyCoordinates(lat, lng);
      },
      () => {
        frame?.classList.remove("scanning");
        updateLocationBadge("Location permission denied or timed out. Manual selection is ready.", "error");
      },
      { enableHighAccuracy: true, timeout: 8000 },
    );
  });

  $("record-btn")?.addEventListener("click", async () => {
    const micStatus = $("mic-status");
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      $("record-btn").classList.remove("recording");
      micStatus.textContent = "Encoding and translating voice report...";
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      activeMicStream = stream;
      startVoiceMeter(stream);
      const preferredMime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "";
      mediaRecorder = preferredMime ? new MediaRecorder(stream, { mimeType: preferredMime }) : new MediaRecorder(stream);
      audioChunks = [];
      mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
      mediaRecorder.onstop = async () => {
        stopVoiceMeter();
        const blob = new Blob(audioChunks, { type: mediaRecorder.mimeType || "audio/wav" });
        try {
          const data = await uploadAudio(blob);
          const input = $("report-input");
          const transcription = (data.transcription || "").trim();
          if (data.has_transcription && transcription) {
            $("audio-path-input").value = "";
            input.value = transcription;
            setTextDirection(input, transcription);
            micStatus.textContent = "Voice translated into the emergency text chat.";
            appendConsoleLine(`[VOICE ROUTER]: Audio translated and inserted into report input.`, $("telemetry"));
          } else {
            $("audio-path-input").value = data.file_path || "";
            input.value = "[AUDIO REPORT TRANSMITTED]";
            micStatus.textContent = "Voice saved. Translation unavailable, dispatch will process audio.";
            appendConsoleLine(`[VOICE ROUTER]: Audio saved. Translation will be attempted during dispatch.`, $("telemetry"));
          }
          input.focus();
        } catch {
          micStatus.textContent = "Audio upload failed";
        }
      };
      mediaRecorder.start();
      $("record-btn").classList.add("recording");
      micStatus.textContent = "Recording. Press again to stop.";
    } catch {
      stopVoiceMeter();
      micStatus.textContent = "Microphone permission blocked.";
    }
  });

  $("report-input")?.addEventListener("input", (event) => setTextDirection(event.target, event.target.value));

  $("map-mode-map")?.addEventListener("click", () => {
    activeMapView = "map";
    $("map-mode-map").classList.add("active");
    $("map-mode-street").classList.remove("active");
    setMap($("region-select").value, $("area-select").value);
  });
  $("map-mode-street")?.addEventListener("click", () => {
    activeMapView = "street";
    $("map-mode-street").classList.add("active");
    $("map-mode-map").classList.remove("active");
    setMap($("region-select").value, $("area-select").value);
  });

  $("submit-report")?.addEventListener("click", async () => {
    const input = $("report-input");
    const message = input.value.trim();
    const audioPath = $("audio-path-input").value;
    if (!message && !audioPath) {
      input.focus();
      return;
    }
    const button = $("submit-report");
    const terminal = $("telemetry");
    terminal.innerHTML = "";
    appendConsoleLine("[MATRIX BOOT]: Opening Haalat emergency intelligence stream...", terminal);
    button.disabled = true;
    button.innerHTML = `<i class="fa-solid fa-wave-square"></i> Processing`;
    $("map-frame")?.classList.add("scanning");
    try {
      const payload = await streamReport({
        message,
        audio_path: audioPath || null,
        region: $("region-select").value,
        area: $("area-select").value,
        lat: $("lat-input").value ? Number($("lat-input").value) : null,
        lng: $("lng-input").value ? Number($("lng-input").value) : null,
      });
      renderDispatch(payload);
      input.value = "";
      $("audio-path-input").value = "";
      $("mic-status").textContent = "Ready";
    } catch (error) {
      appendConsoleLine(`[ERROR]: ${error.message}`, terminal);
    } finally {
      $("map-frame")?.classList.remove("scanning");
      button.disabled = false;
      button.innerHTML = `<i class="fa-solid fa-bolt"></i> Dispatch Report`;
    }
  });

  document.addEventListener("click", (event) => {
    const action = event.target.closest("[data-alert]");
    if (action) updateAlertStatus(action.dataset.alert, action.dataset.status);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  bindCoreUi();
  fetchConfig();
  loadIncidentHistory();
  loadResponderDashboard();
  setInterval(loadIncidentHistory, 8000);
  setInterval(loadResponderDashboard, 8000);
});
