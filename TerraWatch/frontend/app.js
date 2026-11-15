const API_BASE = window.TERRAWATCH_API_BASE || (() => {
  const { protocol, hostname, port, origin } = window.location;
  if (protocol === "file:" || (port && port !== "8000")) {
    return `${protocol === "https:" ? "https:" : "http:"}//${hostname || "127.0.0.1"}:8000`;
  }
  return origin;
})();

const amTranslations = {
  nav_overview: "አጠቃላይ እይታ",
  nav_map: "የመከታተያ ካርታ",
  nav_analysis: "ትንታኔ",
  nav_method: "የአሰራር ዘዴ",
  nav_about: "ስለ እኛ",
  demo_pill: "የቀጥታ API",
  hero_eyebrow: "የምድር ምልከታ · የከተማ ጽናት",
  hero_title: "ከከተማዋ በታች<br>ያለውን መሬት ይመልከቱ።",
  hero_copy: "የአዲስ አበባን የራዳር መፈናቀል፣ የመሬት መስመጥ ቡድኖችን እና ተጋላጭ መዋቅሮችን ያስሱ። የኋላ ገጹን ትንታኔ ለማየት በካርታው ላይ ቦታ ይምረጡ።",
  hero_city: "አዲስ አበባ፣ ኢትዮጵያ",
  sec1_title: "የክትትል አጠቃላይ እይታ",
  sec1_sub: "ከTerraWatch የኋላ ገጽ የተመለሱ የቀጥታ መለኪያዎች",
  m1_label: "በጣም አሉታዊ የመዋቅር መፈናቀል",
  m2_label: "በስጋት ውስጥ ያሉ መዋቅሮች",
  m3_label: "የተቀመጡ የምልከታ ዙሮች",
  m4_label: "የML የመሬት መስመጥ ቡድኖች",
  sec2_title: "ጂኦስፓሻል ክትትል",
  sec2_sub: "የራዳር መፈናቀልን፣ የሞዴል ቡድኖችን እና ተጋላጭ መዋቅሮችን ያስሱ",
  map_title: "አዲስ አበባ · የክትትል ካርታ",
  map_sub: "OPENSTREETMAP · የራዳር ንብርብር እና የሞዴል ውጤቶች",
  filter_all: "ሁሉም መዋቅሮች",
  filter_high: "ከፍተኛ ስጋት",
  filter_med: "መካከለኛ ስጋት",
  filter_low: "ሌሎች የስጋት ደረጃዎች",
  btn_reset: "ካርታውን ዳግም አስጀምር",
  btn_alert: "የML ቡድኖች: በርቷል",
  btn_alert_off: "የML ቡድኖች: ጠፍቷል",
  layers_label: "የካርታ ንብርብሮች",
  layer_sites: "ተጋላጭ መዋቅሮች",
  layer_insar: "የራዳር መፈናቀል ንብርብር",
  layer_base: "የከተማ መሠረታዊ ካርታ",
  selected_label: "የተመረጠ የካርታ ቦታ",
  vuln_label: "የML የቦታ ልዩነት መለኪያ",
  sec3_title: "የመፈናቀል እና የስጋት ትንታኔ",
  sec3_sub: "የኋላ ገጽ ድምር ምልከታዎች፣ የመዋቅር መፈናቀል እና የስጋት ምደባ",
  chart_title: "የድምር መፈናቀል የጊዜ ተከታታይ",
  chart_sub: "የኋላ ገጽ ምልከታዎች · ሴንቲሜትር",
  table_title: "ከፍተኛ ቅድሚያ ያላቸው መዋቅሮች",
  table_sub: "የኋላ ገጽ መፈናቀል እና የስጋት ምደባ",
  th_site: "መዋቅር",
  th_val: "መፈናቀል (ሴ.ሜ)",
  th_vuln: "የስጋት ደረጃ",
  sec4_title: "ስርዓቱ እንዴት እንደሚሰራ",
  sec4_sub: "የተጠቃሚ ገጹ ከሳይንሳዊ የመረጃ ሂደት ጋር ተለይቶ ይሰራል",
  m_card1_t: "1. የSAR ምልከታዎች",
  m_card1_p: "ከተለየ የሳተላይት ምንጭ ተስማሚ የራዳር ምስሎችን እና መረጃዎችን ያግኙ። ቀን፣ ጂኦሜትሪ እና የሂደት ዝርዝሮችን ይመዝግቡ።",
  m_card2_t: "2. የInSAR ሂደት",
  m_card2_p: "የመሬት መፈናቀልን ለመገመት የራዳር ምልከታዎችን ያቀናብሩ። የcoherence፣ የከባቢ አየር ተጽዕኖ፣ የማጣቀሻ ነጥቦችን እና እርግጠኝነትን ያረጋግጡ።",
  m_card3_t: "3. የድር ማሳያ",
  m_card3_p: "የጂኦስፓሻል ውጤቶችን በPython የኋላ ገጽ ያቅርቡ፣ እና በካርታ፣ ግራፍ እና ግልጽ መረጃ በዚህ ገጽ ያሳዩ።"
};

