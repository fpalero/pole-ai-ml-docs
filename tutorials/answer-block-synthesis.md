# Deterministic answer and block synthesis for chatbot tools

> **Diataxis type:** tutorial (learning by doing). Follow along step by step and
> you will finish with a working synthesiser for a new chatbot tool type,
> modelled on a real change from the codebase. Theory is kept to a minimum —
> where you need background, you are pointed at the reference instead.

## What you will build

The analyst chatbot answers with typed **blocks** (`md`, `image`,
`video_segment`, `metric_matrix`, `drills`, …). The frontend renders each block
type as a card — an `image` block becomes a picture, a `metric_matrix` block
becomes a table.

When a tool returns data, the backend should turn that data into typed blocks
**deterministically, in code**. Without this, the raw tool payload leaks into
the chat as prose.

You have seen this failure mode: RAG image queries (`query_pole`,
`query_biomechanics`, `query_calisthenics`, `query_psicology`) returned hits
carrying image paths, but no code converted them into `image` blocks. When the
LLM failed to emit the blocks itself, the user saw raw JSON as text inside an
`md` block:

```text
[{"type": "image", "src": "/api/images/0142-07", ...}]
```

instead of rendered images. That story is ticket
`docs/app/pole_api/phase-35-rag-image-blocks/PAIML-POLE-API-109.md` — read it
alongside this tutorial. By the end, you will have replayed its fix and
understood the recipe for any new tool type.

**Prerequisites:** a checkout of `pole-ai-ml` with `app/pole_api` importable,
and familiarity with running `pixi run test-api`.

## The two-paths mental model

There are two ways an `image` block can reach the user:

1. **Deterministic path.** A synthesiser function converts the tool result
   into typed blocks in code. It always runs, it always behaves the same way,
   and it never invents content.
2. **LLM-mediated path.** The model is prompted to emit blocks itself. It
   sometimes works — and sometimes wraps the JSON in prose, drops the block,
   or pastes the call syntax verbatim.

For data-driven output (images, metrics, segments) the deterministic path is
preferred: the data is already in the tool result, so deriving blocks from it
is mechanical. Reserve the LLM path for prose. (For the full rationale, see
the module docstring in `app/pole_api/src/analyst_chatbot/answer_shaping.py`.)

## The three registration points

Every deterministic synthesis is exactly three edits in one file —
`app/pole_api/src/analyst_chatbot/answer_shaping.py`:

1. Declare the tool in `TOOL_EXPECTED_BLOCKS` (tool name → expected block
   type or types).
2. Write a synthesiser `_blocks_for_<tool>(result)` returning a list of typed
   block dicts.
3. Register it in `_TOOL_SYNTHESIZERS` (tool name → synthesiser).

The rest — guards, de-duplication, exception safety — already exists and you
will reuse it unchanged. Now you will apply the recipe to the RAG image case.

## Step A — Declare the expected block type

Open `answer_shaping.py` and find `TOOL_EXPECTED_BLOCKS` (near the top of the
file). Notice that analysis tools such as `extract_frames` and `get_coach_pose`
already map to `("image",)`, while the four RAG tools are absent. Add them:

```python
TOOL_EXPECTED_BLOCKS: dict[str, tuple[str, ...]] = {
    "extract_frames": ("image",),
    "get_coach_pose": ("image",),
    # ... existing entries unchanged ...
    "query_pole": ("image",),
    "query_biomechanics": ("image",),
    "query_calisthenics": ("image",),
    "query_psicology": ("image",),
}
```

This declaration is what allows `ensure_tool_blocks()` to notice, later, that
an `image` block is owed for a successful RAG call. Nothing renders yet — you
have only stated the expectation.

## Step B — Write the synthesiser

Now write the function that fulfils that expectation. Place it beside the
other `_blocks_for_*` synthesisers (after `_blocks_for_coach_pose` reads
naturally — compare the two to see the pattern: extract locator, convert to
served URL, build the block).

A RAG tool result carries `results`, a list of hits. Each hit may carry an
`image_path` (a raw filesystem locator such as
`data/_OceanofPDF.../figure.png`), an `image_title`, and a `source_document`.
Your function converts each usable hit into the frontend's `image` block
shape — `{ type: 'image'; src: string; caption?; source_document?;
phase_label?; chips? }` — keeping only the fields the tool result can ground:

```python
from analyst_chatbot import image_registry


def _blocks_for_rag_image(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    results = result.get("results")
    if not isinstance(results, list):
        return blocks
    for hit in results:
        if not isinstance(hit, dict):
            continue
        image_path = hit.get("image_path")
        if not isinstance(image_path, str) or not image_path.strip():
            continue
        url = image_registry.ensure_image_url(image_path)
        if url is None:
            continue
        block: dict[str, Any] = {"type": "image", "src": url}
        title = hit.get("image_title")
        if isinstance(title, str) and title.strip():
            block["caption"] = title.strip()
        source = hit.get("source_document")
        if isinstance(source, str) and source.strip():
            block["source_document"] = source.strip()
        blocks.append(block)
    return blocks
```

