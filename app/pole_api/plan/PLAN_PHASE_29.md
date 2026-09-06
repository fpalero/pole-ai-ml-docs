# Fase 29 — Chat hardening + coach cohort test isolation — 🔒 FUTURE

> Plan maestro: [PLAN.md](../PLAN.md) · Origen: phase-28 QA gate — phase 28
> (coach plain-language output, tickets PAIML-POLE-API-084/085/086/087) merged at
> `b1c3560`, QA GREEN on staging. The tester flagged two hardening follow-ups; the
> user approved them as a FUTURE phase — **do not start implementation**.
>
> Tickets: `phase-29-chat-hardening/PAIML-POLE-API-088.md`,
> `phase-29-chat-hardening/PAIML-POLE-API-089.md`.

## Contexto

Two independent hardening gaps surfaced during the phase-28 QA gate, both outside
the phase-28 scope:

1. **Raw-JSON echo (follow-up of API-087 + API-085):** API-087 normalized the wire
   `reply` to markdown synthesized from parsed blocks, and API-085 removed the dead
   `metric_deviation` contract from the prompt. But `analyst_chatbot/blocks.py`
   `parse_blocks()` has no all-unknown fallback: when an LLM reply parses to JSON
   yet contains ZERO valid block types (only unknown types like the legacy
   `metric_deviation`), the unknown items are dropped and the raw JSON array
   string leaks back out as md-wrapped `content` — the exact symptom API-087 was
   meant to kill.
2. **Production-DB leak in coach cohort reads (test isolation):** `CoachService`
   receives an injected `settings` object, but `_gather_insights()` and
   `_insight_z_context()` bypass it — they import the GLOBAL settings
   (`from core.config import settings as _settings`) and read
   `get_database(_settings.skeleton_db)` / `skeleton_cohort_signals` directly. In
   tests this hits the production `skeleton_data` DB instead of
   `skeleton_data_test`, violating the `_testing`-suffix guard convention
   (PLAN.md §4).

## Tickets

| Ticket | Scope | Estado |
| :--- | :--- | :--- |
| `PAIML-POLE-API-088` | Backend never echoes raw JSON for unknown block types (`parse_blocks` all-unknown fallback + `normalize_reply_text`/`blocks_to_text` guarantee) | 🔒 FUTURE |
| `PAIML-POLE-API-089` | Inject signal repo for coach cohort reads (optional `signal_repo` ctor param; full `*_test` isolation) | 🔒 FUTURE |

The two tickets are **independent** — no dependency between them, either may land
first.

## Tasks

- **API-088** — harden `analyst_chatbot/blocks.py` `parse_blocks()`: when a reply
  parses to JSON but yields zero valid block types, drop the unknown blocks and
  return a plain "no usable content" markdown block instead of md-wrapping the raw
  JSON array string. Extend the same guarantee to
  `normalize_reply_text()`/`blocks_to_text()` (the wire `reply` must never be a
  JSON array string). Keep the FE-friendly contract: valid mixed replies still
  drop unknown items silently. Tests: parametrized `parse_blocks` /
  `normalize_reply_text` cases for all-unknown, mixed, malformed, empty; assert no
  raw JSON in any md `content`.
- **API-089** — add an optional `signal_repo: HistogramRepository | None = None`
  constructor param to `CoachService` (default built from the injected
  `settings`), use it for both cohort reads (`_gather_insights()`,
  `_insight_z_context()`), and add tests that seed `skeleton_data_test` cohort
  docs and assert no production DB is read when a repo is injected.

## Acceptance

- No code path returns a raw JSON array string as chat `reply`/`content`, even for
  all-unknown LLM block payloads; mixed valid replies unchanged (unknown items
  dropped silently).
- Coach cohort reads in tests never touch production `skeleton_data`; injected
  repo against `skeleton_data_test` serves seeded cohort docs.
- `pixi run test-api` green, coverage ≥ 80%.

## Dependencies

- **Blocks:** None.
- **Blocked By:** Phase 28 (`b1c3560`, QA GREEN on staging) — context only; this
  phase re-opens no phase-28 ticket.