function setLanguage(lang) {
  const language = lang === "am" ? "am" : "en";
  localStorage.setItem("terrawatch_lang", language);
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (key === "hazard_msg") return;
    if (!element.dataset.defaultText) element.dataset.defaultText = element.innerHTML;
    element.innerHTML = language === "am" && amTranslations[key]
      ? amTranslations[key]
      : element.dataset.defaultText;
  });
  const button = document.getElementById("langToggle");
  if (button) {
    button.textContent = language === "am" ? "🌐 English" : "🌐 አማርኛ";
    button.setAttribute("aria-label", language === "am" ? "Switch to English" : "Switch to Amharic");
  }
}

const apiRequest = async (path, options = {}) => {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { Accept: "application/json", ...options.headers }
    });
  } catch (error) {
    throw new Error(`Cannot reach TerraWatch API at ${API_BASE}: ${error.message}`);
  }

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : null;
  if (!response.ok) {
    throw new Error(body?.detail || `API request failed (${response.status} ${response.statusText}).`);
  }
  if (!body) throw new Error("The API returned a response that was not JSON.");
  return body;
};

const state = {
  structures: null,
  clusters: [],
  selected: null,
  analysis: null,
  map: null,
  baseLayer: null,
  overlay: null,
  structuresLayer: null,
  subcitiesLayer: null,
  clustersLayer: null,
  chart: null,
  timeseries: null,
  hazardEnabled: true
};
try {
  state.selected = JSON.parse(localStorage.getItem("terrawatch_location") || "null");
} catch {
  state.selected = null;
}

const setText = (id, value) => {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
};

const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
})[char]);

const showToast = (message) => {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 3200);
};

const statusElement = (() => {
  const pill = document.querySelector(".demo-pill");
  if (!pill) return null;
  const status = document.createElement("span");
  status.id = "apiStatus";
  status.className = "api-status";
  status.setAttribute("role", "status");
  status.textContent = "CONNECTING";
  pill.replaceWith(status);
  return status;
})();

const setApiStatus = (stateName, message) => {
  if (statusElement) {
    statusElement.dataset.state = stateName;
    statusElement.textContent = stateName === "online" ? "LIVE API" : stateName === "offline" ? "API OFFLINE" : "CONNECTING";
    statusElement.title = message || "";
  }
  const syncStatus = document.getElementById("syncStatus");
  if (syncStatus && stateName === "offline" && message) syncStatus.textContent = message;
};

const selectedLocation = () => state.selected || { lat: 9.015, lon: 38.755 };

window.terraWatch = {
  apiBase: API_BASE,
  request: apiRequest,
  getSelectedLocation: selectedLocation,
  analyzeLocation: (lat, lon) => analyzeLocation(lat, lon),
  getSelectedAnalysis: () => state.analysis,
  getSelectedTimeseries: () => state.timeseries,
  getStructures: () => state.structures,
  getClusters: () => state.clusters
};

function updateHazardBanner() {
  const banner = document.getElementById("hazardBanner");
  if (!banner) return;
  const badge = banner.querySelector(".hazard-badge");
  const text = banner.querySelector(".hazard-text");
  if (badge) badge.textContent = "SUBSIDENCE CLUSTERS";
  if (text) {
    const count = state.clusters.length;
    const peak = state.clusters[0];
    text.textContent = count
      ? `${count} spatial cluster${count === 1 ? "" : "s"} identified by the backend model. Strongest cluster: ${peak.peak_sinking_cm} cm at ${peak.center_lat}°N, ${peak.center_lon}°E.`
      : "The backend currently reports no spatial subsidence clusters.";
  }
  banner.classList.toggle("visible", state.hazardEnabled && state.clusters.length > 0);
  const toggle = document.getElementById("toggleHazardBtn");
  if (toggle) {
    toggle.textContent = `ML clusters: ${state.hazardEnabled ? "ON" : "OFF"}`;
    toggle.classList.toggle("alert-active", state.hazardEnabled);
  }
}