Notice three behaviours you should preserve exactly:

- **Empty or missing `image_path` → skip the hit.** There is nothing to
  render, so emit nothing.
- **Unmappable path (`ensure_image_url()` returns `None`) → skip the hit.**
  `None` means the locator is outside every known root, contains `..`, or has
  an unknown layout — never a servable image.
- **Missing title → omit the `caption` key entirely** rather than sending an
  empty caption. The same applies to `source_document`.

And notice one behaviour that surprises newcomers: a path that maps to a known
root but whose file does not exist on disk **still yields a block**. That is
deliberate. `ensure_image_url()` hashes deterministically even when the file
is absent (see `_ensure_fs_path()` in
`app/pole_api/src/analyst_chatbot/image_registry.py`, including its
`data/`-prefixed RAG path handling near the end of the function); serving a
404 at request time is the serve layer's job, not the synthesiser's. Never
reimplement this logic — always reuse `image_registry.ensure_image_url()`.

## Step C — Register the synthesiser

Find `_TOOL_SYNTHESIZERS` (just above `blocks_for_tool_call`, around line
568). Point all four RAG tools at your new function:

```python
_TOOL_SYNTHESIZERS = {
    # ... existing entries unchanged ...
    "query_pole": _blocks_for_rag_image,
    "query_biomechanics": _blocks_for_rag_image,
    "query_calisthenics": _blocks_for_rag_image,
    "query_psicology": _blocks_for_rag_image,
}
```

You have now completed the three registration points. If you run the focused
tests at this stage (`pixi run test-api -k rag_image`), you will see the new
synthesiser exercised end to end — which brings us to invocation and testing.

## How synthesis is invoked

You do not call your synthesiser directly in production code. Two existing
functions do it for you (in the same module, lines 582–629 — read them now,
they are short):

- `blocks_for_tool_call(name, result)` looks up the synthesiser for `name`
  and runs it. It returns `[]` for error results (a dict containing `error`),
  for unknown tools, and for results with no renderable payload. Any exception
  raised by a synthesiser is caught and logged, returning `[]` — synthesis
  must never break the turn. Only blocks whose `type` is a known block type
  survive.
- `ensure_tool_blocks(blocks, tool_calls)` walks the turn's successful tool
  calls in order, synthesises each one's blocks, and appends a block **only
  if its type is not already present** — so when the LLM did emit a proper
  `image` block, your deterministic one is not duplicated.

That de-duplication is why the declaration in Step A matters separately from
the synthesiser: it is the expectation map that drives the append-if-missing
pass.

## Testing your synthesiser

Add a test class to
`app/pole_api/tests/test_analyst_chatbot_answer_shaping.py`, beside the
existing synthesis tests (`TestExtractFramesImage` shows the house style).
First add a helper that builds a minimal RAG result:

```python
def _rag_result(*hits):
    return {"results": list(hits)}
```

Then write a `TestRagImageSynthesis` class covering the contract from Step B:

| Case | Input | Expectation |
| :--- | :--- | :--- |
| Valid path | hit with `image_path` under a known root | one `image` block; `src` matches the hash-URL pattern below |
| Missing file | `image_path` under a known root, file absent | block **still** created (deterministic URL; the 404 is the serve layer's concern) |
| Empty/missing path | hit with `""` or no `image_path` | hit skipped, no block |
| Title + source | hit with `image_title` and `source_document` | `caption` and `source_document` populated |
| No title | hit without `image_title` | **no** `caption` key on the block |
| All tool names | same result via `blocks_for_tool_call()` for `query_pole`, `query_biomechanics`, `query_calisthenics`, `query_psicology` | each returns the image blocks |
| Append pass | `ensure_tool_blocks([md_block], [rag_call])` | `image` block appended when absent; not duplicated when present |

Assert served URLs with the hash-URL pattern:

```python
import re

_IMAGE_HASH_RE = re.compile(r"^/api/images/[0-9a-f]{32}$")

assert _IMAGE_HASH_RE.match(block["src"]), block["src"]
```

(The 32-hex core comes from `path_hash()` — `sha256("root_id:relpath")`
truncated to 32 characters — formatted by `image_url_for_hash()` as
`/api/images/<hash>`. Both live in `image_registry.py`.)

Run the focused suite and then the full file to check for regressions:

```bash
pixi run test-api -k rag_image
```

## What you have built

You declared an expectation (`TOOL_EXPECTED_BLOCKS`), wrote a synthesiser
(`_blocks_for_rag_image`), registered it (`_TOOL_SYNTHESIZERS`), and tested
the contract — reusing `image_registry.ensure_image_url()` for every
path-to-URL conversion. The same three registration points apply to the next
tool type: declare, synthesise, register, test.

**Where to go next:** the reference for exact field shapes is the
`answer_shaping.py` module itself (`blocks_for_tool_call`,
`ensure_tool_blocks`); the decision context for this recipe is ticket
PAIML-POLE-API-109; the URL-mapping rules (roots, `data/` prefixes, legacy
URLs) are documented in `image_registry.ensure_image_url()`.
