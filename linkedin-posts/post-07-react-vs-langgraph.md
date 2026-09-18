# I Built the Same Agent Twice: Hand-Rolled ReAct vs LangGraph

One challenge — "analyze this video" — implemented two ways. Here's what I learned.

I built the exact same agent twice: once as a hand-rolled ReAct loop, once as a LangGraph StateGraph.

What I found:
- ReAct: total control, but you own every edge case (loops, retries, token budget)
- LangGraph: conditional routing and state out of the box, but you trade some transparency

The framework earns its keep when the graph gets complex — multi-node routing, branches, recovery. For a single tool call? Raw ReAct is lighter.

I use both in my AI Sport Agent stack, depending on the job.

Team ReAct or team LangGraph?

**Hashtags:** #AgenticAI #AI #LangGraph #LLM