function updateOverview() {
  const structures = state.structures?.top_priority_list || [];
  const values = structures
    .filter((item) => item.vertical_cm != null)
    .map((item) => Number(item.vertical_cm))
    .filter(Number.isFinite);
  const strongest = values.length ? Math.min(...values) : null;
  const sync = window.terraWatch.syncStatus;
  setText("overviewMaxDisplacement", strongest === null ? "—" : `${strongest.toFixed(2)} cm`);
  setText("overviewStructureCount", state.structures?.at_risk_structures?.features?.length ?? "—");
  setText("overviewPassCount", sync?.total_passes_stored ?? "—");
  setText("overviewClusterCount", state.clusters.length);
  setText("overviewMaxFoot", strongest === null ? "No structure displacement returned" : "Most negative value in the backend priority list");
  setText("overviewStructuresFoot", "Features returned by the structures API");
  setText("overviewPassFoot", sync?.last_checked ? `Last checked ${new Date(sync.last_checked).toLocaleString()}` : "Stored observation passes");
  setText("overviewClustersFoot", "Spatial clusters returned by the ML service");
}

function updateSyncStatus(payload) {
  window.terraWatch.syncStatus = payload;
  const lastChecked = payload.last_checked ? new Date(payload.last_checked).toLocaleString() : "not yet checked";
  const nextSync = payload.next_scheduled_sync ? new Date(payload.next_scheduled_sync).toLocaleString() : "not scheduled";
  const mode = payload.streaming_mode || "standard";
  const label = `Last check: ${lastChecked} · ${payload.total_passes_stored} pass(es) stored · ${mode} · next: ${nextSync}`;
  setText("syncStatus", label);
  updateOverview();
}

function riskColor(level = "") {
  const normalized = level.toLowerCase();
  if (normalized.includes("high")) return "#ff6e84";
  if (normalized.includes("moderate")) return "#f7be68";
  return "#45e0a3";
}

function passesRiskFilter(feature, filter) {
  if (filter === "all") return true;
  const risk = String(feature.properties?.risk_level || "").toLowerCase();
  return filter === "high" ? risk.includes("high")
    : filter === "medium" ? risk.includes("moderate")
      : !risk.includes("high") && !risk.includes("moderate");
}

function refreshMapLayers() {
  if (!state.map) return;
  const showStructures = document.getElementById("sitesToggle")?.checked ?? true;
  if (state.structuresLayer) {
    if (showStructures) {
      if (!state.map.hasLayer(state.structuresLayer)) state.structuresLayer.addTo(state.map);
    } else {
      state.map.removeLayer(state.structuresLayer);
    }
  }
  if (state.overlay) {
    const showOverlay = document.getElementById("insarToggle")?.checked ?? true;
    if (showOverlay && !state.map.hasLayer(state.overlay)) state.overlay.addTo(state.map);
    if (!showOverlay && state.map.hasLayer(state.overlay)) state.map.removeLayer(state.overlay);
  }
  if (state.subcitiesLayer && !state.map.hasLayer(state.subcitiesLayer)) state.subcitiesLayer.addTo(state.map);
  if (state.clustersLayer) {
    if (state.hazardEnabled && !state.map.hasLayer(state.clustersLayer)) state.clustersLayer.addTo(state.map);
    if (!state.hazardEnabled && state.map.hasLayer(state.clustersLayer)) state.map.removeLayer(state.clustersLayer);
  }
}

