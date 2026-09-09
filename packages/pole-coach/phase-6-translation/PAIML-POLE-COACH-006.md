# PAIML-POLE-COACH-006 — Phase 6 (F): Hy-MT2 translation + glossary + cache

- **Status:** 📋 PLANNED
- **Blocks:** —
- **Blocked By:** PAIML-POLE-COACH-001, PAIML-POLE-COACH-002

## Goal
English-pivot translation for the coach: non-English queries translate to English
before routing/retrieval, answers translate back to the user's language — via
Hy-MT2-1.8B served on existing infrastructure, protected by a catalog-built
glossary, and cached in Redis. No new serving runtime, no torch in-process.

## Architectural context
- **Database:** Redis (already a runtime dep): L1 normalized exact-hash keys
  (`tr:{src}:{tgt}:{sha}`, ~30-day TTL) + L2 semantic near-match table
  (MiniLM embeddings, cosine ≥0.95, placeholders-first). Keys carry
  glossary version + model id; both translation directions cached.
- **Providers (no new infra):** `translator.py` calls `build_llm()` with a new
  `TRANSLATOR_MODEL` setting — local (`ollama`): `hf.co/tencent/Hy-MT2-1.8B-GGUF:Q4_K_M`
  pulled once on the host; staging (`openrouter`): `tencent/hy-mt2-1.8b`.
  No Ollama on ipsf-server, no Docker image, no transformers/torch.
- **Glossary:** built from `trick_catalog.json` (names + aliases, ~500 tricks) +
  static codes (M-01…M-05, joint names); passed via Hy-MT2's glossary workflow.
- **Caching/performance:** English pays zero (gated); caps sized per field
  (query ~128, answer ~1024); p95 latency spike must fit turn wall-clock budgets.
- **Scalability/resilience:** translator fails → English answer (never blank);
  provider down → existing `FALLBACK_ADVICE`. Translator calls tagged in
  `llm_quota` (visible per-user spend).
- **External:** Ollama host (local) / OpenRouter (staging). HF pull once for local.

## Scope (in)
1. `packages/pole_coach/src/pole_coach/translator.py` (own file): detect+translate
   entry, glossary-attached back-translation in formatter path, L1+L2 Redis cache,
   quota tagging, English fallback.
2. Glossary builder from the catalog + static codes; glossary versioning.
3. `Settings.translator_model` (provider-aware default + env override) + Helm
   `translatorModel` value/ConfigMap (**infra repo** change).
4. Host Ollama pull (local dev); OpenRouter model name (staging).
5. Evals: ES round-trip (terms survive untranslated), near-miss threshold tuning
   (mount vs mount-flag must NOT match), latency spike on target hardware.
6. Unit tests (cache hits/misses, glossary placeholders, fallback, quota tags).

## Scope (out)
Transformers/torch in-process serving (dropped); dedicated Hy-MT2 Docker image
(deferred unless spend/privacy mandates); multilingual cross-encoder (pivot removes
the need); touching existing slices' English-only LANGUAGE RULE (stays).

## Tasks
- 6.1 `translator.py` + glossary builder + Redis L1/L2.
- 6.2 Entry + formatter wiring (retrofit hooks into 002 nodes).
- 6.3 Settings + Helm + host pull docs.
- 6.4 Evals (round-trip, threshold, spike) + unit tests.

## Acceptance
- [ ] ES question → EN pipeline → ES answer, trick names/metric codes intact.
- [ ] Near-miss pairs never share a cache entry; p95 within turn budget.
- [ ] Translator spend visible in quota; unit suite green.

## Verification
`pixi run test-pole-coach`, translation scenarios, quota report. Then **start the
integration test** per ticket DoD.

## Risks
- OpenRouter micro-cost per non-English turn → bounded by cache + caps; measured
  via quota before any further optimization.
- Glossary staleness on catalog updates → versioned keys bust the cache.

## Definition of Done
Unit suite + translation evals green → run the integration aggregator and report.
