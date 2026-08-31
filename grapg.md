# LangGraph Agent Workflow – Comprehensive Guide

This document explains the internal mechanics of the `PoleLangGraphAgent` – a LangGraph‑based replacement for the manual `ReActAgent`. The agent processes user messages, enforces strict guardrails (crop‑before‑analyze, confirmation requirements), manages session state, and gracefully handles errors.

## 1. Workflow Diagram

The following Mermaid diagram visualises the entire state‑machine, showing initialisation, the two core nodes (`agent` and `tool`), routing logic, termination conditions, and session synchronisation.

```mermaid
flowchart TD
    subgraph Input["User Input"]
        U[User Message]
        S[Session Data]
    end

    subgraph Init["Initialization"]
        I1[Build AgentState from Session]
        I2[Add System Prompt to Messages]
        I3[Append User Message]
        I4[Check for Confirmation]
        I1 --> I2 --> I3 --> I4
    end

    subgraph Graph["StateGraph Workflow"]
        direction TB
        
        A[⚙️ AGENT NODE<br/>Call LLM & Parse Response]
        
        A --> R{Agent Route<br/>Tool Calls?}
        R -->|No calls| END1[END]
        R -->|Has calls| T
        
        T[🔧 TOOL NODE<br/>Execute Tools with Guardrails]
        
        T --> TR{After Tool Route}
        TR -->|Loop| A
        TR -->|END| END2[END]
    end

    subgraph AgentNode["Agent Node Details"]
        direction LR
        A1[Invoke LLM with Messages]
        A2[Parse Response]
        A3[Parse Tool Calls]
        A4[Add AIMessage to History]
        A5[Store Pending Tool Calls]
        A1 --> A2 --> A3 --> A4 --> A5
    end

    subgraph ToolNode["Tool Node Details"]
        direction TB
        T1[Iterate Pending Tool Calls]
        T1 --> T2{Malformed JSON?}
        T2 -->|Yes| T3[Off-Script Recovery<br/>- Decrease Rephrase Budget<br/>- Add Error ToolMessage]
        T3 --> T4{Budget Exhausted?}
        T4 -->|Yes| T5[Terminal State<br/>Fallback Message]
        T4 -->|No| T6[Continue to Next Call]
        
        T2 -->|No| T7{Analyze Tool<br/>& No Crop/Confirm?}
        T7 -->|Yes| T8[Blocked: Add Guardrail Message]
        T7 -->|No| T9[Invoke Tool via Registry]
        
        T9 --> T10{Success?}
        T10 -->|No| T11[Add Error ToolMessage<br/>Invocation Failed]
        T10 -->|Yes| T12[Add ToolMessage]
        
        T12 --> T13{Crop Tool?}
        T13 -->|Yes| T14[Record Crop Bounds<br/>Reset Confirmation]
        T13 -->|No| T15{Analyze Tool?}
        T15 -->|Yes| T16[Record Analyze Invoked]
        
        T14 --> T17[Increment Iteration]
        T16 --> T17
        T11 --> T17
        T8 --> T17
        T6 --> T17
    end

    subgraph RoutingRules["Routing Rules"]
        R1[**Agent Route:**<br/>- tool_calls exist → TOOL<br/>- no tool_calls → END]
        R2[**Tool Route:**<br/>- crop_invoked → END<br/>- analyze_invoked → END<br/>- budget exhausted → END<br/>- abandoned → END<br/>- else → AGENT]
    end

    subgraph WorkflowPoints["Workflow Termination"]
        W1[**Crop Invoked:**<br/>Return confirmation request<br/>with crop bounds]
        W2[**Analyze Invoked:**<br/>Return correction offer]
        W3[**Budget Exhausted:**<br/>Return fallback message<br/>Mark session abandoned]
    end

    subgraph SessionSync["Session Synchronization"]
        SYNC1[Sync crop bounds to session]
        SYNC2[Sync confirmation status]
        SYNC3[Sync session status]
    end

    subgraph Output["Output"]
        O1[Reply Message]
        O2[Tool Calls History]
        O3[Message History]
        O4[Session Status]
    end

    %% Connections – only between actual nodes, not to subgraph borders
    U --> Init
    S --> Init
    Init --> Graph

    %% Styling
    classDef node fill:#f9f,stroke:#333,stroke-width:2px
    classDef routing fill:#bbf,stroke:#333,stroke-width:2px
    classDef terminal fill:#bfb,stroke:#333,stroke-width:2px
    
    class A,T node
    class R,TR routing
    class END1,END2 terminal