function renderStructures(payload) {
  state.structures = payload;
  const table = document.getElementById("siteTable");
  if (table) {
    table.replaceChildren();
    const rows = payload.top_priority_list || [];
    if (!rows.length) {
      table.innerHTML = '<tr><td colspan="3">No at-risk structures were returned.</td></tr>';
    } else {
      for (const item of rows) {
        const row = document.createElement("tr");
        row.dataset.lat = item.lat;
        row.dataset.lon = item.lon;
        const name = document.createElement("td");
        name.textContent = item.display_name || item.structure_type || "Structure";
        const displacement = document.createElement("td");
        displacement.textContent = Number.isFinite(Number(item.vertical_cm)) ? `${Number(item.vertical_cm).toFixed(2)} cm` : "—";
        const risk = document.createElement("td");
        const pill = document.createElement("span");
        pill.className = `risk-pill ${String(item.risk_level || "").toLowerCase().includes("high") ? "critical" : String(item.risk_level || "").toLowerCase().includes("moderate") ? "elevated" : "low"}`;
        pill.textContent = item.risk_level || "Unclassified";
        risk.appendChild(pill);
        row.append(name, displacement, risk);
        table.appendChild(row);
      }
    }
  }

  const selector = document.getElementById("chartSite");
  if (selector) {
    selector.replaceChildren();
    for (const [index, item] of (payload.top_priority_list || []).entries()) {
      const option = document.createElement("option");
      option.value = `${item.lat},${item.lon}`;
      option.textContent = `${index + 1}. ${item.display_name || item.structure_type || "Structure"}`;
      selector.appendChild(option);
    }
  }

  if (state.map && window.L) {
    if (state.structuresLayer) state.map.removeLayer(state.structuresLayer);
    const filter = document.getElementById("siteFilter")?.value || "all";
    state.structuresLayer = L.geoJSON(payload.at_risk_structures, {
      filter: (feature) => passesRiskFilter(feature, filter),
      style: (feature) => ({
        color: riskColor(feature.properties?.risk_level),
        weight: 2,
        opacity: 0.8
      }),
      pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
        radius: 5,
        color: riskColor(feature.properties?.risk_level),
        fillColor: riskColor(feature.properties?.risk_level),
        fillOpacity: 0.8,
        weight: 1
      }),
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const name = escapeHtml(props.display_name || props.structure_type || "Structure");
        const displacement = Number.isFinite(Number(props.vertical_cm)) ? `${Number(props.vertical_cm).toFixed(2)} cm` : "not available";
        layer.bindPopup(`<strong>${name}</strong><br>Vertical displacement: ${displacement}<br>Risk: ${escapeHtml(props.risk_level || "Unclassified")}<br>Click the feature to analyze its location.`);
        layer.on("click", (event) => {
          L.DomEvent.stopPropagation(event);
          analyzeLocation(event.latlng.lat, event.latlng.lng);
        });
      }
    });
    if (document.getElementById("sitesToggle")?.checked ?? true) state.structuresLayer.addTo(state.map);
  }
  updateOverview();
}

function renderClusters(payload) {
  state.clusters = payload.subsidence_clusters || [];
  if (state.map && window.L) {
    if (state.clustersLayer) state.map.removeLayer(state.clustersLayer);
    state.clustersLayer = L.layerGroup(state.clusters.map((cluster) => {
      const circle = L.circle([cluster.center_lat, cluster.center_lon], {
        radius: Math.max(100, Math.sqrt(Number(cluster.area_km2) * 1_000_000 / Math.PI) || 100),
        color: "#ff6e84",
        weight: 2,
        fillColor: "#ff6e84",
        fillOpacity: 0.15
      });
      circle.bindPopup(`<strong>ML cluster ${cluster.cluster_id}</strong><br>Peak sinking: ${cluster.peak_sinking_cm} cm<br>Mean: ${cluster.mean_sinking_cm} cm<br>Pixels: ${cluster.pixel_count} · Area: ${cluster.area_km2} km²`);
      circle.on("click", (event) => {
        L.DomEvent.stopPropagation(event);
        analyzeLocation(event.latlng.lat, event.latlng.lng);
      });
      return circle;
    }));
    if (state.hazardEnabled) state.clustersLayer.addTo(state.map);
  }
  updateHazardBanner();
  updateOverview();
}

function renderOverlay(payload) {
  if (!state.map || !window.L) return;
  if (state.overlay) state.map.removeLayer(state.overlay);
  state.overlay = L.imageOverlay(payload.image_data_url, payload.bounds, { opacity: 0.72, interactive: false });
  if (document.getElementById("insarToggle")?.checked ?? true) state.overlay.addTo(state.map);
  setText("overlayMetadata", `(±${payload.v_limit_cm} cm · ${payload.resolution_m} m)`);
  state.map.fitBounds(payload.bounds);
}

