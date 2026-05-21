# ModelSelector - LLM Optimizer & Hardware Simulator

> **Live App:** [https://harrytyp.github.io/modelselector/](https://harrytyp.github.io/modelselector/)

An interactive, high-fidelity browser-side simulator that estimates memory allocation, context scaling, and generation throughput (tokens/s) for any given local LLM quantization under specific hardware constraints.

The entire system is powered by **dynamic, live external APIs** to build the hardware database, model metadata registries, and task-performance quality indexes in real-time.

---

## System Architecture & Data Flow

This diagram illustrates the full data pipeline, from browser-side simulation through live Hugging Face, Open LLM Leaderboard, and GPU database APIs, down to the physics engine that computes VRAM allocation and tokens/s:

![System Architecture](https://quickchart.io/graphviz?graph=digraph%20Architecture%20%7B%0A%20%20%20%20node%20%5Bstyle%3Dfilled%2C%20fontname%3D%22Helvetica%22%2C%20fontsize%3D9%5D%0A%20%20%20%20Browser%20%5Blabel%3D%22Browser%20Client%5Cnhttp%3A//localhost%3A8000/%22%2C%20fillcolor%3D%22%236366f1%22%2C%20fontcolor%3Dwhite%5D%0A%20%20%20%20HF%20%5Blabel%3D%22Hugging%20Face%5CnAPIs%22%2C%20fillcolor%3D%22%23da552f%22%2C%20fontcolor%3Dwhite%5D%0A%20%20%20%20OLL%20%5Blabel%3D%22Open%20LLM%5CnLeaderboard%22%2C%20fillcolor%3D%22%233b82f6%22%2C%20fontcolor%3Dwhite%5D%0A%20%20%20%20Wiki%20%5Blabel%3D%22Wikipedia%5CnGPU%20API%22%2C%20fillcolor%3D%22%2310b981%22%2C%20fontcolor%3Dwhite%5D%0A%0A%20%20%20%20UI%20%5Blabel%3D%22Glassmorphic%20UI%22%2C%20shape%3Dbox%2C%20fillcolor%3D%22%23f8fafc%22%2C%20color%3Dblack%5D%0A%20%20%20%20State%20%5Blabel%3D%22Active%20State%22%2C%20shape%3Dbox%2C%20fillcolor%3D%22%23f8fafc%22%2C%20color%3Dblack%5D%0A%20%20%20%20Calc%20%5Blabel%3D%22Physics%20Engine%22%2C%20shape%3Dbox%2C%20fillcolor%3D%22%23f8fafc%22%2C%20color%3Dblack%5D%0A%20%20%20%20LS%20%5Blabel%3D%22LocalSync%22%2C%20shape%3Dbox%2C%20fillcolor%3D%22%23f8fafc%22%2C%20color%3Dblack%5D%0A%0A%20%20%20%20HFS%20%5Blabel%3D%22HF%20Search%22%2C%20shape%3Dellipse%2C%20fillcolor%3D%22%23fef3c7%22%5D%0A%20%20%20%20HFM%20%5Blabel%3D%22HF%20Meta%22%2C%20shape%3Dellipse%2C%20fillcolor%3D%22%23fef3c7%22%5D%0A%20%20%20%20HFC%20%5Blabel%3D%22HF%20Config%22%2C%20shape%3Dellipse%2C%20fillcolor%3D%22%23fef3c7%22%5D%0A%20%20%20%20HFD%20%5Blabel%3D%22HF%20Leaderboard%22%2C%20shape%3Dellipse%2C%20fillcolor%3D%22%23fef3c7%22%5D%0A%0A%20%20%20%20WikiGPU%20%5Blabel%3D%22voidful%20CDN%22%2C%20shape%3Dellipse%2C%20fillcolor%3D%22%23fef3c7%22%5D%0A%0A%20%20%20%20Browser%20-%3E%20UI%20%5Blabel%3D%22render%22%5D%0A%20%20%20%20Browser%20-%3E%20State%20%5Blabel%3D%22persist%22%5D%0A%20%20%20%20Browser%20-%3E%20LS%20%5Blabel%3D%22read/write%22%5D%0A%20%20%20%20HF%20-%3E%20HFS%20-%3E%20UI%20%5Blabel%3D%22keywords%22%5D%0A%20%20%20%20HF%20-%3E%20HFM%20-%3E%20State%20%5Blabel%3D%22metadata%22%5D%0A%20%20%20%20HF%20-%3E%20HFC%20-%3E%20Calc%20%5Blabel%3D%22config.json%22%5D%0A%20%20%20%20OLL%20-%3E%20HFD%20-%3E%20State%20%5Blabel%3D%22benchmarks%22%5D%0A%20%20%20%20Wiki%20-%3E%20WikiGPU%20-%3E%20UI%20%5Blabel%3D%22specs%22%5D%0A%20%20%20%20State%20-%3E%20Calc%20%5Blabel%3D%22formulas%22%5D%0A%20%20%20%20Calc%20-%3E%20UI%20%5Blabel%3D%22charts%22%5D%0A%7D)

---

## Dynamic API Endpoints Directory

### 0. Data Sources & Live Status

All benchmark data is fetched nightly by the GitHub Actions workflow and cached in `data/cache.json`. Every value in the app shows where it came from. The cache payload includes a `sources` block with per-source status, URL, row count, and last-updated timestamp.

| Source | URL | Status | Refreshes |
|---|---|---|---|
| GGUF Model Catalog | `huggingface.co/api/models?filter=gguf` | ✅ Live | Daily 00:00 UTC |
| Open LLM Leaderboard v2 | `datasets-server.huggingface.co/rows` (dataset: open-llm-leaderboard/contents) | ✅ Live | Daily 00:00 UTC |
| BenchLM.ai | `benchlm.ai/api/data/leaderboard` | ✅ Live | Daily 00:00 UTC |
| LiveBench | `livebench.ai/table_YYYY_MM_DD.csv` | ✅ Live | Daily 00:00 UTC |
| EvalPlus | `evalplus.github.io/results.json` | ✅ Live | Daily 00:00 UTC |
| Quantization Constants | GGUF specification + llama.cpp community data | ✅ Fixed | On change |
| GPU Database (TechPowerUp) | RightNow-AI GitHub | ✅ Live | Daily 00:00 UTC |
| **Physical Speed Formula (fallback)** | bandwidth × efficiency ÷ weight-size | ⚡ Real-time | On every search |
| **Quantization Loss (fallback)** | PPL community averages (llama.cpp) | 📊 Fallback | On every search |

### 1. Hugging Face Models API (Live Keyword Search)
* **Endpoint:** `https://huggingface.co/api/models`
* **HTTP Method:** `GET`
* **Query Parameters:**
  * `search`: Keyword string (e.g. `gemma-2-2b`)
  * `filter`: Filter by tag (`gguf` used to isolate local models)
  * `sort`: Metric sorting (`downloads` used to rank popularity)
  * `direction`: Order (`-1` for descending)
  * `limit`: Max matching records (`15`)
  * `full`: Boolean (`true` returns parameter count, tags, and file trees)
* **Usage:** Performs autocomplete model matching and downloads counts lookup inside the **Live Model Hub** sidebar search.
* **Sample Fetch:**
  ```bash
  curl "https://huggingface.co/api/models?search=gemma-2-2b&filter=gguf&sort=downloads&direction=-1&limit=1&full=true"
  ```

---

### 2. Hugging Face Single Model Metadata API
* **Endpoint:** `https://huggingface.co/api/models/{model_id}`
* **HTTP Method:** `GET`
* **Usage:** Triggered when loading a specific model to extract download counts, file size lists, and safetensors weights dimensions.
* **Sample Fetch:**
  ```bash
  curl "https://huggingface.co/api/models/google/gemma-2-2b-it"
  ```

---

### 3. Hugging Face Resolve API (Transformer config.json)
* **Endpoint:** `https://huggingface.co/{model_id}/resolve/{branch}/config.json`
* **HTTP Method:** `GET`
* **Branch Fallback:** System attempts `main` branch first; if missing, falls back to `master` branch.
* **CORS Strategy:** The `/resolve/` endpoint is explicitly hosted on Hugging Face's global CDN and includes the `Access-Control-Allow-Origin: *` header, bypassing raw origin restrictions.
* **Usage:** Downloads the model's structural specifications to extract parameters used in physics equations:
  * `num_hidden_layers` / `num_layers`: Layers count (determines VRAM overhead and KV layers)
  * `hidden_size`: Dimension scaling (calculates attention matrix parameters)
  * `num_attention_heads` / `num_key_value_heads`: Handles GQA (Grouped-Query Attention) ratios used in KV cache VRAM estimates
  * `vocab_size` / `intermediate_size`: Estimates MLPs parameters
* **Sample Fetch:**
  ```bash
  curl -L "https://huggingface.co/google/gemma-2-2b-it/resolve/main/config.json"
  ```

---

### 4. Hugging Face Open LLM Leaderboard API
* **Endpoint:** `https://datasets-server.huggingface.co/rows`
* **HTTP Method:** `GET`
* **Query Parameters:**
  * `dataset`: Name of targeted leaderboard contents (`open-llm-leaderboard/contents`)
  * `config`: Config profile (`default`)
  * `split`: Targeted split (`train`)
  * `limit`: Pagination row counts (`100`)
* **Usage:** Scrapes the scientific task-performance benchmark scores of the top 100 open-source models on startup, linking verified averages directly to imported GGUF variants.
* **Sample Fetch:**
  ```bash
  curl "https://datasets-server.huggingface.co/rows?dataset=open-llm-leaderboard%2Fcontents&config=default&split=train&limit=100"
  ```

---

### 5. TechPowerUp GPU Database (RightNow-AI Dataset)
* **Endpoints:**
  * NVIDIA: `https://raw.githubusercontent.com/RightNow-AI/RightNow-GPU-Database/main/data/nvidia/all.json`
  * AMD: `https://raw.githubusercontent.com/RightNow-AI/RightNow-GPU-Database/main/data/amd/all.json`
  * Intel: `https://raw.githubusercontent.com/RightNow-AI/RightNow-GPU-Database/main/data/intel/all.json`
* **HTTP Method:** `GET`
* **Usage:** A comprehensive open-source database containing technical specifications (transistor count, VRAM in GB, memory bandwidth in GB/s, bus width, TDP, and release dates) for over **2,750+ hardware entries** scraped from TechPowerUp.
* **Filter/Compilation:** The build compiler (`refresh_cache.py`) filters and builds a local dynamic cache database of **812 modern GPUs** with dedicated VRAM >= 4.0 GB, ensuring extremely fast offline-ready lookups and searches in the frontend.

---

## Running Locally & Handling CORS

Browsers apply security protocols (CORS) that block fetching relative files (like `data/cache.json`) when opened via the file protocol (`file:///`).

To host the application locally under secure origins:

1. Open your terminal in the directory.
2. Run a simple Python server:
   ```bash
   python -m http.server 8000
   ```
3. Open your browser and go to: **[http://localhost:8000/](http://localhost:8000/)**
4. The top right indicator will light up green: **Database: Synced**.

---

## Deployment & Automated Refresh

Because ModelSelector is **100% static** (composed exclusively of `index.html` and the pre-computed database `data/cache.json`), it can be hosted for **free** on any static provider without requiring a backend database or node runner.

### Live Deployment
**[https://harrytyp.github.io/modelselector/](https://harrytyp.github.io/modelselector/)**

### Hosting Options:
* **GitHub Pages:** Already configured. Pushes to `main` automatically trigger a Pages deployment. The nightly cache refresh also triggers a redeploy so the live site stays current.
* **Vercel / Netlify:**
  1. Connect your repository to Vercel or Netlify.
  2. Leave the build command blank and publish the root directory.

### Automated Nightly Refresh (GitHub Actions):
A GitHub Actions workflow runs every night at 00:00 UTC to refresh the model catalog and benchmark scores:
1. Fetches the latest GGUF models from Hugging Face Hub
2. Paginates the full Open LLM Leaderboard v2 dataset (4,500+ entries)
3. Queries BenchLM.ai for multi-dimensional rankings
4. Fetches LiveBench scores from the latest CSV release
5. Fetches EvalPlus coding benchmark scores from their live JSON
6. Rebuilds the GPU catalog from the TechPowerUp database
7. Commits the updated `data/cache.json` and triggers a Pages redeploy

See `.github/workflows/refresh_cache.yml` for the full workflow definition.

---

## KV Cache & TPS Physics Simulator Formulations

Memory and speed allocations are compiled using verified GQA-aware formulas:

1. **Quantized Model Size (Weights VRAM):**
   ```math
     \text{VRAM}_{\text{Weights}} = \frac{\text{Parameters (B)} \times \text{BytesPerWeight (Quant)}}{10^9}
   ```

2. **GQA-Aware KV Cache Overhead:**
   ```math
     \text{VRAM}_{\text{KV Cache}} = \frac{2 \times \text{layers} \times \text{context\_length} \times \text{hidden\_size} \times \left( \frac{\text{num\_kv\_heads}}{\text{num\_attn\_heads}} \right) \times 2 \text{ [bytes/fp16]}}{10^9}
   ```

3. **Throughput Compilation (Tokens/s):**
   * If VRAM fits entirely within the GPU:
     ```math
       \text{TPS} = \frac{\text{Memory Bandwidth (GB/s)}}{\text{Model Weights Size (GB)}} \times \text{Efficiency Bonus (35\% for GPU)}
     ```
   * If memory limits require offloading to system RAM:
     ```math
       \text{TPS} = \frac{\text{System Bus Bandwidth (GB/s)}}{\text{Model Weights Size (GB)}} \times \text{Efficiency (22\% for CPU)}
     ```

---

## Simplified User Flow & WebGL Scanner

Following targeted refactoring to keep the simulator lightning-fast and highly focused, the system implements a direct, ultra-transparent developer interface:

1. **Snappy Cache-First Databases:** Startup loads the default model/GPU catalog instantly from the fast local JSON cache (`data/cache.json`), preventing Hugging Face API rate limits or startup fetch lag.
2. **Instant WebGL Hardware Scan:** Click the **Scan My GPU (Auto-Detect)** button next to target devices to automatically identify your active graphics card in 1-click using the browser's WebGL debug extensions.
3. **Completely Transparent Options List:** Dynamic physics simulations are mapped in real-time across all available models, displayed directly inside a dense, sortable table. All complex advisor grid cards have been removed to prioritize raw table transparency.
4. **Rich Model Cards:** Click any row to reveal detailed quantization specifications, memory scaling graphs, and direct links to Hugging Face (`https://huggingface.co/{model_id}`) and the Open LLM Leaderboard.
