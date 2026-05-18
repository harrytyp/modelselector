

Tool-Architektur für lokale Modelle

Die beste Quelle ist nicht eine einzige Quelle.



Für ein belastbares Tool solltest du Modellqualität, quantisierte Qualität, reale Hardware-Performance und VRAM-Schätzung als getrennte Datenebenen behandeln. Für Qualität ist die Open LLM Leaderboard-Familie stark; für echte lokale Geschwindigkeit sind LocalScore und Community-Benchmark-Datenbanken derzeit nützlicher; für VRAM brauchst du am Ende zusätzlich ein eigenes Rechenmodell.

Empfohlener Stack

Quellen prüfen

Qualität

HF Open LLM

Speed

LocalScore

VRAM

Eigenes Modell

Warum so aufgeteilt? Benchmarks für "bestes Modell" und Benchmarks für "läuft auf RTX 4070 mit 26 tok/s in Q4" messen unterschiedliche Dinge. Genau diese Trennung macht dein Tool verlässlich.

Quellen nach Zweck



Nutze pro Frage die Quelle, die methodisch wirklich dazu passt.

1\. Modellqualität ohne Hardware



Beste Primärquelle für "welches Open-Source-Modell ist grundsätzlich stark?"

Top-Quelle



Hugging Face Open LLM Leaderboard ist die robusteste Basis für generelle Open-Model-Qualität, weil dort standardisierte Benchmarks und detaillierte Resultate zentral gepflegt werden. Es ist aber keine gute Einzelquelle für lokale tok/s oder für "welcher Quant ist auf welcher GPU am besten".

Qualitätstandardisierte Benchmarkskaum Hardware-Fokus

2\. Quantisierte Qualität



Beste Primärquelle für "welcher Quant hält Qualität gut?"

Wichtig



Intel Low-Bit Quantized Open LLM Leaderboard ist derzeit eine der saubersten Quellen speziell für quantisierte Varianten, weil nach Quantisierungsverfahren, Datentyp und Modellgröße gefiltert werden kann. Das macht die Quelle sehr wertvoll, wenn dein Tool Rankings je Quant, etwa AWQ, GPTQ oder GGUF, ausgeben soll.

AWQGPTQGGUFQuant-spezifisch

3\. Reale lokale Geschwindigkeit



Beste Primärquelle für "wie schnell läuft es lokal?"

Beste Speed-Quelle



LocalScore ist aktuell die überzeugendste offene Quelle für lokale Performance, weil dieselbe Benchmark-Suite auf realer Hardware gefahren wird und Prompt-Verarbeitung, Generation und TTFT gemeinsam erfasst werden. Der Haken ist, dass die Abdeckung noch wächst und Spezialfälle wie verschiedene Engines, Offload-Modi oder exotische Quants nicht vollständig abbildet.

tok/sTTFTreale Hardwaresingle GPU Fokus

4\. Community-Aggregation für Praxisfälle



Gut für schnelle Orientierung, weniger stark als wissenschaftliche Primärquelle

Sekundärquelle



llm-bench.io ist interessant als Aggregator, weil es ausdrücklich Speed, Speicher und Qualität über Community-Runs zusammenführt. Für dein Tool wäre das eine gute sekundäre Quelle, um Coverage zu erhöhen und reale Kombinationen aus Modell, Quant, Backend und Hardware einzusammeln.

Community datamemory usequality+speed

Empfohlener Daten-Stack



&#x20;   Qualität: HF Open LLM Leaderboard als Default-Ranking für Basismodelle.

&#x20;   Quant-Qualität: Intel Low-Bit Leaderboard plus modellnahe Eval-Sheets auf Hugging Face.

&#x20;   Speed: LocalScore als Kern, ergänzt um llm-bench.io und ggf. eigene Crowd-Benchmarks.

&#x20;   VRAM: Eigene Formel mit Parametern, Quant, Kontext, KV-Cache, Backend und Overhead.