function renderSubcities(payload) {
  const collection = payload.subcities;
  if (!collection?.features?.length || !state.map) return;
  const relevant = {
    ...collection,
    features: collection.features.filter((feature) => {
      const properties = feature.properties || {};
      const isAddisSubcity = Number(properties.admin_level) === 6 &&
        ["Polygon", "MultiPolygon"].includes(feature.geometry?.type);
      return isAddisSubcity &&
        ((properties.mean_vertical_cm != null && Number.isFinite(Number(properties.mean_vertical_cm))) ||
          (properties.hotspot_sinking_cm != null && Number.isFinite(Number(properties.hotspot_sinking_cm))));
    })
  };
  if (state.subcitiesLayer) state.map.removeLayer(state.subcitiesLayer);
  state.subcitiesLayer = L.geoJSON(relevant, {
    style: { color: "#5899ff", weight: 1, opacity: 0.65, fillOpacity: 0.05 },
    onEachFeature: (feature, layer) => {
      const props = feature.properties || {};
      layer.bindPopup(`${escapeHtml(props.name || props["name:en"] || "Subcity")}<br>Mean displacement: ${props.mean_vertical_cm ?? "—"} cm<br>Hotspot: ${props.hotspot_sinking_cm ?? "—"} cm`);
      layer.on("click", (event) => {
        L.DomEvent.stopPropagation(event);
        analyzeLocation(event.latlng.lat, event.latlng.lng);
      });
    }
  }).addTo(state.map);
}

function setSelectedDetails(analysis, lat, lon, series) {
  state.analysis = analysis;
  state.selected = { lat, lon };
  localStorage.setItem("terrawatch_location", JSON.stringify(state.selected));
  const reportButton = document.getElementById("printReportBtn");
  if (reportButton) reportButton.disabled = false;
  setText("siteName", `${lat.toFixed(5)}°N, ${lon.toFixed(5)}°E`);
  setText("siteDescription", analysis.ai_summary || analysis.confidence_level || "No interpretation was returned.");
  setText("siteValue", analysis.exact_80m_cell_cm == null ? "—" : `${analysis.exact_80m_cell_cm.toFixed(2)}`);
  setText("siteUnit", analysis.exact_80m_cell_cm == null ? "cm · no coherent cell" : "cm · 12-day observation");
  setText("vulnScore", analysis.ml_anomaly_score_pct == null ? "N/A" : `${analysis.ml_anomaly_score_pct.toFixed(1)}% anomaly`);
  const fill = document.getElementById("vulnFill");
  if (fill) fill.style.width = `${Math.max(0, Math.min(100, analysis.ml_anomaly_score_pct || 0))}%`;
  setText("vulnInfra", analysis.nearby_structures?.length
    ? `${analysis.nearby_structures.length} exposed structure(s) within 150 m`
    : "No exposed structures returned within 150 m.");
  setText("neighborhoodMean", analysis.neighborhood_mean_cm == null ? "—" : `${analysis.neighborhood_mean_cm.toFixed(2)} cm`);
  setText("analysisUncertainty", analysis.uncertainty_1sigma_cm == null ? "—" : `±${analysis.uncertainty_1sigma_cm.toFixed(2)} cm`);
  setText("annualizedRate", analysis.annualized_rate_cm_yr == null ? "—" : `${analysis.annualized_rate_cm_yr.toFixed(2)} cm/yr`);
  const nearbyList = document.getElementById("nearbyStructures");
  if (nearbyList) {
    nearbyList.replaceChildren();
    if (!analysis.nearby_structures?.length) {
      const item = document.createElement("li");
      item.textContent = "No nearby structures returned.";
      nearbyList.appendChild(item);
    } else {
      for (const structure of analysis.nearby_structures) {
        const item = document.createElement("li");
        item.textContent = `${structure.display_name} (${structure.structure_type}): ${structure.vertical_cm.toFixed(2)} cm · ${structure.risk_level}`;
        nearbyList.appendChild(item);
      }
    }
  }
  const status = document.getElementById("siteStatus");
  if (status) {
    status.textContent = `${analysis.risk_level} · ${analysis.confidence_level}`;
    status.title = analysis.status || "";
  }
  const forecast = document.getElementById("forecastDetails");
  if (forecast) {
    forecast.textContent = analysis.forecast?.length
      ? analysis.forecast.map((point) =>
        `Month ${point.month}: ${point.predicted_cm} cm | 1σ ${point.lower_1s} to ${point.upper_1s} cm | 2σ ${point.lower_2s} to ${point.upper_2s} cm`
      ).join("\n")
      : "Forecast unavailable for this location.";
  }
  window.dispatchEvent(new CustomEvent("terrawatch:location", { detail: { lat, lon, analysis, series } }));
  updateChart(series);
}

