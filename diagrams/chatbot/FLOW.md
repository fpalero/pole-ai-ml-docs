# Flow — `chatbot` (`pole_chatbot` Conversational Agent Backend)

> Layers and key classes of the ReAct conversational agent backend. Shipped in `packages/chatbot`.
> Class-level details: [CLASSES.md](./CLASSES.md).

---

## 1. Agent Architecture Diagram

```mermaid
flowchart LR
    subgraph PRES["Presentation"]
        WS["ChatbotRouter — WS /ws/chat"]
    end

    subgraph APP["Application"]
        AG["ReActAgent"]
        TR["ToolRegistry"]
        JH["JobHandlers"]
        LLM["OpenCodeClient"]
        SS["SessionService"]
    end

    subgraph DOM["Domain"]
        SC["session_schema (ChatbotSession)"]
    end

    subgraph INFRA["Infrastructure"]
        SR["SessionRepo<br/>redis_repo / postgres_repo"]
        MC["MetricsCollector"]
    end

    subgraph TOOLS["pole_tools facade"]
        FC["crop · shift · histogram · similarity"]
    end

    subgraph RAG["pole_rag RAG tools (Phase 6 DONE)"]
        RT["rag_tools.py<br/>query_pole · query_calisthenics<br/>query_psicology → psychology · query_biomechanics<br/>k=3 · unknown-DB ToolError"]
        RS[("Chroma /data/rag<br/>text_chunks + image_descriptions")]
    end

    subgraph JOB["jobs package"]
        ORC["JobOrchestrator"]
    end

    OC[("OpenCode sidecar")]
    DB[("MongoDB / Redis / PostgreSQL")]

    WS --> AG
    AG --> TR
    AG --> SS
    SS --> SC
    SS --> SR
    SR --> DB
    TR --> FC
    TR --> RT
    RT --> RS
    TR --> JH
    JH --> ORC
    AG --> LLM
    LLM --> OC
    AG --> MC
```

---

## 2. ReAct Turn Sequence

```mermaid
sequenceDiagram
    participant C as Client
    participant R as ChatbotRouter
    participant A as ReActAgent
    participant T as ToolRegistry
    participant L as OpenCodeClient
    participant J as JobOrchestrator

    C->>R: WS message (+ session_id)
    R->>A: run(message)
    A->>SS: load/create session
    A->>L: prompt (tool-call request)
    L-->>A: tool call
    A->>T: invoke
    alt job-mode tool (crop/shift)
        T->>J: submit job
        J-->>T: events
        T-->>A: result
    else sync tool (histogram/similarity)
        T-->>A: result
    end
    A->>L: feedback prompt
    L-->>A: agent_reply
    A->>SS: persist session
    A->>R: agent_reply + job events
    R->>C: WS frames
```

### 2.1 Diagram Component Descriptions

| Node | Purpose & Use |
| :--- | :--- |
| **PRES — ChatbotRouter** | `WS /ws/chat` endpoint; receives messages and streams back replies + relayed job events. |
| **APP — ReActAgent** | Runs the bounded ReAct tool-call loop and produces the final reply. |
| **APP — ToolRegistry** | Resolves tool names to handlers (sync or job-mode). |
| **APP — JobHandlers** | Worker-side `crop`/`shift` handlers with progress stages. |
| **APP — OpenCodeClient** | LLM text client to the OpenCode sidecar. |
| **APP — SessionService** | Loads/creates/persists/resumes `ChatbotSession`. |
| **DOM — `session_schema`** | Pydantic `ChatbotSession` domain model. |
| **INFRA — SessionRepo (redis/postgres)** | Persistence backends for sessions. |
| **INFRA — MetricsCollector** | Collects tool latency + LLM token usage. |
| **TOOLS — `pole_tools` facade** | `crop · shift · histogram · similarity` import surface used by tools. |
| **RAG — `rag_tools.py`** | 4 sync RAG tools over `pole_rag.query` (`POLE_RAG_DATA_DIR`, default package `data/`, staging `/data/rag`; explicit `data_dir` wins). `query_psicology` maps to the `psychology` DB dir (036; tool name unchanged). Verified on staging per 030 (k=3, `source_document` metadata). |
| **JOB — JobOrchestrator** | From the `jobs` package; runs job-mode tools. |
| **OpenCode sidecar / MongoDB / Redis / PostgreSQL** | External LLM + datastores. |

---

## 3. Layers and Key Classes

### Presentation
- `ws.py` — `ChatbotRouter`: `WS /ws/chat` (message in → `agent_reply` + relayed job events).

### Application
- `agent.py` — `ReActAgent`: bounded ReAct loop, tool-call execution, error capture, off-script rephrase.
- `tools.py` — `ToolRegistry` + `register_default_tools` (sync `histogram`/`similarity`, job-mode `crop`/`shift`).
- `rag_tools.py` — `RAG_DB_BY_TOOL` + `register_rag_tools` (sync `query_pole`/`query_calisthenics`/`query_psicology`/`query_biomechanics`, k=3, `ToolError` on unknown DB; deferred `pole_rag` import so the module stays importable off-path).
- `job_handlers.py` — `JOB_HANDLERS`: worker-side crop/shift handlers with progress stages.
- `llm.py` — `OpenCodeClient`: text chat to OpenCode sidecar.
- `session_service.py` — `SessionService`: session load/create/persist/resume.

### Domain
- `session_schema.py` — Pydantic `ChatbotSession` model (`original_video`, `current_crop`, `confirmed`, `history`, `status`).

### Infrastructure
- `session/redis_repo.py`, `session/postgres_repo.py`, `session/base.py` — persistence backends.
- `metrics.py` — `MetricsCollector` (tool latency, LLM tokens).
- `config.py` — `ChatbotSettings`.
- `exceptions.py` — error types.

---

## 4. Data Flow (extract → transform → respond)

| Step | Extract | Transform | Produce |
| :--- | :--- | :--- | :--- |
| Message | user text + session | ReAct prompt | tool call |
| Tool call | tool name + args | dispatch sync or job | result / job events |
| Feedback | result + plot | LLM prompt | `agent_reply` |
| Persist | session state | serialize | stored session (resume) |
| Metrics | tool/LLM timings | aggregate | metrics store |
