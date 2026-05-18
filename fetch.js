/**
 * fetch.js
 * Node.js utility to refresh Hugging Face model metadata and config specifications,
 * merging them with consumer GPU specifications to rebuild data/cache.json.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Define output file location
const CACHE_DIR = path.join(__dirname, 'data');
const CACHE_FILE = path.join(CACHE_DIR, 'cache.json');

// Core models we track
const MODELS_TO_REFRESH = [
  {
    model_id: "meta-llama/Meta-Llama-3.1-8B-Instruct",
    name: "Llama 3.1 8B Instruct",
    developer: "Meta",
    parameters: 8.03,
    quality_score: 68.2,
    description: "Meta's flagship lightweight model, optimized for multilingual dialogue and general tasks with 128k context.",
    tags: ["chat", "coding", "multilingual", "rag"]
  },
  {
    model_id: "meta-llama/Meta-Llama-3.1-70B-Instruct",
    name: "Llama 3.1 70B Instruct",
    developer: "Meta",
    parameters: 70.6,
    quality_score: 79.3,
    description: "Meta's highly capable 70B model. Outstanding for complex reasoning, planning, and coding.",
    tags: ["chat", "coding", "reasoning", "complex"]
  },
  {
    model_id: "mistralai/Mistral-7B-Instruct-v0.3",
    name: "Mistral 7B Instruct v0.3",
    developer: "Mistral AI",
    parameters: 7.25,
    quality_score: 65.8,
    description: "An updated version of the classic 7B model. Supports function calling, native vLLM and has an extended vocab.",
    tags: ["chat", "coding", "function-calling"]
  },
  {
    model_id: "google/gemma-2-9b-it",
    name: "Gemma 2 9B IT",
    developer: "Google",
    parameters: 9.24,
    quality_score: 71.5,
    description: "Google's 9B model built on the Gemma 2 architecture. Highly efficient with quality matching larger models.",
    tags: ["chat", "reasoning", "general"]
  },
  {
    model_id: "google/gemma-2-27b-it",
    name: "Gemma 2 27B IT",
    developer: "Google",
    parameters: 27.2,
    quality_score: 77.2,
    description: "A highly competitive 27B parameter model, providing near-frontier class intelligence on high-end consumer hardware.",
    tags: ["chat", "reasoning", "coding"]
  },
  {
    model_id: "microsoft/Phi-3.5-mini-instruct",
    name: "Phi-3.5 Mini Instruct",
    developer: "Microsoft",
    parameters: 3.82,
    quality_score: 61.8,
    description: "A lightweight, state-of-the-art open model built on Phi-3 datasets. Excels in reasoning and math.",
    tags: ["chat", "reasoning", "math", "fast"]
  },
  {
    model_id: "microsoft/Phi-3-medium-128k-instruct",
    name: "Phi-3 Medium Instruct (128k)",
    developer: "Microsoft",
    parameters: 14.0,
    quality_score: 69.1,
    description: "A 14B parameter model with huge 128k context length support, delivering excellent RAG and summarization performance.",
    tags: ["chat", "rag", "long-context"]
  },
  {
    model_id: "Qwen/Qwen2.5-7B-Instruct",
    name: "Qwen 2.5 7B Instruct",
    developer: "Alibaba",
    parameters: 7.62,
    quality_score: 70.8,
    description: "Alibaba's highly acclaimed 7B model. Incredible multilingual and coding capabilities for its size.",
    tags: ["chat", "coding", "multilingual", "fast"]
  },
  {
    model_id: "Qwen/Qwen2.5-72B-Instruct",
    name: "Qwen 2.5 72B Instruct",
    developer: "Alibaba",
    parameters: 72.7,
    quality_score: 81.2,
    description: "Top-tier open source model. Matches closed models on complex coding tasks, maths, and multilingual queries.",
    tags: ["coding", "reasoning", "complex", "multilingual"]
  },
  {
    model_id: "CohereForAI/c4ai-command-r-plus",
    name: "Command R+",
    developer: "Cohere",
    parameters: 104.0,
    quality_score: 75.5,
    description: "A massive 104B model optimized for RAG, tool use, and enterprise tasks. Huge multi-step tool agent capabilities.",
    tags: ["rag", "agents", "tool-use", "enterprise"]
  }
];

// GPU configuration template (re-merged upon rebuild)
const GPU_SPECIFICATIONS = [
  {
    id: "rtx_5090",
    name: "NVIDIA GeForce RTX 5090",
    vram: 32,
    bandwidth: 1792,
    type: "gpu",
    description: "Next-gen flagship consumer card. Outstanding bandwidth and 32GB VRAM capacity."
  },
  {
    id: "rtx_4090",
    name: "NVIDIA GeForce RTX 4090",
    vram: 24,
    bandwidth: 1008,
    type: "gpu",
    description: "Current flagship consumer GPU. Perfect for 8B models and 70B offloaded configurations."
  },
  {
    id: "rtx_4080s",
    name: "NVIDIA GeForce RTX 4080 Super",
    vram: 16,
    bandwidth: 736,
    type: "gpu",
    description: "High-end consumer card. Fast, but bound by 16GB VRAM capacity."
  },
  {
    id: "rtx_4070ti_super",
    name: "NVIDIA GeForce RTX 4070 Ti Super",
    vram: 16,
    bandwidth: 672,
    type: "gpu",
    description: "Excellent price-to-VRAM value with 16GB high-bandwidth VRAM."
  },
  {
    id: "rtx_4070s",
    name: "NVIDIA GeForce RTX 4070 Super",
    vram: 12,
    bandwidth: 504,
    type: "gpu",
    description: "Highly popular mid-range card. Comfortable for 7B/8B Q4 quantizations."
  },
  {
    id: "rtx_4060ti_16gb",
    name: "NVIDIA GeForce RTX 4060 Ti 16GB",
    vram: 16,
    bandwidth: 288,
    type: "gpu",
    description: "Affordable large capacity VRAM (16GB) but bottlenecked by 128-bit memory bus bandwidth."
  },
  {
    id: "rtx_3090",
    name: "NVIDIA GeForce RTX 3090",
    vram: 24,
    bandwidth: 936,
    type: "gpu",
    description: "Legacy king of consumer VRAM. 24GB high bandwidth makes it perfect for local LLMs."
  },
  {
    id: "rtx_3060_12gb",
    name: "NVIDIA GeForce RTX 3060 12GB",
    vram: 12,
    bandwidth: 360,
    type: "gpu",
    description: "Budget choice. Good memory capacity and decent bus width."
  },
  {
    id: "nvidia_a100",
    name: "NVIDIA A100 Tensor Core 80GB",
    vram: 80,
    bandwidth: 2039,
    type: "gpu",
    description: "Enterprise-class GPU. Elite bandwidth and 80GB HBM2e memory."
  },
  {
    id: "nvidia_h100",
    name: "NVIDIA H100 Tensor Core 80GB SXM",
    vram: 80,
    bandwidth: 3350,
    type: "gpu",
    description: "State-of-the-art enterprise graphics. Astronomical memory bandwidth."
  },
  {
    id: "dual_rtx_3090",
    name: "Dual NVIDIA GeForce RTX 3090",
    vram: 48,
    bandwidth: 1872,
    type: "multi_gpu",
    description: "Dual workstation setup. Combines VRAM to run 70B models at full local speed."
  },
  {
    id: "dual_rtx_4090",
    name: "Dual NVIDIA GeForce RTX 4090",
    vram: 48,
    bandwidth: 2016,
    type: "multi_gpu",
    description: "Elite multi-GPU consumer workstation. Phenomenal speed and capacity."
  },
  {
    id: "amd_7900xtx",
    name: "AMD Radeon RX 7900 XTX",
    vram: 24,
    bandwidth: 960,
    type: "gpu",
    description: "AMD flagship gaming card. Outstanding 24GB VRAM and high memory bandwidth."
  },
  {
    id: "amd_7900xt",
    name: "AMD Radeon RX 7900 XT",
    vram: 20,
    bandwidth: 800,
    type: "gpu",
    description: "Strong high-end AMD card. Generous 20GB VRAM pool."
  },
  {
    id: "amd_7800xt",
    name: "AMD Radeon RX 7800 XT",
    vram: 16,
    bandwidth: 624,
    type: "gpu",
    description: "Popular mid-range AMD card with solid 16GB VRAM specs."
  },
  {
    id: "mac_m2_ultra",
    name: "Apple M2 Ultra (192GB Unified)",
    vram: 144,
    bandwidth: 800,
    type: "mac",
    description: "Unified Architecture. Allows allocating up to 144GB of unified memory as VRAM, running 70B+ models in FP16 locally."
  },
  {
    id: "mac_m3_max",
    name: "Apple M3 Max (128GB Unified)",
    vram: 96,
    bandwidth: 400,
    type: "mac",
    description: "High-end MacBook Pro spec. Up to 96GB available for model weights with high bandwidth."
  },
  {
    id: "mac_m2_max",
    name: "Apple M2 Max (96GB Unified)",
    vram: 72,
    bandwidth: 400,
    type: "mac",
    description: "Unified memory architecture. Outstanding balance for 30B class models."
  },
  {
    id: "mac_m3_pro",
    name: "Apple M3 Pro (36GB Unified)",
    vram: 27,
    bandwidth: 150,
    type: "mac",
    description: "Mid-tier Unified Memory. Decent speed, perfect for 8B models at high precision."
  },
  {
    id: "intel_a770",
    name: "Intel Arc A770 16GB",
    vram: 16,
    bandwidth: 560,
    type: "gpu",
    description: "Intel flagship GPU. Great budget option for a spacious 16GB VRAM buffer."
  },
  {
    id: "generic_cpu_ddr5",
    name: "System CPU-Only (DDR5 Dual-Channel)",
    vram: 0,
    bandwidth: 80,
    type: "cpu",
    description: "CPU execution bound by standard DDR5 speed. Extremely slow but limitless size."
  },
  {
    id: "generic_cpu_quad",
    name: "System CPU-Only (DDR5 Quad-Channel)",
    vram: 0,
    bandwidth: 150,
    type: "cpu",
    description: "Workstation CPU execution. Quad-channel bus gives moderate speeds for CPU inference."
  },
  {
    id: "custom",
    name: "Custom Hardware Configuration",
    vram: 24,
    bandwidth: 1008,
    type: "gpu",
    description: "Configure your own active VRAM limits and bus performance."
  }
];

// Helper to fetch content over HTTPS
function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) LocalModelOptimizer/1.0'
      }
    };
    https.get(url, options, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        // Handle redirect
        return fetchUrl(res.headers.location).then(resolve).catch(reject);
      }
      
      if (res.statusCode !== 200) {
        reject(new Error(`Failed with status: ${res.statusCode} at URL: ${url}`));
        return;
      }
      
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => resolve(body));
    }).on('error', reject);
  });
}

// Fetch JSON wrapper
async function fetchJson(url) {
  const content = await fetchUrl(url);
  return JSON.parse(content);
}

// Core execution
async function run() {
  console.log("⚡ Starting Hugging Face Model Sync...");
  console.log(`📡 Fetching metadata for ${MODELS_TO_REFRESH.length} tracking models...`);

  const updatedModels = [];

  for (const template of MODELS_TO_REFRESH) {
    try {
      console.log(`\n🔍 Fetching: ${template.model_id}`);
      
      // 1. Fetch HF Model details (downloads etc.)
      const apiInfo = await fetchJson(`https://huggingface.co/api/models/${template.model_id}`);
      const downloads = apiInfo.downloads || 0;
      console.log(`   └─ Downloads: ${downloads.toLocaleString()}`);

      // 2. Fetch config.json to get exact layers/heads/dimensions
      const configUrl = `https://huggingface.co/${template.model_id}/raw/main/config.json`;
      const config = await fetchJson(configUrl);
      
      // Normalize different config patterns in HF
      const num_layers = config.num_hidden_layers || config.num_layers || config.n_layer || 32;
      const hidden_size = config.hidden_size || config.n_embd || 4096;
      const num_attn_heads = config.num_attention_heads || config.n_head || 32;
      const num_kv_heads = config.num_key_value_heads || num_attn_heads; // Default to MHA if GQA is not set
      const vocab_size = config.vocab_size || 32000;

      console.log(`   └─ Architecture: L:${num_layers} | H:${hidden_size} | A:${num_attn_heads} | KV:${num_kv_heads}`);

      // Push sanitized results
      updatedModels.push({
        model_id: template.model_id,
        name: template.name,
        developer: template.developer,
        parameters: template.parameters,
        base_model_id: template.model_id.replace('-Instruct', '').replace('-it', ''),
        quality_score: template.quality_score,
        downloads: downloads,
        description: template.description,
        config: {
          num_layers,
          hidden_size,
          num_kv_heads,
          num_attn_heads,
          vocab_size
        },
        tags: template.tags
      });
      
      // Simple rate limiting spacing
      await new Promise(r => setTimeout(r, 600));

    } catch (error) {
      console.warn(`   ⚠️  Error fetching ${template.model_id}: ${error.message}`);
      console.log(`      ↳ Keeping default specifications for ${template.name}`);
      
      // Add default specifications if API fetch failed
      updatedModels.push({
        model_id: template.model_id,
        name: template.name,
        developer: template.developer,
        parameters: template.parameters,
        base_model_id: template.model_id.replace('-Instruct', '').replace('-it', ''),
        quality_score: template.quality_score,
        description: template.description,
        config: {
          num_layers: template.model_id.includes('70B') || template.model_id.includes('72B') ? 80 : 32,
          hidden_size: template.model_id.includes('70B') || template.model_id.includes('72B') ? 8192 : 4096,
          num_kv_heads: 8,
          num_attn_heads: template.model_id.includes('70B') || template.model_id.includes('72B') ? 64 : 32,
          vocab_size: 128000
        },
        tags: template.tags
      });
    }
  }

  // 3. Write cache.json file
  const cacheData = {
    generated_at: new Date().toISOString(),
    models: updatedModels,
    gpus: GPU_SPECIFICATIONS
  };

  try {
    if (!fs.existsSync(CACHE_DIR)){
      fs.mkdirSync(CACHE_DIR, { recursive: true });
    }
    
    fs.writeFileSync(CACHE_FILE, JSON.stringify(cacheData, null, 2), 'utf-8');
    console.log(`\n🎉 Success! Successfully updated ${CACHE_FILE}`);
    console.log(`⏰ Saved at: ${cacheData.generated_at}`);
  } catch (err) {
    console.error(`❌ Failed to write cache.json: ${err.message}`);
  }
}

run();