async function analyzeLocation(lat, lon) {
  const params = new URLSearchParams({ lat: String(lat), lon: String(lon) });
  state.selected = { lat, lon };
  state.analysis = null;
  localStorage.setItem("terrawatch_location", JSON.stringify(state.selected));
  const reportButton = document.getElementById("printReportBtn");
  if (reportButton) reportButton.disabled = true;
  setText("siteName", `${lat.toFixed(5)}°N, ${lon.toFixed(5)}°E`);
  setText("siteDescription", "Loading backend analysis…");
  try {
    const [analysis, series] = await Promise.all([
      apiRequest(`/api/analyze?${params}`),
      apiRequest(`/api/timeseries?${params}`)
    ]);
    setSelectedDetails(analysis, lat, lon, series);
    setApiStatus("online", `Analysis loaded for ${lat.toFixed(5)}, ${lon.toFixed(5)}.`);
  } catch (error) {
    setText("siteDescription", error.message);
    setText("siteValue", "—");
    setText("siteUnit", "cm · unavailable");
    setText("vulnScore", "—");
    setText("neighborhoodMean", "—");
    setText("analysisUncertainty", "—");
    setText("annualizedRate", "—");
    setText("vulnInfra", "Nearby structures unavailable.");
    setText("siteStatus", "Analysis unavailable");
    setText("forecastDetails", "Forecast unavailable.");
    document.getElementById("nearbyStructures")?.replaceChildren();
    updateChart({ dates: [], cumulative_cm: [] });
    if (reportButton) reportButton.disabled = true;
    window.dispatchEvent(new CustomEvent("terrawatch:location", { detail: { lat, lon, analysis: null } }));
    setApiStatus("offline", error.message);
  }
}

function printLocationReport() {
  const analysis = state.analysis;
  const location = state.selected;
  const report = document.getElementById("printReport");
  if (!analysis || !location || !report) {
    showToast("Select a location and wait for its backend analysis before printing.");
    return;
  }

  const addText = (parent, tag, text, className) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = text;
    parent.appendChild(element);
    return element;
  };
  const format = (value, suffix = "") =>
    value == null || !Number.isFinite(Number(value)) ? "Not available" : `${Number(value).toFixed(2)}${suffix}`;
  const addTable = (headers, rows) => {
    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    headers.forEach((header) => addText(headerRow, "th", header));
    thead.appendChild(headerRow);
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      row.forEach((value) => addText(tr, "td", value));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    report.appendChild(table);
  };

  report.replaceChildren();
  addText(report, "p", "TERRAWATCH · CIVIL ENGINEERING LOCATION REPORT", "report-kicker");
  addText(report, "h1", "Ground displacement screening report");
  addText(report, "p", `Generated ${new Date().toLocaleString()}`, "report-generated");
  addText(report, "h2", "Location and screening result");
  addTable(["Field", "Backend result"], [
    ["Coordinates (WGS 84)", `${location.lat.toFixed(5)}° N, ${location.lon.toFixed(5)}° E`],
    ["Screening classification", analysis.risk_level || "Not classified"],
    ["Confidence", analysis.confidence_level || "Not available"],
    ["Cell displacement (80 m)", format(analysis.exact_80m_cell_cm, " cm")],
    ["Neighborhood mean", format(analysis.neighborhood_mean_cm, " cm")],
    ["Uncertainty (1σ)", format(analysis.uncertainty_1sigma_cm, " cm")],
    ["Annualized rate estimate", format(analysis.annualized_rate_cm_yr, " cm/year")],
    ["ML anomaly score", format(analysis.ml_anomaly_score_pct, "%")]
  ]);
  addText(report, "h2", "Backend interpretation");
  addText(report, "p", analysis.ai_summary || "No interpretation was returned.");

  addText(report, "h2", "Nearby exposed structures (within 150 m)");
  const nearby = analysis.nearby_structures || [];
  addTable(["Structure", "Type", "Displacement", "Risk"], nearby.length
    ? nearby.map((item) => [
      item.display_name || "Structure",
      item.structure_type || "Not specified",
      format(item.vertical_cm, " cm"),
      item.risk_level || "Not classified"
    ])
    : [["No nearby structures returned", "—", "—", "—"]]);

  addText(report, "h2", "Available time-series observations");
  const series = state.timeseries;
  const dates = series?.dates || [];
  const values = series?.cumulative_cm || [];
  addTable(["Date", "Cumulative displacement"], dates.length
    ? dates.map((date, index) => [date, format(values[index], " cm")])
    : [["No observations returned for this location", "—"]]);
  if (dates.length < 2) {
    addText(report, "p", "The returned observation history is too limited to establish a trend.", "report-note");
  }

  addText(report, "h2", "Backend forecast");
  const forecast = analysis.forecast || [];
  addTable(["Month", "Prediction", "1σ interval", "2σ interval"], forecast.length
    ? forecast.map((point) => [
      String(point.month),
      format(point.predicted_cm, " cm"),
      `${format(point.lower_1s)} to ${format(point.upper_1s)} cm`,
      `${format(point.lower_2s)} to ${format(point.upper_2s)} cm`
    ])
    : [["No forecast returned", "—", "—", "—"]]);

  addText(report, "h2", "Use and limitations");
  addText(report, "p", "This report summarizes backend screening outputs for the selected map location; it is not a structural inspection, geotechnical investigation, or engineering certification. Satellite displacement is an indirect measurement and may be affected by coherence, viewing geometry, atmospheric conditions, and reference choices. Annualized rates and forecasts are model-derived and should not be treated as observed long-term trends, especially when only a small number of observation passes are available. Confirm concerning results with qualified field investigation before making engineering or public-safety decisions.");
  addText(report, "p", "Source: TerraWatch backend point-analysis, nearby-structure, time-series, and forecast responses. Coordinates use WGS 84; displacement values are reported in centimetres.", "report-source");

  window.print();
}

