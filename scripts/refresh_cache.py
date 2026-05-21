import json
import urllib.request
import urllib.parse
import urllib.error
import re
from datetime import datetime, timezone
import os
import sys
import time

def get_model_family(model_id):
    name = model_id.lower()
    if "gemma-4" in name or "gemma4" in name:
        return "gemma-4"
    if "gemma-3" in name or "gemma3" in name:
        return "gemma-3"
    if "gemma-2" in name or "gemma2" in name:
        return "gemma-2"
    if "gemma" in name:
        return "gemma-1"
    if "qwen3" in name:
        if "coder" in name:
            return "qwen3-coder"
        return "qwen3"
    if "qwen" in name:
        if "coder" in name:
            return "qwen-coder"
        return "qwen"
    if "llama-3" in name or "llama3" in name:
        return "llama-3"
    if "llama" in name:
        return "llama-2"
    if "phi" in name:
        return "phi"
    if "mistral" in name:
        return "mistral"
    if "deepseek" in name:
        return "deepseek"
    return "generic"

def fetch_livebench_scores():
    """Fetch LiveBench scores from the latest CSV + categories JSON."""
    # Try to get the latest available table date
    livebench_base = "https://livebench.ai"
    table_dates = []
    try:
        # Fetch known dates list from recent data
        known_dates = [
            "2026_01_08", "2025_12_23", "2025_11_25", "2025_05_30",
            "2025_04_25", "2025_04_02", "2024_11_25", "2024_08_31",
            "2024_07_26", "2024_06_24"
        ]
        # Try each date until one works
        categories_map = {}
        csv_rows = []
        for date_str in known_dates:
            cat_url = f"{livebench_base}/categories_{date_str}.json"
            csv_url = f"{livebench_base}/table_{date_str}.csv"
            try:
                cat_req = urllib.request.Request(cat_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(cat_req, timeout=30) as cat_res:
                    categories_map = json.loads(cat_res.read().decode("utf-8"))
                csv_req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(csv_req, timeout=30) as csv_res:
                    csv_text = csv_res.read().decode("utf-8")
                csv_rows = csv_text.strip().split("\n")
                print(f"[+] LiveBench: loaded {date_str} ({len(csv_rows)-1} models)")
                break
            except Exception:
                continue
        if not csv_rows:
            return {}, "No LiveBench data available"
        # Parse header to find subcategory columns
        header = csv_rows[0].strip().split(",")
        model_col_idx = 0  # first column is model name
        subcat_cols = header[1:]  # remaining columns are subcategory scores
        # Average all subcategory scores per model for an overall score
        scores = {}
        for row in csv_rows[1:]:
            cols = row.strip().split(",")
            if len(cols) < 2:
                continue
            model_name = cols[0].strip().lower()
            vals = []
            for v in cols[1:]:
                try:
                    vals.append(float(v))
                except ValueError:
                    pass
            if vals:
                scores[model_name] = {"score": round(sum(vals) / len(vals), 1), "samples": len(vals)}
        return scores, "success"
    except Exception as e:
        return {}, f"failed: {e}"

def fetch_evalplus_scores():
    """Fetch EvalPlus coding benchmark scores from the live JSON endpoint."""
    try:
        url = "https://evalplus.github.io/results.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        scores = {}
        for model_name, entry in data.items():
            pass1 = entry.get("pass@1", {})
            humaneval = pass1.get("humaneval+")
            mbpp = pass1.get("mbpp+")
            if humaneval is not None and mbpp is not None:
                scores[model_name.lower().replace("-", " ").replace("_", " ")] = {
                    "humaneval": round(float(humaneval) * 100, 1),
                    "mbpp": round(float(mbpp) * 100, 1)
                }
        print(f"[+] EvalPlus: loaded {len(scores)} models from live API")
        return scores, "success"
    except Exception as e:
        return {}, f"failed: {e}"

def find_benchlm_match(hf_id, benchlm_models):
    hf_id_lower = hf_id.lower()
    clean_hf = hf_id_lower.replace('-', ' ').replace('_', ' ')
    
    best_match = None
    max_score = 0
    
    for bm in benchlm_models:
        bm_name = bm.get("model", "").lower()
        
        # Simple equivalence maps
        if bm_name in clean_hf or clean_hf in bm_name:
            return bm
            
        tokens = bm_name.replace('-', ' ').replace('_', ' ').split()
        match_count = sum(1 for t in tokens if t in clean_hf)
        
        if match_count > max_score and match_count >= 2:
            max_score = match_count
            best_match = bm
            
    return best_match

def refresh_cache():
    print("[*] Starting LLM & GPU Database Scanner...")
    
    # 1. Fetch All GGUF Models from Hugging Face Hub API (paginated)
    print("[*] Querying Hugging Face Hub API for all GGUF repositories (paginated)...")
    def fetch_all_hf_gguf(max_total=1000):
        all_models = []
        url = f"https://huggingface.co/api/models?filter=gguf&sort=downloads&direction=-1&limit={max_total}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                all_models = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"[-] HF API error: {e}")
            return []
        print(f"[+] Received {len(all_models)} GGUF models from Hugging Face.")
        return all_models
    hf_models = fetch_all_hf_gguf(max_total=1000)
    # Remove duplicate model_ids (safety, shouldn't occur without full=true)
    seen_ids = set()
    deduped = []
    for m in hf_models:
        mid = m.get('id')
        if mid and mid not in seen_ids:
            seen_ids.add(mid)
            deduped.append(m)
    hf_models = deduped
    # Further deduplicate: different orgs (unsloth, ggml-org, lmstudio-community) upload the same base model
    seen_model = set()
    deduped_by_base = []
    for m in hf_models:
        mid = m.get('id', '')
        # Extract model name after the org prefix
        parts = mid.split('/')
        model_name = parts[-1] if len(parts) > 1 else mid
        model_name = model_name.lower().replace('-gguf', '').replace('_gguf', '').replace('-', ' ').strip()
        if model_name not in seen_model:
            seen_model.add(model_name)
            deduped_by_base.append(m)
    hf_models = deduped_by_base
    print(f"[+] Retrieved {len(hf_models)} unique GGUF models from Hugging Face.")

    # 2. Fetch Open LLM Leaderboard v2 Scores via datasets-server (PAGINATED!)
    # The API returns HTTP 500 for large limit values; we paginate in batches of 100.
    print("[*] Scraping Hugging Face Open LLM Leaderboard v2 benchmark averages (paginated)...")
    leaderboard_base = "https://datasets-server.huggingface.co/rows?dataset=open-llm-leaderboard%2Fcontents&config=default&split=train"
    page_size = 100
    offset = 0
    hf_leaderboard_map = {}
    leaderboard_fetch_ok = False
    
    try:
        # First request to get total row count
        first_url = f"{leaderboard_base}&limit={page_size}&offset=0"
        l_req = urllib.request.Request(first_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(l_req, timeout=60) as l_response:
            l_data = json.loads(l_response.read().decode("utf-8"))
            total_rows = l_data.get("num_rows_total", 0)
            leaderboard_fetch_ok = True
            
            # Process first page
            for row_obj in l_data.get('rows', []):
                row = row_obj.get('row', {})
                fullname = row.get('fullname')
                if fullname:
                    hf_leaderboard_map[fullname.lower().strip()] = row
        
        print(f"[+] Total leaderboard rows: {total_rows}. Paginating in batches of {page_size}...")
        offset += page_size
        
        # Fetch remaining pages with retry logic
        max_retries = 3
        while offset < total_rows:
            page_url = f"{leaderboard_base}&limit={page_size}&offset={offset}"
            fetched = False
            
            for attempt in range(1, max_retries + 1):
                try:
                    p_req = urllib.request.Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(p_req, timeout=60) as p_response:
                        p_data = json.loads(p_response.read().decode("utf-8"))
                        for row_obj in p_data.get('rows', []):
                            row = row_obj.get('row', {})
                            fullname = row.get('fullname')
                            if fullname:
                                hf_leaderboard_map[fullname.lower().strip()] = row
                    fetched = True
                    break
                except Exception as page_err:
                    if attempt < max_retries:
                        print(f"[-] Page offset={offset} attempt {attempt} failed: {page_err}. Retrying in 5s...")
                        time.sleep(5)
                    else:
                        print(f"[-] Page offset={offset} failed after {max_retries} attempts: {page_err}. Skipping.")
            
            if fetched:
                if offset % 500 == 0:
                    print(f"    ... fetched {len(hf_leaderboard_map)} leaderboard entries so far (offset {offset}/{total_rows})")
            offset += page_size
        
        print(f"[+] Successfully loaded {len(hf_leaderboard_map)} scientific leaderboard entries.")
    except Exception as le:
        print(f"[-] Leaderboard API not responding: {le}. Proceeding with benchmark mapping.")
        leaderboard_fetch_ok = False

    # 3. Fetch BenchLM.ai REST API categories (ALL results!)
    print("[*] Querying BenchLM.ai REST API for multi-dimensional rankings...")
    benchlm_url = "https://benchlm.ai/api/data/leaderboard?limit=1000&format=json"
    benchlm_models = []
    try:
        b_req = urllib.request.Request(benchlm_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(b_req, timeout=60) as b_res:
            benchlm_data = json.loads(b_res.read().decode("utf-8"))
            benchlm_models = benchlm_data.get("models", [])
        print(f"[+] Loaded {len(benchlm_models)} BenchLM.ai categorical model scores.")
    except Exception as be:
        print(f"[-] BenchLM.ai API failed: {be}.")

    # 3.5 LiveBench - fetch from live CSV endpoint
    print("[*] Loading LiveBench scores...")
    livebench_scores, lb_status = fetch_livebench_scores()
    if lb_status == "success":
        print(f"[+] LiveBench API: loaded {len(livebench_scores)} model entries.")
    else:
        print(f"[-] LiveBench API: {lb_status}")

    # 3.6 EvalPlus - fetch from live JSON endpoint
    print("[*] Loading EvalPlus scores...")
    evalplus_scores, ep_status = fetch_evalplus_scores()
    if ep_status == "success":
        print(f"[+] EvalPlus API: loaded {len(evalplus_scores)} model entries.")
    else:
        print(f"[-] EvalPlus API: {ep_status}")

    # Process models & resolve exact/derived benchmarks
    models_list = []
    raw_results = {} # Maps model_id or base_model_id to resolved raw scores dict

    for m in hf_models:
        model_id = m.get('id')
        downloads = m.get('downloads', 0)
        author = model_id.split('/')[0] if '/' in model_id else "Community"
        raw_name = model_id.split('/')[-1]
        
        clean_name = raw_name.replace('-GGUF', '').replace('-gguf', '').replace('-', ' ').replace('_', ' ').title()
        
        # Determine parameter size with advanced multi-field inspection
        params = None
        search_strings = [raw_name, model_id]
        for tag in m.get('tags', []):
            if tag.startswith('base_model:'):
                search_strings.append(tag)
                
        for s in search_strings:
            match = re.search(r'\b(\d+(\.\d+)?)[bB]\b', s.replace('-', ' ').replace('_', ' '))
            if not match:
                match = re.search(r'(\d+(\.\d+)?)[bB]', s)
            if match:
                try:
                    params = float(match.group(1))
                    break
                except:
                    pass
                    
        # Fallback to direct parameter tag check
        if params is None:
            for tag in m.get('tags', []):
                if tag.startswith('params:'):
                    try:
                        params = float(tag.replace('params:', '').replace('B', '').replace('b', '').strip())
                        break
                    except:
                        pass
        
        # Skip embedding/OCR/moved non-causal files
        if params is None:
            is_text_gen = any(t in ['text-generation', 'text2text-generation', 'image-text-to-text'] for t in m.get('tags', []))
            if is_text_gen or "it" in raw_name.lower() or "instruct" in raw_name.lower():
                params = 7.0
            else:
                # Last resort: try to get params from the base model API
                base_tag = None
                for tag in m.get('tags', []):
                    if tag.startswith('base_model:') and '/' in tag:
                        bt = tag.split(':', 1)[1]
                        # Skip quantized/GGUF base_model references (they point to other quants, not the real model)
                        if not any(x in bt.lower() for x in ['gguf', 'q8_0', 'q4', 'q5', 'q6', 'q2', 'q3', 'fp16', 'fp8']):
                            base_tag = bt
                            break
                if not base_tag:
                    # Try searching for the model name in HF API to find the real model
                    raw_parts = raw_name.lower().replace('-gguf', '').replace('_gguf', '').split('-')
                    search_name = '-'.join([p for p in raw_parts if p and p not in ('gguf', 'abliterated', 'uncensored', 'lora', 'fp16', 'fp8')])
                    if search_name:
                        try:
                            search_url = f"https://huggingface.co/api/models?search={urllib.parse.quote(search_name)}&sort=downloads&direction=-1&limit=5"
                            s_req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(s_req, timeout=15) as s_resp:
                                search_results = json.loads(s_resp.read().decode('utf-8'))
                            # Try each result until one has safetensors data
                            for sr in search_results:
                                sr_id = sr.get('id', '')
                                if sr_id and 'gguf' not in sr_id.lower():
                                    try:
                                        sr_url = f"https://huggingface.co/api/models/{sr_id}"
                                        sr_req = urllib.request.Request(sr_url, headers={'User-Agent': 'Mozilla/5.0'})
                                        with urllib.request.urlopen(sr_req, timeout=15) as sr_resp:
                                            sr_data = json.loads(sr_resp.read().decode('utf-8'))
                                        st = sr_data.get('safetensors', {})
                                        total_params = st.get('total', 0) if isinstance(st, dict) else 0
                                        if total_params:
                                            params = round(total_params / 1e9, 1)
                                            break
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                if base_tag:
                    try:
                        base_url = f"https://huggingface.co/api/models/{base_tag}"
                        b_req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(b_req, timeout=15) as b_resp:
                            base_data = json.loads(b_resp.read().decode('utf-8'))
                        st = base_data.get('safetensors', {})
                        total_params = st.get('total', 0) if isinstance(st, dict) else 0
                        if total_params:
                            params = round(total_params / 1e9, 1)
                        if not params:
                            m_id = base_data.get('id', '')
                            m_match = re.search(r'(\d+(\.\d+)?)[bB]', m_id)
                            if m_match:
                                params = float(m_match.group(1))
                    except Exception:
                        pass
                if params is None:
                    continue

        # Extract base model ID from tags
        base_model_id = None
        for tag in m.get('tags', []):
            if tag.startswith('base_model:'):
                tag_parts = tag.split(':')
                potential_base = tag_parts[-1]
                if '/' in potential_base:
                    base_model_id = potential_base
                    break
        if not base_model_id:
            base_model_id = model_id.replace('-GGUF', '').replace('-gguf', '')

        # Model network size heuristics
        if params <= 3.5:
            layers, hidden, kv_heads, attn_heads = 32, 3072, 32, 32
        elif params <= 9.5:
            layers, hidden, kv_heads, attn_heads = 32, 4096, 8, 32
        elif params <= 16.0:
            layers, hidden, kv_heads, attn_heads = 40, 5120, 8, 40
        elif params <= 35.0:
            layers, hidden, kv_heads, attn_heads = 64, 6656, 8, 64
        else:
            layers, hidden, kv_heads, attn_heads = 80, 8192, 8, 64
            
        if "gemma-2" in model_id.lower() or "gemma-3" in model_id.lower() or "gemma-4" in model_id.lower():
            if 7 < params < 11:
                layers, hidden, kv_heads, attn_heads = 42, 3584, 8, 16
            elif params < 3:
                layers, hidden, kv_heads, attn_heads = 26, 2048, 8, 8

        tags = ["api-imported"]
        lower_id = model_id.lower()
        if "chat" in lower_id or "instruct" in lower_id or "-it" in lower_id:
            tags.append("chat")
        if "code" in lower_id or "coder" in lower_id:
            tags.append("coding")
        if "math" in lower_id:
            tags.append("math")
        if "vision" in lower_id:
            tags.append("vision")
        if "multilingual" in lower_id:
            tags.append("multilingual")

        # ----------------------------------------------------
        # STAGE 1 & 2: Benchmark Sourcing (Measured / Derived)
        # ----------------------------------------------------
        bench_scores = {}
        status = "estimated"
        derived_from = ""
        
        # Let's search in HF Leaderboard V2 dataset
        lf_entry = hf_leaderboard_map.get(model_id.lower().strip())
        if not lf_entry:
            lf_entry = hf_leaderboard_map.get(base_model_id.lower().strip())
            if lf_entry:
                status = "derived"
                derived_from = base_model_id
        else:
            status = "measured"

        # Let's search in BenchLM.ai rankings
        bm_entry = find_benchlm_match(model_id, benchlm_models)
        if not bm_entry:
            bm_entry = find_benchlm_match(base_model_id, benchlm_models)
            if bm_entry and status == "estimated":
                status = "derived"
                derived_from = base_model_id

        # Pull raw values if available
        if lf_entry:
            bench_scores["ifeval"] = lf_entry.get("IFEval")
            bench_scores["bbh"] = lf_entry.get("BBH")
            bench_scores["math_lvl5"] = lf_entry.get("MATH Lvl 5")
            bench_scores["gpqa"] = lf_entry.get("GPQA")
            bench_scores["musr"] = lf_entry.get("MUSR")
            bench_scores["mmlu_pro"] = lf_entry.get("MMLU-PRO")
        
        if bm_entry:
            cat = bm_entry.get("categoryScores", {})
            if cat.get("coding") is not None:
                bench_scores["benchlm_coding"] = cat.get("coding")
            if cat.get("reasoning") is not None:
                bench_scores["benchlm_reasoning"] = cat.get("reasoning")
            if cat.get("instructionFollowing") is not None:
                bench_scores["benchlm_instruction"] = cat.get("instructionFollowing")
            if cat.get("math") is not None:
                bench_scores["benchlm_math"] = cat.get("math")
            if cat.get("knowledge") is not None:
                bench_scores["benchlm_knowledge"] = cat.get("knowledge")
            if cat.get("multilingual") is not None:
                bench_scores["benchlm_multilingual"] = cat.get("multilingual")

        # 3.7 Resolve LiveBench & EvalPlus from live API data
        fam = get_model_family(model_id)
        model_key = model_id.lower().replace("-", " ").replace("_", " ")
        livebench_score = None
        
        # Try exact model name match first
        if model_key in livebench_scores:
            livebench_score = livebench_scores[model_key].get("score")
        # Try base model name
        if livebench_score is None:
            base_key = base_model_id.lower().replace("-", " ").replace("_", " ")
            if base_key in livebench_scores:
                livebench_score = livebench_scores[base_key].get("score")
        # Try family-level grouping from live data
        if livebench_score is None:
            fam_scores = []
            for lk, lv in livebench_scores.items():
                if get_model_family(lk.replace(" ", "-")) == fam or fam in lk:
                    if lv.get("score") is not None:
                        fam_scores.append(lv["score"])
            if fam_scores:
                fam_scores.sort()
                n = len(fam_scores)
                livebench_score = fam_scores[n // 2] if n % 2 else (fam_scores[n//2-1] + fam_scores[n//2]) / 2.0
        # Last resort: parameter-scaling formula
        if livebench_score is None:
            livebench_score = 50.0 + (params ** 0.5) * 2.2
        bench_scores["livebench"] = round(min(98.0, livebench_score), 1)

        he_score = None
        mbpp_score = None
        # Try exact model name match first
        if model_key in evalplus_scores:
            he_score = evalplus_scores[model_key].get("humaneval")
            mbpp_score = evalplus_scores[model_key].get("mbpp")
        # Try base model name
        if he_score is None:
            base_key = base_model_id.lower().replace("-", " ").replace("_", " ")
            if base_key in evalplus_scores:
                he_score = evalplus_scores[base_key].get("humaneval")
                mbpp_score = evalplus_scores[base_key].get("mbpp")
        # Try family-level grouping from live data
        if he_score is None:
            fam_he, fam_mbpp = [], []
            for ek, ev in evalplus_scores.items():
                if get_model_family(ek.replace(" ", "-")) == fam or fam in ek:
                    if ev.get("humaneval") is not None:
                        fam_he.append(ev["humaneval"])
                    if ev.get("mbpp") is not None:
                        fam_mbpp.append(ev["mbpp"])
            if fam_he:
                fam_he.sort()
                n = len(fam_he)
                he_score = fam_he[n // 2] if n % 2 else (fam_he[n//2-1] + fam_he[n//2]) / 2.0
            if fam_mbpp:
                fam_mbpp.sort()
                n = len(fam_mbpp)
                mbpp_score = fam_mbpp[n // 2] if n % 2 else (fam_mbpp[n//2-1] + fam_mbpp[n//2]) / 2.0
        # Last resort: parameter-scaling formula
        if he_score is None:
            he_score = 55.0 + (params ** 0.5) * 3.5
        if mbpp_score is None:
            mbpp_score = 58.0 + (params ** 0.5) * 3.2
            
        bench_scores["evalplus_humaneval"] = round(min(98.0, he_score), 1)
        bench_scores["evalplus_mbpp"] = round(min(98.0, mbpp_score), 1)

        # Save temporarily for post-processing/medians
        raw_results[model_id] = {
            "status": status,
            "derived_from": derived_from,
            "scores": bench_scores,
            "family": fam,
            "params": params
        }

        # Base quality estimation formula in case completely missing
        quality_score = 50.0 + (params ** 0.5) * 3.6

        # Detect MoE active parameters (e.g. "30B-A3B" = 30B total, 3B active per token)
        active_params = params
        a_match = re.search(r'[aA](\d+(\.\d+)?)[bB]', model_id)
        if not a_match:
            a_match = re.search(r'[aA](\d+(\.\d+)?)[bB]', clean_name)
        if a_match:
            detected = float(a_match.group(1))
            if detected < params and detected > 0:
                active_params = detected

        # For DeepSeek V4 Flash (158B MoE, ~37B active) and similar
        if active_params == params and ('deepseek' in model_id.lower() or 'glm-5' in model_id.lower()):
            active_params = round(params / 4.0, 1)  # estimate: MoE with ~25% active

        models_list.append({
            "model_id": model_id,
            "name": clean_name,
            "developer": author.title(),
            "parameters": params,
            "active_parameters": active_params,
            "base_model_id": base_model_id,
            "quality_score": round(quality_score, 1),
            "description": f"HF GGUF repository. {downloads:,} active community downloads.",
            "config": {
                "num_layers": layers,
                "hidden_size": hidden,
                "num_kv_heads": kv_heads,
                "num_attn_heads": attn_heads,
                "vocab_size": 128256 if "llama" in model_id.lower() else 32000
            },
            "tags": tags,
            "benchmarks": {} # Populated below
        })

    # ----------------------------------------------------
    # STAGE 3: Family Median Fallbacks & Final Mapping
    # ----------------------------------------------------
    # Calculate column-wise medians for each family
    cols = ["ifeval", "bbh", "math_lvl5", "gpqa", "musr", "mmlu_pro", 
            "benchlm_coding", "benchlm_reasoning", "benchlm_instruction", 
            "benchlm_math", "benchlm_knowledge", "benchlm_multilingual",
            "livebench", "evalplus_humaneval", "evalplus_mbpp"]
    
    family_scores = {} # family -> col -> list of measured values
    for m_id, obj in raw_results.items():
        fam = obj["family"]
        if fam not in family_scores:
            family_scores[fam] = {c: [] for c in cols}
            
        for c in cols:
            val = obj["scores"].get(c)
            if val is not None:
                family_scores[fam][c].append(val)
                
    # Compile medians
    family_medians = {}
    for fam, col_dict in family_scores.items():
        family_medians[fam] = {}
        for c in cols:
            vals = sorted(col_dict[c])
            if vals:
                n = len(vals)
                median = vals[n // 2] if n % 2 != 0 else (vals[(n // 2) - 1] + vals[n // 2]) / 2.0
                family_medians[fam][c] = round(median, 1)

    # Global fallback medians based on parameters scaling if family has no scores
    global_fallbacks = {
        "ifeval": 50.0,
        "bbh": 45.0,
        "math_lvl5": 20.0,
        "gpqa": 18.0,
        "musr": 35.0,
        "mmlu_pro": 38.0,
        "benchlm_coding": 50.0,
        "benchlm_reasoning": 55.0,
        "benchlm_instruction": 55.0,
        "benchlm_math": 25.0,
        "benchlm_knowledge": 50.0,
        "benchlm_multilingual": 60.0,
        "livebench": 50.0,
        "evalplus_humaneval": 55.0,
        "evalplus_mbpp": 58.0
    }

    # Final pass to populate benchmarks with fallback rules and quant penalties
    for model_obj in models_list:
        m_id = model_obj["model_id"]
        raw_obj = raw_results[m_id]
        
        resolved = {}
        status = raw_obj["status"]
        derived_from = raw_obj["derived_from"]
        fam = raw_obj["family"]
        params = raw_obj["params"]
        
        # Apply staging fallback rules
        for c in cols:
            val = raw_obj["scores"].get(c)
            if val is not None:
                # Direct match or derived match (Stage 1 / 2)
                if status == "derived":
                    # Apply a small quant quality penalty for derived quants
                    resolved[c] = round(max(0.0, val - 1.8), 1)
                else:
                    resolved[c] = round(val, 1)
            else:
                # Stage 3: Family Median Fallback
                fam_val = family_medians.get(fam, {}).get(c)
                if fam_val is not None:
                    resolved[c] = fam_val
                    if status == "measured" or status == "derived":
                        pass # keep status
                    else:
                        status = "estimated"
                else:
                    # Stage 4: Global parameter-scaling fallback
                    base_val = global_fallbacks[c]
                    scale = (params ** 0.3) * 1.2
                    resolved[c] = round(min(100.0, base_val * scale), 1)
                    if status != "measured" and status != "derived":
                        status = "estimated"

        # Calculate a default overall base score using standard weighted averages
        avg_overall = sum(resolved.values()) / len(cols)
        model_obj["quality_score"] = round(avg_overall, 1)
        
        model_obj["benchmarks"] = {
            "status": status,
            "derived_from": derived_from,
            "metrics": resolved
        }

    # 4. Compile GPU Database Dynamically from Live TechPowerUp open database APIs
    print("[*] Compiling GPU Database dynamically...")
    gpus_list = []
    
    # Architectural, dynamic, or specialized non-discrete presets
    gpus_list.append({
      "id": "custom",
      "name": "Custom Hardware Configuration",
      "vram": 24.0,
      "bandwidth": 1008,
      "type": "gpu",
      "description": "Configure your own active VRAM limits and bus performance."
    })
    gpus_list.append({
      "id": "generic_cpu_ddr5",
      "name": "System CPU-Only (DDR5 Dual-Channel)",
      "vram": 0.0,
      "bandwidth": 80,
      "type": "cpu",
      "description": "CPU execution bound by standard DDR5 speed. Extremely slow but limitless size."
    })
    gpus_list.append({
      "id": "generic_cpu_quad",
      "name": "System CPU-Only (DDR5 Quad-Channel)",
      "vram": 0.0,
      "bandwidth": 150,
      "type": "cpu",
      "description": "Workstation CPU execution. Quad-channel bus gives moderate speeds for CPU inference."
    })
    gpus_list.append({
      "id": "intel_integrated",
      "name": "Intel Integrated HD/Iris Xe Graphics",
      "vram": 4.0,
      "bandwidth": 60,
      "type": "gpu",
      "description": "Integrated APU sharing system memory. Bound by system RAM bandwidth speed."
    })
    gpus_list.append({
      "id": "amd_integrated",
      "name": "AMD Radeon Integrated Graphics",
      "vram": 4.0,
      "bandwidth": 60,
      "type": "gpu",
      "description": "Integrated APU sharing system memory. Bound by system RAM bandwidth speed."
    })
    
    # Dynamic Apple Silicon Unified Memory architectures (not standard discrete PCIe desktop cards)
    mac_profiles = [
        ("M3 Pro", 27.0, 150, "Apple M3 Pro (36GB Unified)"),
        ("M2 Max", 72.0, 400, "Apple M2 Max (96GB Unified)"),
        ("M3 Max", 96.0, 400, "Apple M3 Max (128GB Unified)"),
        ("M2 Ultra", 144.0, 800, "Apple M2 Ultra (192GB Unified)")
    ]
    for m_gen, vram, band, desc in mac_profiles:
        gpus_list.append({
            "id": f"mac_{m_gen.lower().replace(' ', '_')}",
            "name": desc,
            "vram": vram,
            "bandwidth": band,
            "type": "mac",
            "description": f"Unified memory architecture. {desc} profile suited for local inference."
        })
        
    # Dynamic Multi-GPU configuration presets
    gpus_list.append({
      "id": "dual_rtx_3090",
      "name": "Dual NVIDIA GeForce RTX 3090",
      "vram": 48.0,
      "bandwidth": 1872,
      "type": "multi_gpu",
      "description": "Dual workstation setup. Combines VRAM to run 70B models at full local speed."
    })
    gpus_list.append({
      "id": "dual_rtx_4090",
      "name": "Dual NVIDIA GeForce RTX 4090",
      "vram": 48.0,
      "bandwidth": 2016,
      "type": "multi_gpu",
      "description": "Elite multi-GPU consumer workstation. Phenomenal speed and capacity."
    })

    # TechPowerUp modern GPU database endpoints
    tpu_urls = [
        ("NVIDIA", "https://raw.githubusercontent.com/RightNow-AI/RightNow-GPU-Database/main/data/nvidia/all.json"),
        ("AMD", "https://raw.githubusercontent.com/RightNow-AI/RightNow-GPU-Database/main/data/amd/all.json"),
        ("INTEL", "https://raw.githubusercontent.com/RightNow-AI/RightNow-GPU-Database/main/data/intel/all.json")
    ]
    
    parsed_gpus = []
    for brand, url in tpu_urls:
        print(f"[*] Querying TechPowerUp {brand} GPU database...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                brand_data = json.loads(response.read().decode("utf-8"))
            
            print(f"[+] Loaded {len(brand_data)} raw entries for {brand}.")
            for item in brand_data:
                vram = float(item.get("memorySize", 0.0))
                
                # Filter out low VRAM legacy cards (less than 4.0GB)
                if vram < 4.0:
                    continue
                    
                name = item.get("name", "")
                manufacturer = item.get("manufacturer", brand)
                
                # Clean full name presentation
                full_name = str(name)
                if not full_name.lower().startswith(manufacturer.lower()):
                    full_name = f"{manufacturer} {full_name}"
                    
                gpu_id = "ext_" + item.get("id", "").replace("-", "_")
                
                band = float(item.get("memoryBandwidth", 0.0))
                bus = int(item.get("memoryBus", 0))
                
                # Backfill memory bandwidth estimate based on bus size if missing
                if band <= 0:
                    if bus == 128:
                        band = 288.0
                    elif bus == 192:
                        band = 504.0
                    elif bus == 256:
                        band = 672.0
                    elif bus == 384:
                        band = 936.0
                    else:
                        band = float(vram * 24.0)
                        
                arch = item.get("architecture", "Unknown")
                release = item.get("releaseDate", "Unknown")
                
                parsed_gpus.append({
                    "id": gpu_id,
                    "name": full_name,
                    "vram": vram,
                    "bandwidth": int(band),
                    "type": "gpu",
                    "description": f"TechPowerUp specification. Architecture: {arch}. Release: {release}."
                })
        except Exception as ex:
            print(f"[-] Failed to fetch or parse {brand} TPU dataset: {ex}")
            
    # Deduplicate and merge TechPowerUp list
    seen_ids = set(g["id"] for g in gpus_list)
    for g in parsed_gpus:
        if g["id"] not in seen_ids:
            gpus_list.append(g)
            seen_ids.add(g["id"])
            
    print(f"[+] Loaded and merged TechPowerUp specs. Total compiled catalog: {len(gpus_list)} GPUs.")

    # 5. Consolidate and overwrite data/cache.json
    
    # Quantization physical constants (GGUF specification) and quality loss
    # (community-established averages from llama.cpp perplexity evaluations)
    QUANT_BYTES = {
        "Q2_K": 0.325, "Q3_K_M": 0.438, "Q4_0": 0.500,
        "Q4_K_M": 0.563, "Q5_K_M": 0.688, "Q6_K": 0.750,
        "Q8_0": 1.000, "fp16": 2.000
    }
    QUANT_QUALITY_LOSS = {
        "Q2_K": 12.5, "Q3_K_M": 4.5, "Q4_0": 2.0,
        "Q4_K_M": 1.0, "Q5_K_M": 0.4, "Q6_K": 0.15,
        "Q8_0": 0.05, "fp16": 0.0
    }
    QUANT_SAMPLES = {k: 0 for k in QUANT_BYTES}  # empirical sample count (0 = default)
    # TODO: In future, aggregate empirical loss from per-quant leaderboard entries
    # when a centralized GGUF evaluation dataset becomes available.

    SPEED_SCALING = {
        "Q2_K": 1.10,   # Less data to move = faster per byte
        "Q3_K_M": 1.05,
        "Q4_0": 1.02,
        "Q4_K_M": 1.00, # Baseline - sweet spot
        "Q5_K_M": 0.92, # More data to move, slightly slower
        "Q6_K": 0.85,
        "Q8_0": 0.78,
        "fp16": 0.65    # Much more data, significantly slower
    }
    PHYSICAL_CONSTANTS = {
        "gpu_efficiency": 0.44,
        "cpu_efficiency": 0.30,
        "apple_silicon_bonus": 0.80
    }
    
    cache_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "huggingface_leaderboard": {
                "name": "Hugging Face Open LLM Leaderboard v2",
                "url": "https://huggingface.co/datasets/open-llm-leaderboard/contents",
                "status": "success" if leaderboard_fetch_ok else "failed",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "row_count": len(hf_leaderboard_map)
            },
            "benchlm": {
                "name": "BenchLM.ai Scientific API",
                "url": "https://benchlm.ai/api/data/leaderboard",
                "status": "success" if benchlm_models else "failed",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "row_count": len(benchlm_models)
            },
            'livebench': {
                'name': 'LiveBench LLM Benchmark',
                'url': 'https://livebench.ai/',
                'status': lb_status,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'row_count': len(livebench_scores)
            },
            'evalplus': {
                'name': 'EvalPlus Code Benchmark (HumanEval+ & MBPP+)',
                'url': 'https://evalplus.github.io/results.json',
                'status': ep_status,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'row_count': len(evalplus_scores)
            },
            "techpowerup": {
                "name": "TechPowerUp GPU Database",
                "url": "https://raw.githubusercontent.com/RightNow-AI/RightNow-GPU-Database/main/data/",
                "status": "success" if parsed_gpus else "failed",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "row_count": len(parsed_gpus)
            },
            "huggingface_models": {
                "name": "Hugging Face GGUF Catalog API",
                "url": "https://huggingface.co/api/models",
                "status": "success" if hf_models else "failed",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "row_count": len(hf_models)
            },
            "quantization": {
                "name": "GGUF Quantization Constants & Quality Loss",
                "url": "https://github.com/ggml-org/llama.cpp/wiki/Feature-Matrix",
                "status": "success",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "row_count": len(QUANT_BYTES)
            },
            "speed_estimation": {
                "name": "Speed Estimation Engine",
                "url": "https://github.com/ggml-org/llama.cpp/wiki/Feature-Matrix",
                "status": "success",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "row_count": len(SPEED_SCALING)
            }
        },
        "quant_bytes": QUANT_BYTES,
        "quant_loss": QUANT_QUALITY_LOSS,
        "quant_samples": QUANT_SAMPLES,
        "speed_scaling": SPEED_SCALING,
        "physical_constants": PHYSICAL_CONSTANTS,
        "models": models_list if models_list else [],
        "gpus": gpus_list if gpus_list else []
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/cache.json", "w", encoding="utf-8") as f:
        json.dump(cache_payload, f, indent=2, ensure_ascii=False)
        
    print("\n[+] SUCCESS!")
    print("    Overwrote data/cache.json with:")
    print(f"   * {len(models_list)} pure generative GGUF models from HF Hub")
    print(f"   * {len(gpus_list)} consolidated GPUs specs (dynamic TechPowerUp database)")
    print(f"    Cache timestamp: {cache_payload['generated_at']}")

if __name__ == "__main__":
    refresh_cache()
