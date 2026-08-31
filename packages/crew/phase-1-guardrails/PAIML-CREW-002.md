# Ticket: PAIML-CREW-002

## Title
Tool refactor (SUCCESS/ERROR states)

## Description
Refactor all tools in `crew/crew_implement.py` to return explicit, deterministic `SUCCESS:` / `ERROR:` prefixed messages using the `tool_result()` helper from `guardrails.py`. This prevents loop drift caused by ambiguous tool feedback.

## What to Do
- Import `tool_result` from `crew.guardrails`
- Refactor each tool in `build_crews()`:
  - `read_file(path)`:
    - Success: `tool_result(True, f"Read {len(content)} chars from {path}")`
    - Error: `tool_result(False, f"File not found: {path}")`
  - `write_file(path, content)`:
    - Success: `tool_result(True, f"Written {len(content)} chars to {path}")`
    - Error: `tool_result(False, f"Write failed: {path}")`
  - `run_shell(command)`:
    - Success (rc=0): `tool_result(True, f"Command completed: {command}")`  + stdout/stderr
    - Error (rc≠0): `tool_result(False, f"Command failed (rc={rc}): {command}")` + stdout/stderr
  - `list_files(path)`:
    - Success: `tool_result(True, f"Found {len(names)} files")` + file list
    - Error: `tool_result(False, f"Path not found: {path}")`
  - `run_tests()`:
    - Success (rc=0): `tool_result(True, "All tests passed")` + output
    - Error (rc≠0): `tool_result(False, f"Tests failed (rc={rc})")` + output
- Keep existing truncation logic (`_truncate()`)
- Ensure the original informational content (stdout, stderr, file list) is still included after the prefix

## Acceptance Criteria
- [ ] All 5 tools use `tool_result()` for their return values
- [ ] Success cases return `"SUCCESS: ..."` prefix
- [ ] Error cases return `"ERROR: ..."` prefix
- [ ] Original output content (stdout, file list, etc.) is preserved after the prefix
- [ ] Truncation still works correctly

## Dependencies
- **Blocked By**: PAIML-CREW-001, PAIML-CREW-007
- **Blocks**: PAIML-CREW-003, PAIML-CREW-005, PAIML-CREW-008