function updateChart(series) {
  state.timeseries = series;
  const status = document.getElementById("chartStatus");
  if (!state.chart) {
    if (status) status.textContent = "Loading chart library…";
    return;
  }
  const dates = series?.dates || [];
  const values = series?.cumulative_cm || [];
  state.chart.data.labels = dates;
  state.chart.data.datasets[0].data = values;
  state.chart.update();
  if (status) {
    status.textContent = dates.length
      ? `${dates.length} observation(s) returned by the backend. Values are cumulative cm; no points are interpolated.`
      : "No coherent time-series observations are available at this location.";
  }
}

function initializeChart() {
  const canvas = document.getElementById("displacementChart");
  if (!canvas || !window.Chart) return;
  const context = canvas.getContext("2d");
  const gradient = context.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, "rgba(62, 228, 242, 0.34)");
  gradient.addColorStop(1, "rgba(62, 228, 242, 0)");
  state.chart = new Chart(context, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Backend cumulative displacement",
        data: [],
        borderColor: "#3ee4f2",
        backgroundColor: gradient,
        fill: true,
        tension: 0.25,
        borderWidth: 2.5,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (context) => ` ${context.parsed.y.toFixed(2)} cm` } }
      },
      scales: {
        x: { grid: { color: "rgba(155, 184, 216, 0.08)" }, ticks: { color: "#8ca3be" } },
        y: {
          grid: { color: "rgba(155, 184, 216, 0.1)" },
          ticks: { color: "#8ca3be", callback: (value) => `${value} cm` },
          title: { display: true, text: "Cumulative displacement (cm)", color: "#9eb3cc" }
        }
      }
    }
  });
}

function loadChartLibrary() {
  if (!document.getElementById("displacementChart") || window.Chart) {
    initializeChart();
    if (state.chart && state.timeseries) updateChart(state.timeseries);
    return;
  }
  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js";
  script.onload = () => {
    initializeChart();
    if (state.chart && state.timeseries) updateChart(state.timeseries);
  };
  script.onerror = () => setText("chartStatus", "Chart.js could not be loaded. Backend structure and analysis data are still available.");
  document.head.appendChild(script);
}

function selectChartLocation(value) {
  const [lat, lon] = String(value).split(",").map(Number);
  if (Number.isFinite(lat) && Number.isFinite(lon)) analyzeLocation(lat, lon);
}

