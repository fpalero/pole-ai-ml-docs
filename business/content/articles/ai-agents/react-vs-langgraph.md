# Custom ReAct vs LangGraph: Two Ways to Build the Same Agent

**Section:** AI Agents · **Featured:** ✅

## What it delivers
The judgment to pick the right agent framework for the job — not a dogmatic
"always LangGraph" answer — so you don't over- or under-engineer.

## How it's built
One challenge — "analyze this video" — implemented twice: a hand-rolled ReAct
loop versus a StateGraph with conditional routing, compared on trade-offs,
token accounting, and where the framework earns its keep.

## Proof
- **Code:** [packages/chatbot](https://github.com/fpalero/pole-ai-ml/tree/develop/packages) · [packages/pole_coach](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole_coach)
- **Live in the pole app:** ReAct fallback behind the LangGraph coach
