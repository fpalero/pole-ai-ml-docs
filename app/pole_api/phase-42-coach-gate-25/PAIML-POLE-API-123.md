# Ticket: PAIML-POLE-API-123

## Title
Investigate why RAG/analyst image hashes become unverifiable (FC3 deep-dive)

## Status
🔒 FUTURE — investigations only; not scheduled. The user-confirmed fix for
the visible symptom (broken `<img>` → FC3 fail-closed gate) ships in
PAIML-POLE-API-122; this ticket owns the *why*.

## Description
Three SAMPLE-5 turns (VA-04 `extract_frames`/`frame_pose`, TP-03, IN-02)
failed ONLY on unloaded `<img>` tags: `broken images
/api/images/<hash>?token=…` — while the underlying answers were rich, fully
tool-grounded, and otherwise passing. The fail-closed gate in
PAIML-POLE-API-122 (`analyst_chatbot/blocks.py` `_resolves_image_hash is not
True → drop`) will stop emitting them, but it changes a symptom, not the
cause: these hashes *should* be servable.

Candidate causes to investigate (from the 122 evidence trail):
1. **TOCTOU between gate check and browser fetch.** `_resolves_image_hash`
   checks `resolve(hash)` during turn shaping; the `<img>` fetches seconds
   later. A file deleted/evacuated in between → endpoint 410 → broken. The
   `image_registry` L1→L2("all host paths")→miss + stale-eviction paths
   (`image_registry.py:355-385`) are candidates — is the file gone, or is it
   on another host path not probed?
2. **`None` from the registry import / resolve exception.** Lazy import
   failure (`blocks.py:309-310`) or an exception inside `resolve`
   (`316-317`) silently degrades to `None` → pass-through → 410. Are there
   transient Redis/OSError hiccups in `_l2_get` / `_split_l2_value` /
   `_checked_file` (`image_registry.py:214-223, 370-385`)? Correlate with
   backend logs at the failing timestamps (2026-09-11 ~06:19/06:32/06:42 UTC).
3. **Token auth vs readiness 401/403.** The `?token=` media URL may be
   failing auth/expiry, not the hash lookup — check `images.py` (200 | 410 |
   401/403) and whether the token is minted fresh per block or expires
   between shaping and fetch.
4. **Pure-hash vs full-path origin (issue #3 legacy).** Are these hashes
   minted from RAG `image_path` values that never existed in this
   container's `ALLOWED_ROOTS` (the original 093/issue-#3 class)?

Expected evidence deliverable at completion: log-correlated per-case
trace (which of 1–4 fired), a decision on whether the endpoint/authorship
should 200 instead of 410 with a placeholder, and whether `ensure_image_url`
should be stricter at mint-time (`answer_shaping.py:268-282`).

## Files Affected (investigation surface — no code change required yet)
- `app/pole_api/src/analyst_chatbot/image_registry.py`
- `app/pole_api/src/analyst_chatbot/blocks.py`
- `app/pole_api/src/analyst_chatbot/answer_shaping.py`
- `app/pole_api/src/analyst_chatbot/services.py` (image endpoint / token)
- backend logs on `ipsf-server` (pole-ai ns, pod `pole-api`) at the three
  failing timestamps + local reproduction on k3s-local

## Acceptance Criteria
- [ ] Root cause identified with a backend-log-correlated trace for each of
      the three failing hashes (or a harmonised single cause + why).
- [ ] Recommendation: endpoint 200-with-placeholder vs mint-time stricter
      validation vs both; approved by owner and then scheduled.

## Dependencies
- **Blocked By**: none (can run in parallel with 122; 122's fail-closed fix
  is the immediate symptom stop).
- **Blocks**: nothing.

## Estimated Effort
- [M]