function initializeMap() {
  const mapElement = document.getElementById("map");
  if (!mapElement || !window.L) return;
  state.map = L.map(mapElement, { zoomControl: true, scrollWheelZoom: false }).setView([9.015, 38.755], 12);
  state.baseLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(state.map);
  state.map.on("click", (event) => analyzeLocation(event.latlng.lat, event.latlng.lng));
  document.getElementById("siteFilter")?.addEventListener("change", async () => {
    if (state.structures) renderStructures(state.structures);
  });
  document.getElementById("sitesToggle")?.addEventListener("change", refreshMapLayers);
  document.getElementById("insarToggle")?.addEventListener("change", refreshMapLayers);
  document.getElementById("baseToggle")?.addEventListener("change", (event) => {
    if (event.target.checked) state.baseLayer.addTo(state.map);
    else state.map.removeLayer(state.baseLayer);
  });
  document.getElementById("resetMap")?.addEventListener("click", () => {
    state.map.setView([9.015, 38.755], 12);
    const filter = document.getElementById("siteFilter");
    if (filter) filter.value = "all";
    const sites = document.getElementById("sitesToggle");
    const overlay = document.getElementById("insarToggle");
    const base = document.getElementById("baseToggle");
    if (sites) sites.checked = true;
    if (overlay) overlay.checked = true;
    if (base) base.checked = true;
    refreshMapLayers();
  });
  document.getElementById("toggleHazardBtn")?.addEventListener("click", () => {
    state.hazardEnabled = !state.hazardEnabled;
    updateHazardBanner();
    refreshMapLayers();
  });
  document.getElementById("syncNowBtn")?.addEventListener("click", syncNow);
  window.addEventListener("load", () => setTimeout(() => state.map.invalidateSize(), 150));
}

async function syncNow() {
  const button = document.getElementById("syncNowBtn");
  if (button) {
    button.disabled = true;
    button.textContent = "Syncing…";
  }
  try {
    const result = await apiRequest("/api/sync-now", { method: "POST" });
    showToast(result.message || "NISAR sync completed.");
    await loadBackendData();
  } catch (error) {
    setApiStatus("offline", error.message);
    showToast(`Sync failed: ${error.message}`);
  } finally {
    if (button) {
      button.disabled = false;
      button.textContent = "Sync now";
    }
  }
}

async function loadBackendData() {
  const requests = [
    apiRequest("/api/structures").then((payload) => {
      renderStructures(payload);
      renderSubcities(payload);
    }),
    apiRequest("/api/ml-clusters").then(renderClusters),
    apiRequest("/api/sync-status").then(updateSyncStatus)
  ];
  if (state.map) {
    requests.push(apiRequest("/api/overlay").then(renderOverlay));
  }
  const results = await Promise.allSettled(requests);
  const failed = results.filter((result) => result.status === "rejected");
  if (failed.length) {
    const message = failed.map((result) => result.reason.message).join(" ");
    setApiStatus("offline", message);
    if (document.getElementById("siteTable")) {
      const table = document.getElementById("siteTable");
      table.innerHTML = `<tr><td colspan="3">${escapeHtml(message)}</td></tr>`;
    }
  } else {
    setApiStatus("online", "Connected to the TerraWatch backend.");
  }
  updateOverview();
}

function initializeNavigation() {
  const menuToggle = document.getElementById("menuToggle");
  const nav = document.getElementById("navLinks");
  menuToggle?.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menuToggle.setAttribute("aria-expanded", String(open));
  });
  nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => nav.classList.remove("open")));
  const currentPage = document.body.dataset.page;
  const pageToHref = { overview: "index.html", map: "map.html", analysis: "analysis.html", method: "methodology.html", assistant: "assistant.html", about: "about.html" };
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.toggle("active", link.getAttribute("href") === pageToHref[currentPage]);
  });
  const todayLabel = document.getElementById("todayLabel");
  if (todayLabel) todayLabel.textContent = new Date().toLocaleDateString(undefined, { month: "short", year: "numeric" }).toUpperCase();
}

document.getElementById("siteTable")?.addEventListener("click", (event) => {
  const row = event.target.closest("tr[data-lat][data-lon]");
  if (row) selectChartLocation(`${row.dataset.lat},${row.dataset.lon}`);
});

document.getElementById("chartSite")?.addEventListener("change", (event) => selectChartLocation(event.target.value));
document.getElementById("printReportBtn")?.addEventListener("click", printLocationReport);
document.getElementById("langToggle")?.addEventListener("click", (event) => {
  setLanguage(localStorage.getItem("terrawatch_lang") === "am" ? "en" : "am");
});

initializeNavigation();
setLanguage(localStorage.getItem("terrawatch_lang") || "en");
initializeMap();
loadChartLibrary();
updateHazardBanner();
loadBackendData().then(() => {
  const location = selectedLocation();
  if (document.getElementById("map") || document.getElementById("displacementChart")) {
    analyzeLocation(location.lat, location.lon);
  }
});