&#x20;   Verfügbarkeit: Modell-Metadaten direkt aus Hugging Face und GGUF/MLX/Ollama-Releases ableiten.



Faustregel: Qualität und Hardware nie aus derselben Quelle erzwingen, wenn die Methodik dafür nicht gebaut wurde.

VRAM: zuverlässigste Quelle



Es gibt dafür keine einzelne wirklich zuverlässige öffentliche Quelle. Rechner wie DevTk oder APXML sind nützlich als Orientierung, aber sie sind explizit Schätzungen.

VRAM\_total ≈ weights + KV\_cache + runtime\_overhead

weights ≈ params × bytes\_per\_weight(quant)

KV\_cache ≈ layers × hidden\_size × seq\_len × batch × bytes\_cache × factor

runtime\_overhead ≈ backend + graph + allocator + fragmentation



&#x20;   Die Gewichtsgröße ist noch der einfache Teil; problematisch wird es bei KV-Cache, Backend-Unterschieden und Teil-Offload.

&#x20;   Deshalb sollte dein Tool VRAM immer als Schätzung mit Konfidenz ausgeben, nicht als absolute Wahrheit.

&#x20;   Am verlässlichsten wird VRAM, wenn du Formel + gemessene Community-Runs kombinierst.



Was du speichern solltest

Feld	Warum es zählt

base\_model\_id	Normalisiert Varianten eines Modells über Quants und Dateiformate hinweg.

quant\_scheme	Trennt GGUF Q4\_K\_M, AWQ 4bit, GPTQ 4bit, EXL2 usw.

backend	llama.cpp, vLLM, Ollama, MLX, TensorRT-LLM liefern sehr verschiedene Ergebnisse.

hardware\_profile	GPU, VRAM, RAM, CPU, Apple unified memory, PCIe-Setup.

context\_length	tok/s und Speicher ändern sich stark mit Kontextgröße.

metrics	prompt tok/s, gen tok/s, TTFT, peak VRAM, avg VRAM, success/fail.

Ranking-Logik für dein Tool

Empfehlung pro Nutzerfrage



Beispiel: "Ich habe 24 GB VRAM und will Coding + 20 tok/s".



&#x20;   Filtere zuerst nach gemessener oder geschätzter Passung in VRAM.

&#x20;   Danach minimiere TTFT und maximiere Generation tok/s für genau diesen Hardwaretyp.

&#x20;   Reranke zuletzt nach Qualitäts-Score aus Basismodell + Quant-Abschlag.



Quant-Empfehlung



&#x20;   Zeige nie nur "bester Quant" global, sondern "bester Quant auf dieser Hardware und für diesen Zweck".

&#x20;   Halte einen separaten Qualitätsverlust-Score pro Quantfamilie und Modellfamilie vor.

&#x20;   Markiere Datenqualität: gemessen, abgeleitet, oder heuristisch geschätzt.







Hier ist der vollständige Umsetzungsplan. Die wichtigste Vorab-Erkenntnis aus der Recherche: LocalScore hat noch keine öffentliche REST-API – das ist der größte Constraint, der die Architektur beeinflusst.

Tech Stack (minimal)



text

Vanilla HTML + CSS + JavaScript (kein Framework)

├── index.html        ← alles in einer Datei, offline-fähig

├── data/cache.json   ← lokaler Daten-Cache (täglich refreshbar)

└── fetch.js          ← optionales Node-Script zum Cache-Refresh



Kein Build-Prozess, kein npm, kein Backend. Die Seite läuft mit open index.html lokal oder auf jedem statischen Hoster.

Datenquellen \& vollständige API-Endpunkte

Ebene 1 – Modell-Metadaten \& Qualität



Hugging Face Hub API – keine Auth nötig für öffentliche Modelle



text

\# Modell-Liste (gefiltert nach Tags/Bibliothek)

