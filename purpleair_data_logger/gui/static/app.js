const COLORS = [
  "#a855f7",
  "#06b6d4",
  "#10b981",
  "#f59e0b",
  "#f43f5e",
  "#3b82f6",
];

let currentLocale = "en";
let localeStrings = {};
let supportedLocales = ["en"];

async function apiGet(path) {
  const r = await fetch(path);
  return r.json();
}

async function apiPost(path, payload) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
  return r.json();
}

function resolveDotted(obj, path) {
  if (!obj || !path) return null;
  const parts = path.split(".");
  let curr = obj;
  for (const p of parts) {
    if (curr && typeof curr === "object" && p in curr) {
      curr = curr[p];
    } else {
      return null;
    }
  }
  return curr;
}

function t(key, fallback) {
  if (localeStrings && typeof localeStrings === "object") {
    if (key in localeStrings && typeof localeStrings[key] === "string") {
      return localeStrings[key];
    }
    const val = resolveDotted(localeStrings, key);
    if (typeof val === "string") {
      return val;
    }
  }
  return fallback !== undefined ? fallback : key;
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const translated = t(key, null);
    if (translated) {
      if (
        el.tagName === "INPUT" &&
        (el.type === "button" || el.type === "submit")
      ) {
        el.value = translated;
      } else {
        el.textContent = translated;
      }
    }
  });

  const langSel = document.getElementById("lang-select");
  if (langSel && supportedLocales && supportedLocales.length > 0) {
    langSel.innerHTML = "";
    supportedLocales.forEach((code) => {
      const opt = document.createElement("option");
      opt.value = code;
      opt.textContent = code.toUpperCase();
      if (code === currentLocale) opt.selected = true;
      langSel.appendChild(opt);
    });
  }
}

async function initLocale(targetLocale) {
  try {
    const url = targetLocale
      ? `/api/locale?locale=${encodeURIComponent(targetLocale)}`
      : "/api/locale";
    const res = await apiGet(url);
    if (res.ok) {
      currentLocale = res.locale || "en";
      supportedLocales = res.supported || ["en"];
      localeStrings = res.strings || {};
      applyTranslations();
    }
  } catch (_e) {}
}

async function switchLocale(newLocale) {
  try {
    const res = await apiPost("/api/locale", { locale: newLocale });
    if (res.ok) {
      currentLocale = res.locale;
      supportedLocales = res.supported;
      localeStrings = res.strings;
      applyTranslations();
      await loadConfigIntoUi();
    }
  } catch (_e) {}
}

const selectedSeries = new Set();
let userModifiedSeries = false;
let lastSeriesMap = {};

function updateSeriesPills(seriesMap) {
  const container = document.getElementById("chart-series-selector");
  if (!container) return;
  const allNames = Object.keys(seriesMap || {});
  if (allNames.length === 0) {
    container.innerHTML = "";
    return;
  }

  if (!userModifiedSeries) {
    allNames.forEach((n) => selectedSeries.add(n));
  }

  let html = "";
  allNames.forEach((name, idx) => {
    const color = COLORS[idx % COLORS.length];
    const isSel = selectedSeries.has(name);
    html += `
      <div class="series-pill ${isSel ? "active" : ""}" data-series="${name}" style="${isSel ? `border-color:${color};color:${color}` : ""}">
        <span class="dot">${isSel ? "●" : "○"}</span>
        <span>${name}</span>
      </div>
    `;
  });
  container.innerHTML = html;

  container.querySelectorAll(".series-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      const name = pill.dataset.series;
      userModifiedSeries = true;
      if (selectedSeries.has(name)) {
        selectedSeries.delete(name);
      } else {
        selectedSeries.add(name);
      }
      updateSeriesPills(lastSeriesMap);
      renderChart(lastSeriesMap);
    });
  });
}

