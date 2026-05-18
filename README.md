# LocalModel.ai — LLM Optimizer & Hardware Simulator

An interactive, high-fidelity browser-side simulator that estimates memory allocation, context scaling, and generation throughput (tokens/s) for any given local LLM quantization under specific hardware constraints.

The entire system is powered by **dynamic, live external APIs** to build the hardware database, model metadata registries, and task-performance quality indexes in real-time.

---

## 🏗️ System Architecture & Data Flow

```mermaid
graph TD
    subgraph Browser Client (http://localhost:8000/)
        UI[Interactive Glassmorphic UI]
        State[Active Application State]
        Calc[Physical Simulator Engine]
        LS[Local Storage Sync]
    end

    subgraph Hugging Face Hub APIs
        HF_Search[HF Models API] -->|Search Keywords| UI
        HF_Meta[HF Model Meta API] -->|Model details & Safetensors| State
        HF_Config[HF Resolve CDN] -->|config.json layers/heads/hidden| Calc
    end

    subgraph Open LLM Leaderboard API
        HF_Dataset[HF Datasets Server] -->|Open LLM Leaderboard contents| State
    end

    subgraph Wikipedia GPU API
        Wiki_GPU[voidful Raw CDN] -->|994 GPU specification array| UI
    end

    State -->|Math formulas| Calc
    LS <-->|Offline Persistence| State
    Calc -->|Interactive Tables & Canvas Charts| UI
```

---

## 📡 Dynamic API Endpoints Directory

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
* **CORS Strategy:** The `/resolve/` endpoint is explicitly hosted on Hugging Face's global CDN and includes the `Access-Control-Allow-Origin: *` header, bypassing raw origin restrictions!
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
* **Filter/Compilation**: The build compiler (`refresh_cache.py`) filters and builds a local dynamic cache database of **812 modern GPUs** with dedicated VRAM $\ge$ 4.0GB, ensuring extremely fast offline-ready lookups and searches in the frontend.

---

## ⚙️ Running Locally & Handling CORS

Browsers apply security protocols (CORS) that block fetching relative files (like `data/cache.json`) when opened via the file protocol (`file:///`).

To host the application locally under secure origins:

1. Open your terminal in the directory.
2. Run a simple Python server:
   ```bash
   python -m http.server 8000
   ```
3. Open your browser and go to: **[http://localhost:8000/](http://localhost:8000/)**
4. The top right indicator will light up green: **`🟢 Database: Synced`**.

---

## 🚀 Deployment & Automated Refresh

Because LocalModel.ai is **100% static** (composed exclusively of `index.html` and the pre-computed database `data/cache.json`), it can be hosted for **free** on any static provider without requiring a backend database or node runner!

### Hosting Options:
* **GitHub Pages:**
  1. Push this project folder to a GitHub repository.
  2. Navigate to **Settings > Pages** and enable GitHub Pages on your primary branch.
* **Vercel / Netlify:**
  1. Connect your repository to Vercel or Netlify.
  2. Leave the build command blank and publish the root directory.

### Automated Cache Refreshes (GitHub Actions Cron):
To keep the model catalog and Open LLM Leaderboard benchmark scores fresh without running the python script manually, you can commit this simple GitHub Actions workflow to run once a day at midnight UTC:

Create a file at `.github/workflows/refresh_cache.yml`:
```yaml
name: Refresh Model Cache
on:
  schedule:
    - cron: '0 0 * * *' # Runs every day at midnight UTC
  workflow_dispatch: # Allows manual trigger

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Run Database Scanner
        run: python scripts/refresh_cache.py
      - name: Commit and Push Changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add data/cache.json
          git commit -m "Auto-refresh model and GPU cache database [skip ci]" || exit 0
          git push
```

---

## 🧮 KV Cache & TPS Physics Simulator Formulations

Memory and speed allocations are compiled using verified GQA-aware formulas:

1. **Quantized Model Size (Weights VRAM):**
   $$\text{VRAM}_{\text{Weights}} = \frac{\text{Parameters (B)} \times \text{BytesPerWeight (Quant)}}{10^9}$$

2. **GQA-Aware KV Cache Overhead:**
   $$\text{VRAM}_{\text{KV Cache}} = \frac{2 \times \text{layers} \times \text{context\_length} \times \text{hidden\_size} \times \left( \frac{\text{num\_kv\_heads}}{\text{num\_attn\_heads}} \right) \times 2 \text{ [bytes/fp16]}}{10^9}$$

3. **Throughput Compilation (Tokens/s):**
   * If VRAM fits entirely within the GPU:
     $$\text{TPS} = \frac{\text{Memory Bandwidth (GB/s)}}{\text{Model Weights Size (GB)}} \times \text{Efficiency Bonus (35\% for GPU)}$$
   * If memory limits require offloading to system RAM:
     $$\text{TPS} = \frac{\text{System Bus Bandwidth (GB/s)}}{\text{Model Weights Size (GB)}} \times \text{Efficiency (22\% for CPU)}$$

---

## 🔍 Simplified User Flow & WebGL Scanner

Following targeted refactoring to keep the simulator lightning-fast and highly focused, the system implements a direct, ultra-transparent developer interface:

1. **Snappy Cache-First Databases**: Startup loads the default model/GPU catalog instantly from the fast local JSON cache (`data/cache.json`), preventing Hugging Face API rate limits or startup fetch lag.
2. **Instant WebGL Hardware Scan**: Click the **Scan My GPU (Auto-Detect)** button next to target devices to automatically identify your active graphics card in 1-click using the browser's WebGL debug extensions.
3. **Completely Transparent Options List**: Dynamic physics simulations are mapped in real-time across all available models, displayed directly inside a dense, sortable table. All complex advisor grid cards have been removed to prioritize raw table transparency.
4. **Rich Model Cards**: Click any row to reveal detailed quantization specifications, memory scaling graphs, and direct links to Hugging Face (`https://huggingface.co/{model_id}`) and the Open LLM Leaderboard.