GET https://huggingface.co/api/models

&#x20; ?search=<query>

&#x20; \&filter=gguf          ← oder "text-generation"

&#x20; \&sort=downloads

&#x20; \&direction=-1

&#x20; \&limit=100

&#x20; \&full=true            ← gibt parameter\_count, tags etc. zurück



\# Einzelnes Modell (Metadaten: params, dtype, tags, safetensors-header)

GET https://huggingface.co/api/models/{owner}/{model\_id}

&#x20; ?blobs=true           ← gibt Dateigrößen zurück



\# Config.json lesen (für hidden\_size, num\_layers usw. → VRAM-Formel)

GET https://huggingface.co/{owner}/{model\_id}/resolve/main/config.json



HF Datasets API – Open LLM Leaderboard Ergebnisse



text

\# Leaderboard-Inhalte als Dataset abrufen (Parquet-basiert)

GET https://datasets-server.huggingface.co/rows

&#x20; ?dataset=open-llm-leaderboard%2Fcontents

&#x20; \&config=default

&#x20; \&split=train

&#x20; \&offset=0

&#x20; \&length=100



\# Schema prüfen

GET https://datasets-server.huggingface.co/info

&#x20; ?dataset=open-llm-leaderboard%2Fcontents



Ebene 2 – Quantisierte Qualität



Intel Low-Bit Quantized Leaderboard – ebenfalls als HF Dataset verfügbar



text

GET https://datasets-server.huggingface.co/rows

&#x20; ?dataset=Intel%2Flow\_bit\_open\_llm\_leaderboard

&#x20; \&config=default

&#x20; \&split=train

&#x20; \&offset=0

&#x20; \&length=100



Ebene 3 – Lokale Hardware-Performance



LocalScore – noch keine offizielle REST-API. Zwei Strategien:



text

\# Option A: HTML-Scraping (fragil, aber möglich)

GET https://localscore.ai/results

&#x20; → JSON ist im <script id="\_\_NEXT\_DATA\_\_"> eingebettet

&#x20; → per regex/DOMParser extrahierbar



\# Option B (empfohlen): LocalScore GitHub gibt SQLite-DB frei

GET https://raw.githubusercontent.com/cjpais/LocalScore/main/localscore.db

&#x20; → lokal mit sql.js (WASM SQLite) auswerten, kein Server nötig

&#x20; → enthält: model\_id, quant, hardware, prompt\_tps, gen\_tps, ttft, vram\_used



llm-bench.io – als Fallback/Ergänzung



text

GET https://llm-bench.io

&#x20; → ebenfalls JSON in Next.js \_\_NEXT\_DATA\_\_

&#x20; → Felder: model, quantization, backend, gpu, tokens\_per\_second, vram\_gb



Ebene 4 – VRAM-Schätzung



vramio – öffentliche freie API



text

GET https://vramio.ksingh.in/model

&#x20; ?hf\_id=meta-llama/Llama-3.1-8B

&#x20; → gibt zurück: vram\_gb, parameters, dtype, overhead



\# Response-Beispiel:

{

&#x20; "model\_id": "meta-llama/Llama-3.1-8B",

&#x20; "parameters": 8030000000,

&#x20; "dtype": "bfloat16",

&#x20; "base\_vram\_gb": 14.9,

&#x20; "inference\_vram\_gb": 17.9

}



Zusätzlich eigene Formel für Quant-Varianten (die API gibt nur Base-dtype zurück):



javascript

const BYTES\_PER\_QUANT = {

&#x20; "Q2\_K": 0.325, "Q3\_K\_M": 0.438, "Q4\_0": 0.500,

&#x20; "Q4\_K\_M": 0.563, "Q5\_K\_M": 0.688, "Q6\_K": 0.750,

&#x20; "Q8\_0": 1.000, "fp16": 2.000, "bf16": 2.000,

&#x20; "awq-4bit": 0.563, "gptq-4bit": 0.563, "exl2-4bit": 0.563

};