function renderChart(seriesMap) {
  lastSeriesMap = seriesMap || {};
  updateSeriesPills(seriesMap);

  const svg = document.getElementById("telemetry-chart");
  const W = 900,
    H = 240,
    padL = 55,
    padR = 20,
    padT = 26,
    padB = 24;
  const plotW = W - padL - padR,
    plotH = H - padT - padB;
  const allEntries = Object.entries(seriesMap || {}).filter(
    ([, pts]) => pts && pts.length > 0,
  );

  let html = "";
  for (let i = 0; i < 5; i++) {
    const y = padT + (plotH * i) / 4;
    html += `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="#334155" stroke-dasharray="3,4"/>`;
  }

  if (allEntries.length === 0) {
    const emptyMsg = t(
      "status_bar.chart_empty_web",
      'Start CLI Logger or click "Run 1 Cycle (--once)" to stream PurpleAir telemetry',
    );
    html += `<text x="${W / 2}" y="${H / 2}" text-anchor="middle" fill="#94a3b8" font-size="13">${emptyMsg}</text>`;
    svg.innerHTML = html;
    return;
  }

  const activeEntries = allEntries.filter(([name]) => selectedSeries.has(name));

  if (activeEntries.length === 0) {
    const noSelMsg = t(
      "status_bar.no_series_selected",
      "No series selected. Select one or more fields above to view telemetry.",
    );
    html += `<text x="${W / 2}" y="${H / 2}" text-anchor="middle" fill="#94a3b8" font-size="13">${noSelMsg}</text>`;
    svg.innerHTML = html;
    return;
  }

  const allVals = activeEntries.flatMap(([, pts]) =>
    pts.map((p) => Number(p.value)),
  );
  let vmin = Math.min(...allVals),
    vmax = Math.max(...allVals);
  if (Math.abs(vmax - vmin) < 1e-9) {
    vmin -= 1;
    vmax += 1;
  }

  html += `<text x="${padL - 8}" y="${padT + 4}" text-anchor="end" fill="#94a3b8" font-size="11">${vmax.toFixed(1)}</text>`;
  html += `<text x="${padL - 8}" y="${padT + plotH}" text-anchor="end" fill="#94a3b8" font-size="11">${vmin.toFixed(1)}</text>`;

  let lx = padL;
  activeEntries.forEach(([name, pts]) => {
    const allIdx = allEntries.findIndex(([n]) => n === name);
    const color = COLORS[(allIdx >= 0 ? allIdx : 0) % COLORS.length];
    html += `<text x="${lx}" y="16" fill="${color}" font-size="12" font-weight="600">● ${name}</text>`;
    lx += Math.min(220, name.length * 7 + 30);

    if (pts.length === 1) {
      const y = padT + plotH - ((pts[0].value - vmin) / (vmax - vmin)) * plotH;
      html += `<circle cx="${padL + plotW / 2}" cy="${y}" r="4" fill="${color}"/>`;
      return;
    }
    const span = Math.max(1, pts.length - 1);
    const poly = pts
      .map((pt, i) => {
        const x = padL + (i / span) * plotW;
        const y =
          padT + plotH - ((Number(pt.value) - vmin) / (vmax - vmin)) * plotH;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
    html += `<polyline fill="none" stroke="${color}" stroke-width="2.2" points="${poly}"/>`;
  });

  svg.innerHTML = html;
}

async function loadConfigIntoUi() {
  const data = await apiGet("/api/config");
  if (!data.ok) return;
  const prefix = t("app.json_config_prefix", "JSON Config: ");
  document.getElementById("config-subtitle").textContent =
    `${prefix}${data.path}`;
  document.getElementById("json-editor").value = data.raw;

  const dutSel = document.getElementById("req-dut");
  dutSel.innerHTML = "";
  ((data.config && data.config.duts) || []).forEach((d) => {
    const opt = document.createElement("option");
    opt.value = d.name;
    opt.textContent = `${d.name} (${d.dut_ip})`;
    dutSel.appendChild(opt);
  });

  if (data.config && data.config.gui) {
    if (data.config.gui.theme) {
      document.body.dataset.theme =
        data.config.gui.theme === "light" ? "light" : "dark";
    }
  }
}

async function pollStatus() {
  try {
    const snap = await apiGet("/api/status");
    if (!snap.ok) return;
    const st = snap.stats || {};
    document.getElementById("kpi-state").textContent = snap.running
      ? "RUNNING"
      : "IDLE";
    document.getElementById("kpi-cycles").textContent =
      st.cycles_completed ?? st.batches_polled ?? 0;
    document.getElementById("kpi-batches").textContent =
      st.processed_batches ?? st.batches_written ?? 0;
    document.getElementById("kpi-samples").textContent =
      st.processed_samples ?? st.samples_written ?? 0;
    document.getElementById("kpi-queue").textContent = st.queue_depth ?? 0;
    document.getElementById("kpi-errors").textContent =
      `${st.poll_errors ?? 0} / ${st.sink_errors ?? 0}`;

    renderChart(snap.series || {});
    document.getElementById("cli-log").textContent = (snap.cli_lines || [])
      .slice(-35)
      .join("\n");
    document.getElementById("footer-cli").textContent =
      `Backend CLI: ${snap.cli_command}`;

    const audits = snap.audit || [];
    if (audits.length > 0) {
      const a0 = audits[0];
      document.getElementById("footer-audit").textContent =
        `Last CLI [${a0.exit_code ?? "running"}, ${a0.duration_ms} ms]: ${a0.command}`;
    }
    const auditBody = document.getElementById("audit-tbody");
    auditBody.innerHTML = audits
      .map(
        (a) =>
          `<tr><td>${a.timestamp}</td><td>${a.exit_code ?? "..."}</td><td>${a.duration_ms}</td><td><code>${a.command}</code></td></tr>`,
      )
      .join("");
  } catch (_e) {}
}

function setupEvents() {
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".tab")
        .forEach((b) => b.classList.remove("active"));
      document
        .querySelectorAll(".tab-panel")
        .forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    });
  });

  document.getElementById("btn-theme").addEventListener("click", () => {
    document.body.dataset.theme =
      document.body.dataset.theme === "light" ? "dark" : "light";
  });

  const langSelect = document.getElementById("lang-select");
  if (langSelect) {
    langSelect.addEventListener("change", (e) => {
      void switchLocale(e.target.value);
    });
  }

  document.getElementById("btn-start").addEventListener("click", async () => {
    await apiPost("/api/run/start");
    await pollStatus();
  });

  document.getElementById("btn-stop").addEventListener("click", async () => {
    await apiPost("/api/run/stop");
    await pollStatus();
  });

  document.getElementById("btn-once").addEventListener("click", async () => {
    await apiPost("/api/run/once");
    await pollStatus();
  });

  const btnChartAll = document.getElementById("btn-chart-all");
  if (btnChartAll) {
    btnChartAll.addEventListener("click", () => {
      userModifiedSeries = true;
      Object.keys(lastSeriesMap || {}).forEach((n) => selectedSeries.add(n));
      updateSeriesPills(lastSeriesMap);
      renderChart(lastSeriesMap);
    });
  }

  const btnChartNone = document.getElementById("btn-chart-none");
  if (btnChartNone) {
    btnChartNone.addEventListener("click", () => {
      userModifiedSeries = true;
      selectedSeries.clear();
      updateSeriesPills(lastSeriesMap);
      renderChart(lastSeriesMap);
    });
  }

  document
    .getElementById("btn-probe-all")
    .addEventListener("click", async () => {
      const res = await apiPost("/api/probe", {});
      const rows = ((res.data && res.data.results) || []).flatMap(
        (r) => r.samples || [],
      );
      document.getElementById("req-tbody").innerHTML = rows
        .map(
          (s) =>
            `<tr><td>${s.oid}</td><td>${s.oid_index}</td><td>${s.snmp_type}</td><td>${s.raw_value}</td><td>${s.type_name}</td><td>${s.status}</td></tr>`,
        )
        .join("");
      document.getElementById("req-status").textContent =
        `CLI probe returned ${rows.length} sample(s).`;
      document.querySelector('[data-tab="studio"]').click();
      await pollStatus();
    });

  document
    .getElementById("btn-exec-req")
    .addEventListener("click", async () => {
      const dut = document.getElementById("req-dut").value;
      const op = document.getElementById("req-op").value;
      const oids = document.getElementById("req-oids").value;
      const record = document.getElementById("req-record").checked;
      let res;
      if (op === "set") {
        res = await apiPost("/api/set", {
          dut,
          oid: oids.split(",")[0].trim(),
          set_type: document.getElementById("req-set-type").value,
          value: document.getElementById("req-set-val").value,
          record,
        });
      } else {
        res = await apiPost("/api/request", {
          dut,
          operation: op,
          oids,
          record,
        });
      }
      const payload = res.data || {};
      const samples = payload.samples || [];
      document.getElementById("req-tbody").innerHTML = samples
        .map(
          (s) =>
            `<tr><td>${s.oid}</td><td>${s.oid_index}</td><td>${s.snmp_type}</td><td>${s.raw_value}</td><td>${s.type_name}</td><td>${s.status}</td></tr>`,
        )
        .join("");
      document.getElementById("req-status").textContent = res.ok
        ? `OK: ${samples.length} sample(s) in ${(payload.latency_ms || 0).toFixed(2)} ms`
        : `Error: ${(payload && payload.error) || res.stderr || res.error}`;
      await pollStatus();
    });

  document.getElementById("btn-inspect").addEventListener("click", async () => {
    const dut = encodeURIComponent(
      document.getElementById("exp-dut").value.trim(),
    );
    const metric = encodeURIComponent(
      document.getElementById("exp-metric").value.trim(),
    );
    const limit = encodeURIComponent(
      document.getElementById("exp-limit").value || "50",
    );
    const res = await apiGet(
      `/api/inspect?limit=${limit}&dut=${dut}&metric=${metric}`,
    );
    const rows = (res.data && res.data.rows) || [];
    document.getElementById("exp-tbody").innerHTML = rows
      .map(
        (r) =>
          `<tr><td>${r.ts_unix_ns ?? r.timestamp_ns}</td><td>${r.dut_name}</td><td>${r.metric_name}</td><td>${r.oid}</td><td>${r.snmp_type}</td><td>${r.raw_value || r.str_val || r.value}</td><td>${r.sink_type}</td></tr>`,
      )
      .join("");
    await pollStatus();
  });

  document
    .getElementById("btn-load-tpl")
    .addEventListener("click", async () => {
      const name = document.getElementById("tpl-select").value;
      const res = await apiGet(
        `/api/template?name=${encodeURIComponent(name)}`,
      );
      if (res.ok && res.raw) {
        document.getElementById("json-editor").value = res.raw;
        document.getElementById("json-status").textContent =
          `Loaded '${name}' CLI template.`;
      }
      await pollStatus();
    });

  document
    .getElementById("btn-validate-json")
    .addEventListener("click", async () => {
      const raw = document.getElementById("json-editor").value;
      const res = await apiPost("/api/validate", { raw });
      const rep = res.data || {};
      document.getElementById("json-status").textContent = rep.valid
        ? `VALID (${rep.enabled_duts} sensors, ${rep.total_metrics} metrics, ${rep.enabled_sinks} sinks)`
        : `INVALID: ${(rep.errors || [res.stderr]).join("; ")}`;
      await pollStatus();
    });

  document
    .getElementById("btn-save-json")
    .addEventListener("click", async () => {
      const raw = document.getElementById("json-editor").value;
      const res = await apiPost("/api/config", { raw });
      if (res.error) {
        document.getElementById("json-status").textContent =
          `Error: ${res.error}`;
        return;
      }
      const rep = res.data || {};
      document.getElementById("json-status").textContent = rep.valid
        ? "Saved JSON configuration and validated via CLI."
        : `Saved with validation warnings/errors: ${(rep.errors || []).join("; ")}`;
      await loadConfigIntoUi();
      await pollStatus();
    });
}

window.addEventListener("DOMContentLoaded", async () => {
  setupEvents();
  await initLocale();
  await loadConfigIntoUi();
  await pollStatus();
  setInterval(() => {
    void pollStatus();
  }, 1000);
});
