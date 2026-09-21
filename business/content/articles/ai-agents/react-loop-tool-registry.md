# Wrapping ML in an Agent: ReAct Loop + Tool Registry

**Section:** AI Agents · **Featured:** ✅

## What it delivers
An agent that turns ML capabilities into safe, callable tools — so a user can
"ask" for an analysis and get a real computation, not a hallucinated answer.

## How it's built
A bounded ReAct agent exposing ML as tools: sync tools for histogram and
similarity, job-mode tools for crop and shift, plus rate limiting and error
capture around every call.

## Proof
- **Code:** [packages/chatbot](https://github.com/fpalero/pole-ai-ml/tree/develop/packages)
- **Live in the pole app:** the AI Coach's chat tools on `pole-coach.duckdns.org`
