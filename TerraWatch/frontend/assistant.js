(function () {
  if (!window.terraWatch) return;

  const isAssistantPage = Boolean(document.getElementById("aiPageTitle"));
  if (!isAssistantPage) {
    const widgetRoot = document.createElement("div");
    widgetRoot.className = "assistant-widget-root";
    widgetRoot.innerHTML = `
      <button class="assistant-launcher" id="assistantLauncher" type="button" aria-label="Open TerraWatch AI assistant" aria-expanded="false" aria-controls="assistantWidget">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5a8.5 8.5 0 0 0-7.2 13l-.9 4.1 4.1-1.1A8.5 8.5 0 1 0 12 3.5Z"/><path d="M8.2 12h.1m3.6 0h.1m3.6 0h.1"/></svg>
        <span>Ask AI</span>
      </button>
      <section class="assistant-widget" id="assistantWidget" aria-label="TerraWatch AI assistant" hidden>
        <header class="assistant-widget-header">
          <div>
            <div class="assistant-widget-title" id="aiPanelTitle">TerraWatch AI</div>
            <div class="assistant-widget-subtitle">LIVE SITE DATA · BACKEND CONNECTED</div>
          </div>
          <div class="assistant-widget-controls">
            <button type="button" class="assistant-widget-clear" id="clearChatBtn">Clear</button>
            <button type="button" class="assistant-widget-close" id="closeAssistantBtn" aria-label="Close AI assistant">×</button>
          </div>
        </header>
        <div class="assistant-widget-messages" id="chatMessages" role="log" aria-live="polite"></div>
        <div class="assistant-widget-prompts" id="promptChips">
          <button class="prompt-chip" type="button" data-prompt="Summarize the current subsidence clusters and their measurements">Summarize clusters</button>
          <button class="prompt-chip" type="button" data-prompt="Explain the analysis for my selected map location">Explain selected site</button>
          <button class="prompt-chip" type="button" data-prompt="How does InSAR detect urban land subsidence?">How InSAR works</button>
        </div>
        <form class="assistant-widget-inputbar" id="chatForm">
          <input class="chat-input" id="chatInput" type="text" placeholder="Ask about this site…" autocomplete="off" required>
          <button class="action-btn primary" type="submit" id="sendBtn">Send</button>
        </form>
        <div class="assistant-widget-disclaimer">Answers use returned site data when available and are not engineering advice.</div>
      </section>
    `;
    document.body.appendChild(widgetRoot);
  }

  const messages = document.getElementById("chatMessages");
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const siteSelect = document.getElementById("aiSiteSelect");
  const quickBrief = document.getElementById("aiQuickBrief");

  if (!messages || !form || !input) return;

  let sending = false;

  function syncLocale() {
    const isAm = localStorage.getItem("terrawatch_lang") === "am";
    const setText = (id, value) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    };
    setText("aiPageTitle", isAm
      ? "TerraWatch AI · የመሬት መስመጥ ተንታኝ"
      : "TerraWatch AI · Subsidence Analyst");
    setText("aiPageSub", isAm
      ? "ስለ ቀጥታ የኋላ ገጽ መለኪያዎች፣ መዋቅሮች ወይም InSAR ዘዴ ይጠይቁ"
      : "Ask questions about live backend measurements, structures, or InSAR methodology");
    setText("aiPanelTitle", isAm ? "ጂኦስፓሻል AI ረዳት" : isAssistantPage ? "Geospatial AI Copilot" : "TerraWatch AI");
    setText("sendBtn", isAm ? "ላክ →" : isAssistantPage ? "Send →" : "Send");
    setText("clearChatBtn", isAm ? "ውይይት አጽዳ" : isAssistantPage ? "Clear chat" : "Clear");
    input.placeholder = isAm ? "ስለ መሬት መስመጥ፣ መዋቅሮች ወይም InSAR ይጠይቁ..." : isAssistantPage
      ? "Ask about subsidence, structures, or InSAR…"
      : "Ask about this site…";
    setText("askSiteBtn", isAm ? "ስለዚህ ቦታ AIን ይጠይቁ →" : "Ask AI about this site →");
    const launcher = document.getElementById("assistantLauncher");
    if (launcher) launcher.setAttribute("aria-label", isAm ? "የTerraWatch AI ረዳትን ክፈት" : "Open TerraWatch AI assistant");
  }

  function appendMessage(role, text, label) {
    const wrapper = document.createElement("div");
    wrapper.className = `msg ${role}`;
    const meta = document.createElement("div");
    meta.className = "msg-meta";
    meta.textContent = label || (role === "assistant" ? "TERRAWATCH AI · BACKEND" : "YOU");
    const content = document.createElement("div");
    content.textContent = text;
    content.style.whiteSpace = "pre-wrap";
    wrapper.append(meta, content);
    messages.appendChild(wrapper);
    if (role === "assistant" && wrapper.scrollHeight > messages.clientHeight) {
      messages.scrollTop = wrapper.getBoundingClientRect().top - messages.getBoundingClientRect().top + messages.scrollTop;
    } else {
      messages.scrollTop = messages.scrollHeight;
    }
  }

  function updateBrief(analysis) {
    if (!quickBrief) return;
    if (!analysis) {
      quickBrief.textContent = "Select a location to load its backend analysis.";
      return;
    }
    quickBrief.textContent = analysis.status === "OK"
      ? `${analysis.risk_level}. Cell displacement: ${analysis.exact_80m_cell_cm ?? "not available"} cm; annualized rate: ${analysis.annualized_rate_cm_yr ?? "not available"} cm/year; confidence: ${analysis.confidence_level}.`
      : `${analysis.status}: ${analysis.ai_summary}`;
  }

  function format(value, suffix = "") {
    return value == null || !Number.isFinite(Number(value)) ? "not available" : `${Number(value).toFixed(2)}${suffix}`;
  }

  function buildDataBrief(question) {
    const query = question.toLowerCase();
    const structures = window.terraWatch.getStructures();
    const priorities = structures?.top_priority_list || [];
    const clusters = window.terraWatch.getClusters() || [];
    const analysis = window.terraWatch.getSelectedAnalysis();
    const location = window.terraWatch.getSelectedLocation();
    const series = window.terraWatch.getSelectedTimeseries();

    if (/cluster|hot.?spot|subsidence zone|zone/.test(query)) {
      if (!clusters.length) return "The backend has not returned any subsidence clusters.";
      const strongest = clusters.slice(0, 3).map((cluster, index) =>
        `${index + 1}. Peak ${format(cluster.peak_sinking_cm, " cm")} at ${cluster.center_lat}°N, ${cluster.center_lon}°E; mean ${format(cluster.mean_sinking_cm, " cm")}; area ${format(cluster.area_km2, " km²")}.`
      );
      return `${clusters.length} clusters are returned by the backend model. Strongest returned clusters:\n${strongest.join("\n")}\nThese are model-derived screening zones, not confirmed damage reports.`;
    }

    if (/structure|building|bridge|road|infrastructure|priority|exposed/.test(query)) {
      if (!priorities.length) return "The backend has not returned a priority structure list.";
      const top = priorities.slice(0, 5).map((item, index) =>
        `${index + 1}. ${item.display_name || item.structure_type || "Structure"} — ${format(item.vertical_cm, " cm")}; ${item.risk_level || "risk not classified"}.`
      );
      return `${structures.at_risk_structures?.features?.length ?? priorities.length} structure features are returned; this priority list contains ${priorities.length}. Most negative values in the returned priority list:\n${top.join("\n")}\nThese screening values do not replace a site inspection.`;
    }

    if (/time.?series|trend|history|historical|over time|observation/.test(query)) {
      const dates = series?.dates || [];
      const values = series?.cumulative_cm || [];
      if (!dates.length) return "No coherent time-series observations were returned for the selected location.";
      const points = dates.map((date, index) => `${date}: ${format(values[index], " cm")}`);
      return `${dates.length} time-series observation(s) are available at ${location.lat.toFixed(5)}°N, ${location.lon.toFixed(5)}°E:\n${points.join("\n")}\n${dates.length < 2 ? "A single observation cannot establish a trend; no history has been interpolated." : "These are backend observations; the series should not be extrapolated beyond its recorded dates."}`;
    }

    if (/method|insar|nisar|radar|satellite|coherence|sar/.test(query)) {
      return "TerraWatch presents backend-derived radar displacement on an approximately 80 m grid, point-level uncertainty and risk classification, nearby mapped structures, time-series observations when available, and spatial clusters from the backend ML service. InSAR estimates relative ground motion from changes in radar phase between satellite acquisitions; low coherence or limited acquisitions can reduce confidence. Annualized rates and forecasts are model-derived, especially uncertain with few passes, and require field verification before engineering decisions.";
    }

    if (analysis) {
      const nearby = analysis.nearby_structures?.length
        ? ` Nearby structures within 150 m: ${analysis.nearby_structures.map((item) => `${item.display_name} (${format(item.vertical_cm, " cm")}, ${item.risk_level})`).join("; ")}.`
        : " No nearby structures were returned within 150 m.";
      return `At ${location.lat.toFixed(5)}°N, ${location.lon.toFixed(5)}°E, the backend classifies the location as ${analysis.risk_level} (${analysis.confidence_level}). Cell displacement: ${format(analysis.exact_80m_cell_cm, " cm")}; uncertainty: ${format(analysis.uncertainty_1sigma_cm, " cm")}; annualized estimate: ${format(analysis.annualized_rate_cm_yr, " cm/year")}. ${analysis.ai_summary || "No backend interpretation was returned."}${nearby}\nAnnualized values and forecasts are screening estimates, not verified long-term movement or an engineering assessment.`;
    }

    return "Live analysis is not available yet. Select a location or wait for the backend data to load, then ask about the selected site, clusters, structures, observations, or InSAR methodology.";
  }

  function getBackendFallbackReason(answer) {
    const match = answer.match(/^\[Gemini unavailable: ([^\]]+)\]/);
    return match?.[1] || null;
  }

  function isBuiltInBackendReply(answer) {
    return answer.startsWith("[Local data briefing]") ||
      getBackendFallbackReason(answer) !== null ||
      (answer.startsWith("At ") && answer.includes(" NISAR measured ")) ||
      answer.startsWith("TerraWatch combines ascending and descending");
  }

  async function loadContext() {
    const results = await Promise.allSettled([
      window.terraWatch.request("/api/structures"),
      window.terraWatch.request("/api/ml-clusters"),
      window.terraWatch.request("/api/sync-status")
    ]);

    const [structuresResult, clustersResult, syncResult] = results;
    if (structuresResult.status === "fulfilled") {
      const structures = structuresResult.value;
      const priority = structures.top_priority_list || [];
      const values = priority
        .filter((item) => item.vertical_cm != null)
        .map((item) => Number(item.vertical_cm))
        .filter(Number.isFinite);
      document.getElementById("assistantStructureCount").textContent =
        String(structures.at_risk_structures?.features?.length ?? "—");
      document.getElementById("assistantPeak").textContent =
        values.length ? `${Math.min(...values).toFixed(2)} cm` : "—";
      if (siteSelect) {
        siteSelect.replaceChildren();
        priority.forEach((item, index) => {
          const option = document.createElement("option");
          option.value = `${item.lat},${item.lon}`;
          option.textContent = `${index + 1}. ${item.display_name || item.structure_type || "Structure"}`;
          siteSelect.appendChild(option);
        });
      }
    } else {
      appendMessage("assistant", `Structure context unavailable: ${structuresResult.reason.message}`, "LIVE DATA STATUS");
    }
    if (clustersResult.status === "fulfilled") {
      document.getElementById("assistantClusterCount").textContent =
        `${(clustersResult.value.subsidence_clusters || []).length} clusters`;
    } else {
      document.getElementById("assistantClusterCount").textContent = "Unavailable";
    }
    if (syncResult.status === "fulfilled") {
      document.getElementById("assistantPasses").textContent =
        `${syncResult.value.total_passes_stored ?? "—"} pass(es)`;
    } else {
      document.getElementById("assistantPasses").textContent = "Unavailable";
    }

    const selected = window.terraWatch.getSelectedLocation();
    await window.terraWatch.analyzeLocation(selected.lat, selected.lon);
    updateBrief(window.terraWatch.getSelectedAnalysis());
  }

  async function sendQuestion(question) {
    const trimmed = question.trim();
    if (!trimmed || sending) return;
    sending = true;
    appendMessage("user", trimmed);
    input.value = "";
    const button = document.getElementById("sendBtn");
    if (button) button.disabled = true;
    const typing = document.createElement("div");
    typing.className = "msg assistant";
    typing.textContent = "Checking live TerraWatch data…";
    messages.appendChild(typing);

    let responseText;
    let responseLabel = "TERRAWATCH AI · BACKEND";
    try {
      const location = window.terraWatch.getSelectedLocation();
      const payload = await window.terraWatch.request("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed, lat: location.lat, lon: location.lon })
      });
      if (typeof payload.answer !== "string" || !payload.answer.trim()) {
        throw new Error("The chat endpoint returned no answer.");
      }
      responseText = payload.answer.trim();
      if (isBuiltInBackendReply(responseText)) {
        const fallbackReason = getBackendFallbackReason(responseText);
        responseText = buildDataBrief(trimmed);
        if (fallbackReason) {
          responseText += `\n\nGemini was unavailable (${fallbackReason}); this is a live-data briefing.`;
        }
        responseLabel = "TERRAWATCH · LIVE DATA BRIEFING";
      }
    } catch (error) {
      responseText = `${buildDataBrief(trimmed)}\n\nThe chat service was unavailable (${error.message}); this briefing uses only data already returned by the TerraWatch backend.`;
      responseLabel = "TERRAWATCH · LIVE DATA FALLBACK";
    } finally {
      typing.remove();
      appendMessage("assistant", responseText, responseLabel);
      sending = false;
      if (button) button.disabled = false;
      input.focus();
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendQuestion(input.value);
  });

  document.getElementById("promptChips")?.addEventListener("click", (event) => {
    const chip = event.target.closest(".prompt-chip");
    if (chip) sendQuestion(chip.dataset.prompt || chip.textContent);
  });

  document.getElementById("clearChatBtn")?.addEventListener("click", () => {
    messages.replaceChildren();
    appendMessage("assistant", "Ask about live site analysis, clusters, structures, observations, or InSAR methodology.");
  });

  siteSelect?.addEventListener("change", async () => {
    const [lat, lon] = siteSelect.value.split(",").map(Number);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
    await window.terraWatch.analyzeLocation(lat, lon);
    updateBrief(window.terraWatch.getSelectedAnalysis());
  });

  document.getElementById("askSiteBtn")?.addEventListener("click", () => {
    sendQuestion("Provide a detailed briefing for my selected location.");
  });

  window.addEventListener("terrawatch:location", (event) => updateBrief(event.detail.analysis));
  document.getElementById("langToggle")?.addEventListener("click", () => setTimeout(syncLocale, 0));

  const launcher = document.getElementById("assistantLauncher");
  const widget = document.getElementById("assistantWidget");
  const closeButton = document.getElementById("closeAssistantBtn");
  const setWidgetOpen = (open) => {
    if (!widget || !launcher) return;
    widget.hidden = !open;
    launcher.setAttribute("aria-expanded", String(open));
    if (open) input.focus();
    else launcher.focus();
  };
  launcher?.addEventListener("click", () => setWidgetOpen(widget.hidden));
  closeButton?.addEventListener("click", () => setWidgetOpen(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && widget && !widget.hidden) setWidgetOpen(false);
  });

  syncLocale();
  appendMessage("assistant", "Ask about live site analysis, clusters, structures, observations, or InSAR methodology.");
  if (isAssistantPage) {
    loadContext().catch((error) => {
      appendMessage("assistant", `Could not load live backend context: ${error.message}`, "LIVE DATA STATUS");
    });
  }
})();
