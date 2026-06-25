**How it Works**

Verity is A RAG fact-checking application that extracts verifiable claims from text and live audio, retrieves real evidence, and returns confidence-scored verdicts with citations.

What it does

Record live audio from any tab, and Verity will:


1. Extract every discrete, verifiable factual claim from the input
2. Decompose complex claims into atomic, independently checkable 3/ sub-claims
3. Retrieve real evidence for each sub-claim via web search
4. Evaluate each sub-claim against that evidence (supported, contradicted, or inconclusive) with a confidence score and plain-English reasoning

Surface sources so every verdict is traceable, not just asserted


**What's completed**
Claim extraction, decomposition, evidence retrieval, and evaluation (full pipeline, end to end)
Real-time audio capture and transcription via WebSocket (handles buffering and async transcription so the connection never blocks)
Supabase persistence with a normalized schema (transcripts → claims → subclaim_evaluations)
PolitiFact ground-truth dataset scraped and stored for calibration work


**Tech stack**
LLM: OpenRouter (Gemini 2.5 Flash) — direct API calls 
Transcription: OpenAI Whisper (local)
Evidence Retrieval: Serper API
Backend: FastAPI
Database: Supabase (Postgres)
Real-time audio: WebSockets + MediaRecorder

**Flow**

```
┌─────────────────────────────────────┐
│     chrome.tabCapture / getDisplayMedia     │
│         (audio chunks, webm)        │
└──────────────────┬──────────────────┘
                   │
                   ▼
        WebSocket (FastAPI)
        receive_bytes() loop
                   │
                   ▼
         buffer (~9s window)
                   │
                   ▼
      asyncio.create_task()
       (non-blocking background)
                   │
                   ▼
          Whisper (local)
           transcript text
                   │
                   ▼
       claim extractor (LLM)
            claims[]
                   │
                   ▼
      claim decomposer (LLM)
           subclaims[]
                   │
                   ▼
           Serper API
       3 sources per subclaim
                   │
                   ▼
       claim evaluator (LLM)
   verdict + confidence + reasoning
                   │
                   ▼
      parse_llm_response()
       confidence capped ≤ 0.95
                   │
                   ▼
   send_queue → websocket.send_text()
          JSON back to client
                   │
                   ▼
            Supabase
transcripts → claims → subclaim_evaluations
```
