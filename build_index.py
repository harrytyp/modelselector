#!/usr/bin/env python3
"""Build the complete index.html with all new features."""
import os

root = "C:/Users/go75bel/Downloads/ModelSelector"

with open(os.path.join(root, "index.html"), "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS before </style>
css_additions = """
    /* === COMPARISON CHECKBOX === */
    .compare-checkbox {
      width: 18px; height: 18px;
      border: 2px solid var(--border-color);
      border-radius: 4px;
      background: rgba(255,255,255,0.03);
      cursor: pointer;
      accent-color: var(--accent-indigo);
      transition: all 0.2s;
    }
    .compare-checkbox:checked {
      border-color: var(--accent-indigo);
      box-shadow: 0 0 8px rgba(99,102,241,0.4);
    }
    th.checkbox-col, td.checkbox-col { width: 40px; text-align: center; }
    td.checkbox-col { cursor: default; }

    .btn-compare {
      background: linear-gradient(135deg, var(--accent-indigo), #4f46e5);
      border: none; color: white;
      padding: 0.45rem 1rem; border-radius: 8px;
      font-size: 0.8rem; font-weight: 700; cursor: pointer;
      transition: all 0.2s;
      display: flex; align-items: center; gap: 0.4rem;
      opacity: 0.5; pointer-events: none;
    }
    .btn-compare.active { opacity: 1; pointer-events: auto; }
    .btn-compare:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(99,102,241,0.4); }

    .compare-modal-content { max-height: 85vh; overflow-y: auto; }
    .compare-table-wrap { overflow-x: auto; border-radius: 12px; border: 1px solid var(--border-color); }
    .compare-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .compare-table th {
      background: rgba(0,0,0,0.2); padding: 0.75rem 1rem;
      font-size: 0.7rem; text-transform: uppercase;
      letter-spacing: 0.5px; color: var(--text-muted);
      border-bottom: 1px solid var(--border-color);
      text-align: left; white-space: nowrap;
    }
    .compare-table td {
      padding: 0.6rem 1rem;
      border-bottom: 1px solid rgba(255,255,255,0.03);
      font-family: var(--font-mono); font-size: 0.78rem;
    }
    .compare-table tr:last-child td { border-bottom: none; }
    .compare-table .metric-label { color: var(--text-secondary); font-weight: 600; font-family: var(--font-sans); font-size: 0.75rem; }
    .compare-table .model-header-cell { font-weight: 700; color: #fff; font-family: var(--font-sans); }
    .compare-model-name { display: flex; flex-direction: column; gap: 0.15rem; }
    .compare-model-name .name { font-weight: 700; color: #fff; font-size: 0.85rem; }
    .compare-model-name .meta { font-size: 0.65rem; color: var(--text-muted); }
    .compare-table .score-good { color: var(--fit-green); }
    .compare-table .score-mid { color: var(--fit-amber); }
    .compare-table .score-bad { color: var(--fit-red); }

    .btn-expand-bench {
      background: rgba(99,102,241,0.1);
      border: 1px solid rgba(99,102,241,0.2);
      color: var(--accent-indigo);
      padding: 0.3rem 0.6rem; border-radius: 6px;
      font-size: 0.65rem; font-weight: 700; cursor: pointer;
      transition: all 0.2s;
      font-family: var(--font-sans); white-space: nowrap;
    }
    .btn-expand-bench:hover { background: rgba(99,102,241,0.2); border-color: var(--accent-indigo); }

    .benchmark-col-header { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; }
    .benchmark-col-header .short { font-size: 0.65rem; font-weight: 700; color: var(--text-muted); }
    .benchmark-col-header .full { font-size: 0.5rem; color: var(--text-muted); opacity: 0.6; white-space: nowrap; }
    td.benchmark-cell { text-align: center; font-family: var(--font-mono); font-size: 0.78rem; padding: 0.5rem 0.6rem; }

    .license-badge {
      display: inline-block; font-size: 0.6rem; font-weight: 700;
      padding: 0.1rem 0.35rem; border-radius: 3px;
      text-transform: uppercase; letter-spacing: 0.3px;
    }
    .license-apache-2\\.0 { background: rgba(16,185,129,0.12); color: var(--fit-green); border: 1px solid rgba(16,185,129,0.2); }
    .license-mit { background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.2); }
    .license-llama3\\.2, .license-llama3\\.1, .license-llama3, .license-llama2, .license-llama3\\.3 { background: rgba(245,158,11,0.12); color: var(--fit-amber); border: 1px solid rgba(245,158,11,0.2); }
    .license-gemma { background: rgba(239,68,68,0.12); color: var(--fit-red); border: 1px solid rgba(239,68,68,0.2); }
    .license-qwen { background: rgba(6,182,212,0.12); color: var(--accent-cyan); border: 1px solid rgba(6,182,212,0.2); }
    .license-deepseek { background: rgba(168,85,247,0.12); color: #a855f7; border: 1px solid rgba(168,85,247,0.2); }
    .license-cc-by-nc-4\\.0, .license-cc-by-nc-sa-4\\.0, .license-cc-by-nc-nd-4\\.0, .license-cc-by-sa-4\\.0, .license-cc-by-4\\.0 { background: rgba(236,72,153,0.12); color: #ec4899; border: 1px solid rgba(236,72,153,0.2); }
    .license-other { background: rgba(148,163,184,0.1); color: var(--text-secondary); border: 1px solid rgba(148,163,184,0.15); }

    .scatter-container {
      background: var(--bg-card); border: 1px solid var(--border-color);
      border-radius: 20px; padding: 1.5rem; position: relative; min-height: 500px;
    }
    .scatter-controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .scatter-controls .title { font-size: 0.85rem; font-weight: 700; color: #fff; }
    .scatter-legend {
      display: flex; flex-wrap: wrap; gap: 0.4rem 0.8rem;
      font-size: 0.7rem; color: var(--text-secondary);
      margin-top: 0.75rem; padding-top: 0.75rem;
      border-top: 1px solid var(--border-color);
    }
    .scatter-legend-item { display: flex; align-items: center; gap: 0.3rem; }
    .scatter-legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
    #scatterCanvas { width: 100%; height: 460px; cursor: crosshair; }
    .scatter-tooltip {
      position: absolute; background: rgba(12,17,34,0.95);
      border: 1px solid var(--accent-indigo); border-radius: 8px;
      padding: 0.5rem 0.75rem; font-size: 0.75rem;
      pointer-events: none; display: none; z-index: 100;
      backdrop-filter: blur(12px); box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      max-width: 240px;
    }
    .scatter-tooltip .model-name { font-weight: 700; color: #fff; margin-bottom: 0.2rem; }
    .scatter-tooltip .detail { color: var(--text-secondary); line-height: 1.4; }
    .scatter-tooltip .detail span { color: var(--accent-cyan); font-family: var(--font-mono); }

    .view-toggle-group {
      display: flex; gap: 0.25rem;
      background: rgba(0,0,0,0.2); padding: 0.2rem; border-radius: 6px;
      border: 1px solid var(--border-color);
    }
    .view-toggle-btn {
      padding: 0.35rem 0.65rem; font-size: 0.72rem; font-weight: 700;
      border: none; border-radius: 4px; cursor: pointer;
      background: transparent; color: var(--text-muted);
      transition: all 0.2s; font-family: var(--font-sans);
    }
    .view-toggle-btn.active { background: var(--accent-indigo); color: #fff; box-shadow: 0 0 8px rgba(99,102,241,0.3); }
    .view-toggle-btn:hover:not(.active) { color: var(--text-secondary); }

    .license-filter-select {
      background: rgba(0,0,0,0.2); border: 1px solid var(--border-color);
      border-radius: 8px; padding: 0.4rem 0.6rem;
      color: var(--text-primary); font-size: 0.75rem;
      font-family: var(--font-sans); width: 100%; outline: none; cursor: pointer;
    }
    .license-filter-select:focus { border-color: var(--accent-indigo); }
  </style>"""

content = content.replace(
    "        height: 95vh;\n      }\n    }\n  </style>",
    "        height: 95vh;\n      }\n    }\n" + css_additions,
    1
)

# 2. Add license filter in sidebar Advanced section
license_filter_html = """          <!-- License Filter -->
          <div style="border-top: 1px solid rgba(255, 255, 255, 0.03); padding-top: 0.75rem;">
            <h3 style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; font-weight: bold; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.3rem;">
              📜 License Filter
            </h3>
            <select id="licenseFilter" class="license-filter-select">
              <option value="all">All Licenses</option>
              <option value="apache-2.0">Apache 2.0</option>
              <option value="mit">MIT</option>
              <option value="llama3.2">Llama 3.2</option>
              <option value="llama3.1">Llama 3.1</option>
              <option value="llama3">Llama 3</option>
              <option value="llama2">Llama 2</option>
              <option value="llama3.3">Llama 3.3</option>
              <option value="gemma">Gemma</option>
              <option value="qwen">Qwen</option>
              <option value="deepseek">DeepSeek</option>
              <option value="cc-by-4.0">CC-BY-4.0</option>
              <option value="cc-by-nc-4.0">CC-BY-NC-4.0</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <!-- Live API Import (Live Model Hub) -->"""

content = content.replace(
    '          <!-- Live API Import (Live Model Hub) -->',
    license_filter_html,
    1
)

# 3. Add view toggle + compare button in controls bar
controls_bar_replace = """        <div class="sort-wrapper" style="display: flex; align-items: center; gap: 0.75rem;">
          <!-- View Toggle -->
          <div class="view-toggle-group">
            <button class="view-toggle-btn active" data-view="table">📋 Table</button>
            <button class="view-toggle-btn" data-view="scatter">📊 Scatter</button>
          </div>
          
          <!-- Compare Button -->
          <button id="btnCompare" class="btn-compare">
            🔄 Compare (<span id="compareCount">0</span>)
          </button>

          <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">Sort By:</span>
          <select id="sortSelect" class="sort-select" style="background: rgba(0,0,0,0.25); border: 1px solid var(--border-color); border-radius: 12px; padding: 0.55rem 2rem 0.55rem 0.75rem; color: #fff; font-size: 0.825rem; font-weight: 600; cursor: pointer; outline: none; transition: all 0.2s; -webkit-appearance: none; -moz-appearance: none; appearance: none; background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right%200.75rem%20center; background-size: 0.65rem%20auto; min-width: 180px;">
            <option value="score" selected>Overall Fit Score</option>
            <option value="quality">Model Intelligence (General)</option>
            <option value="speed">Generation Speed (tok/s)</option>
            <option value="vram">Memory Required (GB)</option>
            <option value="params">Parameter Size (B)</option>
            <option value="context">GPU Load Ratio</option>
          </select>
        </div>"""

old_controls = """        <div class="sort-wrapper" style="display: flex; align-items: center; gap: 0.75rem;">
          <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">Sort By:</span>
          <select id="sortSelect" class="sort-select" style="background: rgba(0,0,0,0.25); border: 1px solid var(--border-color); border-radius: 12px; padding: 0.55rem 2rem 0.55rem 0.75rem; color: #fff; font-size: 0.825rem; font-weight: 600; cursor: pointer; outline: none; transition: all 0.2s; -webkit-appearance: none; -moz-appearance: none; appearance: none; background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right%200.75rem%20center; background-size: 0.65rem%20auto; min-width: 180px;">
            <option value="score" selected>Overall Fit Score</option>
            <option value="quality">Model Intelligence (General)</option>
            <option value="speed">Generation Speed (tok/s)</option>
            <option value="vram">Memory Required (GB)</option>
            <option value="params">Parameter Size (B)</option>
            <option value="context">GPU Load Ratio</option>
          </select>
        </div>"""

content = content.replace(old_controls, controls_bar_replace, 1)

# 4. Update table header and add scatter view
old_table_section = """      <!-- Models List Container -->
      <div class="models-table-container">
        <table class="models-table">
          <thead>
            <tr>
              <th data-sort="score" style="cursor:pointer;">Model Name & Description</th>
              <th data-sort="vram" style="cursor:pointer;">Best Fitting Quant</th>
              <th data-sort="vram" style="cursor:pointer;">Hardware Allocation</th>
              <th data-sort="speed" style="cursor:pointer;">Est. Gen Speed</th>
              <th data-sort="quality" style="cursor:pointer;">Intelligence</th>
              <th data-sort="score" style="width: 160px; cursor:pointer;">Overall Fit</th>
            </tr>
          </thead>
          <tbody id="modelsTableBody">
            <!-- Populated by JS -->
          </tbody>
        </table>
      </div>"""

new_table_section = """      <!-- Models List Container -->
      <div id="tableView">
        <div class="models-table-container">
          <table class="models-table">
            <thead>
              <tr>
                <th class="checkbox-col"><input type="checkbox" id="selectAllCheckbox" class="compare-checkbox" title="Select all for comparison"></th>
                <th data-sort="score" style="cursor:pointer;">Model Name & Description</th>
                <th data-sort="vram" style="cursor:pointer;">Best Fitting Quant</th>
                <th data-sort="vram" style="cursor:pointer;">Hardware Allocation</th>
                <th data-sort="speed" style="cursor:pointer;">Est. Gen Speed</th>
                <th data-sort="quality" style="cursor:pointer;">
                  <div style="display: flex; align-items: center; gap: 0.4rem;">
                    <span>Intelligence</span>
                    <button id="btnExpandBench" class="btn-expand-bench">🔬 Benchmarks</button>
                  </div>
                </th>
                <th data-sort="score" style="width: 160px; cursor:pointer;">Overall Fit</th>
              </tr>
            </thead>
            <tbody id="modelsTableBody">
              <!-- Populated by JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Scatter Plot View (hidden by default) -->
      <div id="scatterView" class="scatter-container" style="display: none;">
        <div class="scatter-controls">
          <span class="title">📊 Speed vs Quality — Model Landscape</span>
          <span style="font-size:0.7rem; color:var(--text-muted);">X: Intelligence Score · Y: Generation Speed (tok/s) · Color: Quant Type</span>
        </div>
        <canvas id="scatterCanvas"></canvas>
        <div id="scatterLegend" class="scatter-legend"></div>
        <div id="scatterTooltip" class="scatter-tooltip"></div>
      </div>"""

content = content.replace(old_table_section, new_table_section, 1)

# 5. Add comparison modal before detail modal
compare_modal_html = """  <!-- COMPARISON MODAL -->
  <div class="modal-overlay" id="compareModal" style="z-index: 1000;">
    <div class="modal-container" style="max-width: 1100px;">
      
      <div class="modal-header">
        <div class="modal-header-info">
          <h2>🔄 Side-by-Side Model Comparison</h2>
          <p>Compare selected models across all metrics</p>
        </div>
        <button class="btn-close" id="compareModalClose">✕</button>
      </div>

      <div class="modal-content compare-modal-content">
        <div id="compareModalBody">
          <!-- Populated by JS -->
        </div>
      </div>

    </div>
  </div>

  <!-- DETAIL DRAWER MODAL -->"""

content = content.replace(
    "  <!-- DETAIL DRAWER MODAL -->",
    compare_modal_html,
    1
)

# 6. Now add all the JS changes
# 6a. Add new state variables after the existing state section
old_state = """    // ACTIVE APPLICATION STATE
    let appDb = DEFAULT_CACHE;
    let selectedUsecase = "chat";
    let activeHardware = {};
    let activeModalModel = null;
    let activeSelectedGpuId = "rtx_4090";
    let leaderboardDb = {};
    let externalGpuDb = [];

    // Persistent evaluation provider switches"""

new_state = """    // ACTIVE APPLICATION STATE
    let appDb = DEFAULT_CACHE;
    let selectedUsecase = "chat";
    let activeHardware = {};
    let activeModalModel = null;
    let activeSelectedGpuId = "rtx_4090";
    let leaderboardDb = {};
    let externalGpuDb = [];

    // Comparison & Benchmarks state
    let selectedModels = [];
    let benchmarksExpanded = false;
    let viewMode = "table";

    // Persistent evaluation provider switches"""

content = content.replace(old_state, new_state, 1)

# 6b. Add new DOM references after existing ones (after const vramCanvas)
old_dom_end = """    const chartContextTarget = document.getElementById("chartContextTarget");
    const vramCanvas = document.getElementById("vramChart");

    // INITIALIZATION"""

new_dom_end = """    const chartContextTarget = document.getElementById("chartContextTarget");
    const vramCanvas = document.getElementById("vramChart");

    // New feature DOM references
    const btnCompare = document.getElementById("btnCompare");
    const compareCount = document.getElementById("compareCount");
    const compareModal = document.getElementById("compareModal");
    const compareModalBody = document.getElementById("compareModalBody");
    const compareModalClose = document.getElementById("compareModalClose");
    const selectAllCheckbox = document.getElementById("selectAllCheckbox");
    const btnExpandBench = document.getElementById("btnExpandBench");
    const scatterCanvas = document.getElementById("scatterCanvas");
    const scatterTooltip = document.getElementById("scatterTooltip");
    const scatterLegend = document.getElementById("scatterLegend");
    const licenseFilter = document.getElementById("licenseFilter");
    const tableView = document.getElementById("tableView");
    const scatterView = document.getElementById("scatterView");

    // INITIALIZATION"""

content = content.replace(old_dom_end, new_dom_end, 1)

# 6c. Add license filter logic in renderDashboard model loop
# After the search/filter matching section, add license filter
old_filter_section = """        // Filter out if search keyword is present
        const matchesSearch = 
          model.name.toLowerCase().includes(searchVal) ||
          model.developer.toLowerCase().includes(searchVal) ||
          model.description.toLowerCase().includes(searchVal) ||
          model.model_id.toLowerCase().includes(searchVal) ||
          model.tags.some(t => t.toLowerCase().includes(searchVal));

        if (matchesSearch && bestSim) {"""

new_filter_section = """        // Filter by license
        const licenseVal = (model.license || "other").toLowerCase();
        const activeLicenseFilter = licenseFilter ? licenseFilter.value : "all";
        const matchesLicense = activeLicenseFilter === "all" || licenseVal === activeLicenseFilter;

        // Filter out if search keyword is present
        const matchesSearch = 
          model.name.toLowerCase().includes(searchVal) ||
          model.developer.toLowerCase().includes(searchVal) ||
          model.description.toLowerCase().includes(searchVal) ||
          model.model_id.toLowerCase().includes(searchVal) ||
          model.tags.some(t => t.toLowerCase().includes(searchVal));

        if (matchesSearch && bestSim && matchesLicense) {"""

content = content.replace(old_filter_section, new_filter_section, 1)

# 6d. Replace the entire render row logic (from the `computedResults.forEach` to the end of renderDashboard)
old_render_rows = """      // RENDER ROWS TO BODY
      modelsTableBody.innerHTML = "";
      
      if (computedResults.length === 0) {
        modelsTableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 3rem;">No models matched your active filters or query. Try adjusting VRAM limits or format settings.</td></tr>`;
        return;
      }

      computedResults.forEach(res => {
        const tr = document.createElement("tr");
        
        // Fit status class
        let badgeColorClass = "red";
        let badgeText = "Out of Memory";
        if (res.bestSim.fitStatus === "VRAM") {
          badgeColorClass = "green";
          badgeText = "Fits VRAM";
        } else if (res.bestSim.fitStatus === "RAM") {
          badgeColorClass = "amber";
          badgeText = "Offloads to RAM";
        }

        // Developer class tag
        const devClass = res.model.developer.toLowerCase().replace(" ", "");

        // Build tags markup
        const tagsMarkup = res.model.tags.map(t => `<span class="tag-badge">${t}</span>`).join("");

        // Build speed cell
        const speedText = res.bestSim.fitStatus === "OOM" 
          ? `<span style="color: var(--fit-red); font-weight:600;">OOM</span>` 
          : `<span class="tps-value">${res.bestSim.speedTPS.toFixed(1)}</span> <span class="tps-label">tok/s</span>`;

        // Intelligence / HF LLM Leaderboard
        const dynamicBaseQuality = getDynamicUseCaseScore(res.model, selectedUsecase);
        const finalIntelligence = (dynamicBaseQuality - QUANT_QUALITY_LOSS[res.bestQuantKey]).toFixed(1);
        const lossPercent = QUANT_QUALITY_LOSS[res.bestQuantKey];

        tr.innerHTML = `
          <td>
            <div class="td-model-info">
              <div class="model-name-row">
                <span>${res.model.name}</span>
                <span class="dev-badge ${devClass}">${res.model.developer}</span>
              </div>
              <div class="model-desc-row">${res.model.description}</div>
              <div class="tags-container">${tagsMarkup}</div>
            </div>
          </td>
          <td>
            <div class="quant-pill">${res.bestQuantKey}</div>
            <div style="font-size:0.7rem; color: var(--text-muted); margin-top:0.25rem;">${res.bestSim.weightsSizeGB.toFixed(1)} GB Weights</div>
          </td>
          <td>
            <div class="fit-status-wrapper">
              <span class="fit-badge ${badgeColorClass}">
                <span style="width: 8px; height:8px; border-radius:50%; background-color: currentColor;"></span>
                ${badgeText}
              </span>
              <span class="fit-meta">${res.bestSim.totalVramGB.toFixed(1)} GB Need / ${(res.bestSim.gpuRatio * 100).toFixed(0)}% GPU</span>
            </div>
          </td>
          <td>
            ${speedText}
          </td>
          <td>
            <div class="quality-ring-wrapper">
              <span class="quality-number">${finalIntelligence}</span>
              ${lossPercent > 0 ? `<span class="quality-loss-tag">-${lossPercent.toFixed(1)}%</span>` : ''}
            </div>
          </td>
          <td>
            <div class="score-container">
              <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: ${Math.min(res.fitScore, 100)}%;"></div>
              </div>
              <span class="score-percent">${res.fitScore}%</span>
            </div>
          </td>
        `;

        tr.addEventListener("click", () => {
          openDetailModal(res.model);
        });

        modelsTableBody.appendChild(tr);
      });
    }"""

new_render_rows = """      // Handle view mode
      if (viewMode === "scatter") {
        tableView.style.display = "none";
        scatterView.style.display = "block";
        drawScatterPlot(computedResults);
        return;
      } else {
        tableView.style.display = "block";
        scatterView.style.display = "none";
      }

      // RENDER ROWS TO BODY
      modelsTableBody.innerHTML = "";
      
      const colCount = benchmarksExpanded ? 7 + BENCHMARK_KEYS.length : 7;
      if (computedResults.length === 0) {
        modelsTableBody.innerHTML = `<tr><td colspan="${colCount}" style="text-align: center; color: var(--text-muted); padding: 3rem;">No models matched your active filters or query. Try adjusting VRAM limits or format settings.</td></tr>`;
        return;
      }

      computedResults.forEach(res => {
        const tr = document.createElement("tr");
        
        // Fit status class
        let badgeColorClass = "red";
        let badgeText = "Out of Memory";
        if (res.bestSim.fitStatus === "VRAM") {
          badgeColorClass = "green";
          badgeText = "Fits VRAM";
        } else if (res.bestSim.fitStatus === "RAM") {
          badgeColorClass = "amber";
          badgeText = "Offloads to RAM";
        }

        // Developer class tag
        const devClass = res.model.developer.toLowerCase().replace(" ", "");

        // Build tags markup
        const tagsMarkup = res.model.tags.map(t => `<span class="tag-badge">${t}</span>`).join("");

        // Build speed cell
        const speedText = res.bestSim.fitStatus === "OOM" 
          ? `<span style="color: var(--fit-red); font-weight:600;">OOM</span>` 
          : `<span class="tps-value">${res.bestSim.speedTPS.toFixed(1)}</span> <span class="tps-label">tok/s</span>`;

        // Intelligence / HF LLM Leaderboard
        const dynamicBaseQuality = getDynamicUseCaseScore(res.model, selectedUsecase);
        const finalIntelligence = (dynamicBaseQuality - QUANT_QUALITY_LOSS[res.bestQuantKey]).toFixed(1);
        const lossPercent = QUANT_QUALITY_LOSS[res.bestQuantKey];

        // Check if model is selected for comparison
        const isChecked = selectedModels.includes(res.model.model_id);
        
        // License badge
        const lic = res.model.license || "other";
        const licClass = "license-" + lic.replace(/[.]/g, "\\\\.").toLowerCase();
        const licDisplay = lic.replace(/-/g, " ").replace(/\\d+\\.\\d+/, '').trim() || lic;

        // Build benchmark columns if expanded
        let benchCellsHtml = "";
        if (benchmarksExpanded) {
          const metrics = (res.model.benchmarks && res.model.benchmarks.metrics) || {};
          BENCHMARK_KEYS.forEach(key => {
            const val = metrics[key];
            let colorClass = "score-mid";
            if (val !== undefined && val !== null) {
              if (val >= 60) colorClass = "score-good";
              else if (val < 30) colorClass = "score-bad";
            }
            const displayVal = val !== undefined && val !== null ? val.toFixed(1) : "—";
            benchCellsHtml += `<td class="benchmark-cell ${colorClass}">${displayVal}</td>`;
          });
        }

        tr.innerHTML = `
          <td class="checkbox-col">
            <input type="checkbox" class="compare-checkbox" data-model-id="${res.model.model_id}" ${isChecked ? 'checked' : ''}>
          </td>
          <td>
            <div class="td-model-info">
              <div class="model-name-row">
                <span>${res.model.name}</span>
                <span class="dev-badge ${devClass}">${res.model.developer}</span>
                <span class="license-badge ${licClass}">${licDisplay}</span>
              </div>
              <div class="model-desc-row">${res.model.description}</div>
              <div class="tags-container">${tagsMarkup}</div>
            </div>
          </td>
          <td>
            <div class="quant-pill">${res.bestQuantKey}</div>
            <div style="font-size:0.7rem; color: var(--text-muted); margin-top:0.25rem;">${res.bestSim.weightsSizeGB.toFixed(1)} GB Weights</div>
          </td>
          <td>
            <div class="fit-status-wrapper">
              <span class="fit-badge ${badgeColorClass}">
                <span style="width: 8px; height:8px; border-radius:50%; background-color: currentColor;"></span>
                ${badgeText}
              </span>
              <span class="fit-meta">${res.bestSim.totalVramGB.toFixed(1)} GB Need / ${(res.bestSim.gpuRatio * 100).toFixed(0)}% GPU</span>
            </div>
          </td>
          <td>
            ${speedText}
          </td>
          <td>
            <div class="quality-ring-wrapper">
              <span class="quality-number">${finalIntelligence}</span>
              ${lossPercent > 0 ? `<span class="quality-loss-tag">-${lossPercent.toFixed(1)}%</span>` : ''}
            </div>
          </td>
          ${benchCellsHtml}
          <td>
            <div class="score-container">
              <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: ${Math.min(res.fitScore, 100)}%;"></div>
              </div>
              <span class="score-percent">${res.fitScore}%</span>
            </div>
          </td>
        `;

        tr.addEventListener("click", (e) => {
          if (e.target.type !== 'checkbox') {
            openDetailModal(res.model);
          }
        });

        // Checkbox handler
        const cb = tr.querySelector(".compare-checkbox");
        cb.addEventListener("change", (e) => {
          e.stopPropagation();
          const mid = e.target.dataset.modelId;
          if (e.target.checked) {
            if (!selectedModels.includes(mid) && selectedModels.length < 6) {
              selectedModels.push(mid);
            }
          } else {
            selectedModels = selectedModels.filter(id => id !== mid);
          }
          updateCompareButton();
        });

        modelsTableBody.appendChild(tr);
      });
    }"""

content = content.replace(old_render_rows, new_render_rows, 1)

# 6e. Add BENCHMARK_KEYS constant and new functions before "FIRE EVERYTHING UP"
old_fire = """    // FIRE EVERYTHING UP
    window.addEventListener("DOMContentLoaded", init);"""

new_before_fire = """    // Benchmark column definitions
    const BENCHMARK_KEYS = [
      { key: "gpqa", short: "GPQA", full: "PhD Reasoning" },
      { key: "mmlu_pro", short: "MMLU", full: "Expert Knowledge" },
      { key: "math_lvl5", short: "MATH5", full: "Lvl 5 Algebra" },
      { key: "bbh", short: "BBH", full: "Multi-Step" },
      { key: "ifeval", short: "IFEVAL", full: "Instr. Follow" },
      { key: "musr", short: "MUSR", full: "Multi-Step Reas." },
      { key: "benchlm_coding", short: "CODE", full: "Coding" },
      { key: "benchlm_reasoning", short: "REAS", full: "Reasoning" },
      { key: "benchlm_instruction", short: "INST", full: "Instruction" },
      { key: "benchlm_math", short: "MATH", full: "Math" },
      { key: "benchlm_knowledge", short: "KNOW", full: "Knowledge" },
      { key: "benchlm_multilingual", short: "MULTI", full: "Multilingual" },
      { key: "livebench", short: "LIVE", full: "LiveBench" },
      { key: "evalplus_humaneval", short: "HE+", full: "HumanEval+" },
      { key: "evalplus_mbpp", short: "MBPP+", full: "MBPP+" }
    ];

    // UPDATE EXPANDED BENCHMARK COLUMNS
    function updateBenchmarkColumns() {
      const table = document.querySelector(".models-table");
      if (!table) return;
      const header = table.querySelector("thead tr");
      if (!header) return;
      
      // Remove existing expanded benchmark headers
      header.querySelectorAll(".benchmark-col-header").forEach(el => el.remove());
      
      if (benchmarksExpanded) {
        const qualityTh = header.querySelector("th:nth-child(6)");
        BENCHMARK_KEYS.forEach(bk => {
          const th = document.createElement("th");
          th.style.cursor = "pointer";
          th.innerHTML = `<div class="benchmark-col-header"><span class="short">${bk.short}</span><span class="full">${bk.full}</span></div>`;
          if (qualityTh && qualityTh.nextSibling) {
            header.insertBefore(th, qualityTh.nextSibling);
          } else {
            header.appendChild(th);
          }
        });
        btnExpandBench.textContent = "🔬 Collapse";
      } else {
        btnExpandBench.textContent = "🔬 Benchmarks";
      }
    }

    // UPDATE COMPARE BUTTON STATE
    function updateCompareButton() {
      const count = selectedModels.length;
      compareCount.textContent = count;
      if (count >= 2) {
        btnCompare.classList.add("active");
      } else {
        btnCompare.classList.remove("active");
      }
    }

    // OPEN COMPARISON MODAL
    function openCompareModal() {
      if (selectedModels.length < 2) return;
      
      const models = selectedModels.map(mid => appDb.models.find(m => m.model_id === mid)).filter(Boolean);
      if (models.length < 2) return;
      
      compareModal.style.display = "flex";
      
      // Define all metrics to compare
      const metricRows = [
        { label: "Parameters", get: m => m.parameters.toFixed(1) + " B" },
        { label: "Active Params (MoE)", get: m => (m.active_parameters || m.parameters).toFixed(1) + " B" },
        { label: "Quality Score", get: m => (m.quality_score || 0).toFixed(1) },
        { label: "Layers", get: m => m.config.num_layers },
        { label: "Hidden Size", get: m => m.config.hidden_size },
        { label: "Attention Heads", get: m => m.config.num_attn_heads },
        { label: "KV Heads", get: m => m.config.num_kv_heads || "—" },
        { label: "License", get: m => m.license || "—" }
      ];
      
      // Add all benchmarks
      const metrics = models[0].benchmarks && models[0].benchmarks.metrics || {};
      Object.keys(metrics).sort().forEach(key => {
        metricRows.push({
          label: key.replace(/_/g, " ").replace(/\\b\\w/g, l => l.toUpperCase()),
          get: m => {
            const v = (m.benchmarks && m.benchmarks.metrics && m.benchmarks.metrics[key]);
            return v !== undefined && v !== null ? v.toFixed(1) + "%" : "—";
          }
        });
      });
      
      // Also add speed/VRAM simulation for each model
      const activeCtx = parseInt(contextRange.value);
      metricRows.push(
        { label: "Speed (Q4_K_M)", get: m => {
          const sim = simulateInference(m, "Q4_K_M", activeCtx);
          return sim.fitStatus !== "OOM" ? sim.speedTPS.toFixed(1) + " tok/s" : "OOM";
        }},
        { label: "VRAM (Q4_K_M)", get: m => {
          const sim = simulateInference(m, "Q4_K_M", activeCtx);
          return sim.totalVramGB.toFixed(1) + " GB";
        }},
        { label: "Benchmark Status", get: m => (m.benchmarks && m.benchmarks.status) || "estimated" }
      );
      
      const modelKeys = models.map((m, i) => ({ id: m.model_id, name: m.name, dev: m.developer }));
      
      let html = `<div class="compare-table-wrap"><table class="compare-table"><thead><tr>
        <th>Metric</th>`;
      
      models.forEach(m => {
        html += `<th><div class="compare-model-name"><span class="name">${m.name}</span><span class="meta">${m.developer}</span></div></th>`;
      });
      
      html += `</tr></thead><tbody>`;
      
      metricRows.forEach(row => {
        html += `<tr><td class="metric-label">${row.label}</td>`;
        models.forEach(m => {
          let val = row.get(m);
          // Color code numeric values
          let cls = "";
          if (typeof val === 'string' && val.includes('%')) {
            const num = parseFloat(val);
            if (num >= 70) cls = "score-good";
            else if (num >= 40) cls = "score-mid";
            else cls = "score-bad";
          }
          html += `<td class="${cls}">${val}</td>`;
        });
        html += `</tr>`;
      });
      
      html += `</tbody></table></div>`;
      
      compareModalBody.innerHTML = html;
    }

    // DRAW SCATTER PLOT
    function drawScatterPlot(computedResults) {
      const canvas = scatterCanvas;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      
      const w = rect.width;
      const h = rect.height;
      
      ctx.clearRect(0, 0, w, h);
      
      const padL = 60;
      const padR = 30;
      const padT = 30;
      const padB = 40;
      
      const plotW = w - padL - padR;
      const plotH = h - padT - padB;
      
      // Prepare data points
      const points = [];
      computedResults.forEach(res => {
        const quality = getDynamicUseCaseScore(res.model, selectedUsecase) - QUANT_QUALITY_LOSS[res.bestQuantKey];
        const speed = res.bestSim.speedTPS;
        if (quality > 0 && speed > 0) {
          points.push({
            x: quality,
            y: speed,
            model: res.model,
            quantKey: res.bestQuantKey,
            name: res.model.name,
            dev: res.model.developer
          });
        }
      });
      
      if (points.length === 0) return;
      
      // Find bounds with margins
      let minX = Math.min(...points.map(p => p.x)) * 0.9;
      let maxX = Math.max(...points.map(p => p.x)) * 1.1;
      let minY = 0;
      let maxY = Math.max(...points.map(p => p.y)) * 1.15;
      
      minX = Math.max(0, minX);
      maxX = Math.min(100, maxX);
      
      // Quant color palette
      const QUANT_COLORS = {
        "Q2_K": "#ef4444", "Q3_K_M": "#f97316", "Q4_0": "#eab308",
        "Q4_K_M": "#22c55e", "Q5_K_M": "#06b6d4", "Q6_K": "#6366f1",
        "Q8_0": "#a855f7", "fp16": "#ec4899"
      };
      
      function mapX(val) { return padL + (val - minX) / (maxX - minX) * plotW; }
      function mapY(val) { return padT + plotH * (1 - (val - minY) / (maxY - minY)); }
      
      // Draw grid
      ctx.strokeStyle = "rgba(255,255,255,0.05)";
      ctx.lineWidth = 1;
      ctx.fillStyle = "rgba(148,163,184,0.4)";
      ctx.font = "9px var(--font-sans)";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      
      for (let i = 0; i <= 5; i++) {
        const valY = minY + (maxY - minY) * (i / 5);
        const y = mapY(valY);
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(w - padR, y);
        ctx.stroke();
        ctx.fillText(valY.toFixed(0) + " t/s", padL - 5, y);
      }
      
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      for (let i = 0; i <= 10; i++) {
        const valX = minX + (maxX - minX) * (i / 10);
        const x = mapX(valX);
        ctx.beginPath();
        ctx.moveTo(x, padT);
        ctx.lineTo(x, h - padB);
        ctx.stroke();
        ctx.fillStyle = "rgba(148,163,184,0.5)";
        ctx.fillText(valX.toFixed(0) + "%", x, h - padB + 5);
        ctx.fillStyle = "rgba(148,163,184,0.4)";
      }
      
      // Axes labels
      ctx.fillStyle = "rgba(148,163,184,0.6)";
      ctx.font = "10px var(--font-sans)";
      ctx.textAlign = "center";
      ctx.fillText("Intelligence Quality Score (%)", padL + plotW / 2, h - 2);
      ctx.save();
      ctx.translate(10, padT + plotH / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.fillText("Generation Speed (tok/s)", 0, 0);
      ctx.restore();
      
      // Draw data points
      const dotRadius = 5;
      const pointData = [];
      
      points.forEach((p, idx) => {
        const px = mapX(p.x);
        const py = mapY(p.y);
        const color = QUANT_COLORS[p.quantKey] || "#6366f1";
        
        // Glow
        ctx.shadowColor = color;
        ctx.shadowBlur = 6;
        
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(px, py, dotRadius, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.shadowBlur = 0;
        
        // White outline
        ctx.strokeStyle = "rgba(255,255,255,0.3)";
        ctx.lineWidth = 0.5;
        ctx.stroke();
        
        pointData.push({ px, py, ...p });
      });
      
      // Build legend
      const usedQuants = [...new Set(points.map(p => p.quantKey))];
      scatterLegend.innerHTML = usedQuants.map(q => 
        `<span class="scatter-legend-item">
          <span class="scatter-legend-dot" style="background:${QUANT_COLORS[q] || '#6366f1'}"></span>
          ${q}
        </span>`
      ).join("");
      
      // Hover interaction
      const tooltip = scatterTooltip;
      let hoverTimeout;
      
      function handleScatterMove(e) {
        const rect2 = canvas.getBoundingClientRect();
        const mx = e.clientX - rect2.left;
        const my = e.clientY - rect2.top;
        
        let closest = null;
        let minDist = 20;
        
        pointData.forEach(p => {
          const dist = Math.sqrt((mx - p.px) ** 2 + (my - p.py) ** 2);
          if (dist < minDist) {
            minDist = dist;
            closest = p;
          }
        });
        
        if (closest) {
          canvas.style.cursor = "pointer";
          tooltip.style.display = "block";
          tooltip.style.left = (closest.px + 15) + "px";
          tooltip.style.top = (closest.py - 10) + "px";
          
          // Ensure tooltip stays in bounds
          if (parseInt(tooltip.style.left) + 240 > w) {
            tooltip.style.left = (closest.px - 250) + "px";
          }
          
          tooltip.innerHTML = `
            <div class="model-name">${closest.name}</div>
            <div class="detail">Developer: ${closest.dev}</div>
            <div class="detail">Quality: <span>${closest.x.toFixed(1)}%</span></div>
            <div class="detail">Speed: <span>${closest.y.toFixed(1)} tok/s</span></div>
            <div class="detail">Quant: <span>${closest.quantKey}</span></div>
          `;
        } else {
          tooltip.style.display = "none";
          canvas.style.cursor = "crosshair";
        }
      }
      
      canvas.onmousemove = handleScatterMove;
      canvas.onmouseleave = () => {
        tooltip.style.display = "none";
        canvas.style.cursor = "crosshair";
      };
    }

    // FIRE EVERYTHING UP
    window.addEventListener("DOMContentLoaded", init);"""

content = content.replace(old_fire, new_before_fire, 1)

# 6f. Add new event listeners in setupEventListeners
# Insert after the status modal close handler

old_status_close = """        });\n      }\n\n      window.addEventListener(\"click\", (e) => {\n        if (e.target === detailModal) {\n          detailModal.style.display = \"none\";\n          activeModalModel = null;\n        }\n      });\n\n      window.addEventListener(\"click\", (e) => {\n        if (e.target === detailModal) {\n          detailModal.style.display = \"none\";\n          activeModalModel = null;\n        }\n      });"""

new_status_close_ext = """        });\n      }\n\n      window.addEventListener(\"click\", (e) => {\n        if (e.target === detailModal) {\n          detailModal.style.display = \"none\";\n          activeModalModel = null;\n        }\n      });\n\n      window.addEventListener(\"click\", (e) => {\n        if (e.target === detailModal) {\n          detailModal.style.display = \"none\";\n          activeModalModel = null;\n        }\n      });\n
      // View toggle buttons
      document.querySelectorAll(\".view-toggle-btn\").forEach(btn => {
        btn.addEventListener(\"click\", () => {
          document.querySelectorAll(\".view-toggle-btn\").forEach(b => b.classList.remove(\"active\"));
          btn.classList.add(\"active\");
          viewMode = btn.dataset.view;
          renderDashboard();
        });
      });

      // Compare button
      btnCompare.addEventListener(\"click\", () => {
        openCompareModal();
      });

      // Compare modal close
      compareModalClose.addEventListener(\"click\", () => {
        compareModal.style.display = \"none\";
      });
      window.addEventListener(\"click\", (e) => {
        if (e.target === compareModal) {
          compareModal.style.display = \"none\";
        }
      });

      // Select all checkbox
      selectAllCheckbox.addEventListener(\"change\", (e) => {
        const checked = e.target.checked;
        document.querySelectorAll(\".compare-checkbox\").forEach(cb => {
          if (cb.id !== \"selectAllCheckbox\") {
            cb.checked = checked;
            const mid = cb.dataset.modelId;
            if (checked && mid) {
              if (!selectedModels.includes(mid) && selectedModels.length < 6) {
                selectedModels.push(mid);
              }
            } else if (!checked && mid) {
              selectedModels = selectedModels.filter(id => id !== mid);
            }
          }
        });
        updateCompareButton();
      });

      // Expand benchmarks button
      btnExpandBench.addEventListener(\"click\", (e) => {
        e.stopPropagation();
        benchmarksExpanded = !benchmarksExpanded;
        updateBenchmarkColumns();
        renderDashboard();
      });

      // License filter
      licenseFilter.addEventListener(\"change\", () => {
        renderDashboard();
      });"""

content = content.replace(old_status_close, new_status_close_ext, 1)

# Write the file
with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as f:
    f.write(content)

print("Done! File written successfully.")
print(f"Size: {os.path.getsize(os.path.join(root, 'index.html'))} bytes")