function estimateVRAM(params, quantKey, contextLen, numLayers, hiddenSize) {

&#x20; const weights = (params \* BYTES\_PER\_QUANT\[quantKey]) / 1e9;

&#x20; const kvCache = (2 \* numLayers \* contextLen \* hiddenSize \* 2) / 1e9; // fp16 KV

&#x20; const overhead = 0.8; // GB

&#x20; return weights + kvCache + overhead;

}



Umsetzungsplan (Phasen)

Phase 1 – Daten-Cache aufbauen



Ein einmaliges fetch.js (Node, kein Framework) das alle APIs abruft und data/cache.json schreibt. Cron oder manuell täglich ausführen.



text

fetch.js

&#x20; → HF Leaderboard Rows         → cache.quality\[]

&#x20; → Intel Low-Bit Leaderboard   → cache.quant\_quality\[]

&#x20; → LocalScore DB (SQLite)      → cache.performance\[]

&#x20; → vramio für Top-50-Modelle   → cache.vram\[]

&#x20; → HF Model-Metadaten          → cache.models\[]



Phase 2 – index.html



Drei Ansichten, alle clientseitig aus cache.json:



text

┌─ Filter-Leiste ──────────────────────────────────────────┐

│  GPU-VRAM: \[8GB] \[12GB] \[16GB] \[24GB] \[48GB]             │

│  Mindest tok/s: \[10] \[20] \[40]                            │

│  Use Case: \[Coding] \[Chat] \[RAG] \[Reasoning]              │

│  Quant-Familie: \[GGUF] \[AWQ] \[GPTQ] \[EXL2]               │

└──────────────────────────────────────────────────────────┘



┌─ Ergebnis-Tabelle ───────────────────────────────────────┐

│  Modell │ Bester Quant │ VRAM │ tok/s │ Qualität │ Fit   │

│  Llama3 │ Q4\_K\_M       │ 5.2G │ 38    │ 87       │ 🟢    │

└──────────────────────────────────────────────────────────┘



┌─ Detail-View (on click) ─────────────────────────────────┐

│  Alle Quants mit tok/s Sparkline, VRAM-Kurve je Kontext, │

│  Qualitätsverlust Q8→Q4, Datenquelle + Confidence-Label  │

└──────────────────────────────────────────────────────────┘



Phase 3 – Ranking-Logik



javascript

function score(model, userVRAM, minTPS) {

&#x20; const fits = model.vram\_estimate <= userVRAM;           // hard filter

&#x20; const speedScore = Math.min(model.gen\_tps / minTPS, 2); // 0–2

&#x20; const qualityScore = model.benchmark\_avg / 100;         // 0–1

&#x20; const quantPenalty = QUANT\_QUALITY\_LOSS\[model.quant];   // 0–0.15

&#x20; return fits ? (speedScore \* 0.5 + (qualityScore - quantPenalty) \* 0.5) : 0;

}



Wichtige Einschränkungen

Problem	Lösung

LocalScore hat keine REST-API 	SQLite-DB direkt laden + sql.js (WASM)

HF Leaderboard ändert Dataset-Struktur	Schema via /info-Endpoint vorab prüfen

vramio kennt keine Quants 	eigene Quant-Multiplikatoren + vramio als Basis

llm-bench.io kein API	\_\_NEXT\_DATA\_\_ parsen, als sekundär behandeln

Daten veralten	cache.json mit generated\_at-Timestamp + Warn-Banner nach 7 Tagen

Lokale Nutzung



bash

\# Cache initial befüllen (Node erforderlich, nur für Refresh)

node fetch.js



\# Website starten – kein Server nötig

open index.html



\# Oder mit minimalem HTTP-Server (für fetch() von lokalem JSON)

npx serve .



Das war's. Willst du, dass ich direkt mit index.html + fetch.js anfange?

