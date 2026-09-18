# Your LLM Agent Will Ignore Your Prompt Rules

"Don't do X" in a prompt won't stop an agent from doing X. Build rails instead.

Prompt instructions are suggestions, not guarantees. So I built guardrails that can't be talked around:

- Word-matched confirmation (never an LLM judgment)
- Tool-call gating on session state
- A rephrase budget for off-script recovery
- Synthetic state blocks injected per turn

Safety that survives prompt drift — deterministic, testable, boring.

This is the guardrail layer in my AI Sport Agent's coaching agent.

How do you guard your agents?

**Hashtags:** #AgenticAI #AI #LLM #PromptEngineering
