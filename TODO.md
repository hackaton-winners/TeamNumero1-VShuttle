# Backend TODO (Max 2 Hours)

## Goal
Ship a deterministic, crash-safe backend that processes `input.json` and outputs structured decisions:
- `GO` / `STOP` / `HUMAN_CONFIRM`
- with `reason`, `confidence`, `fused_text`, `id_scenario`

## Roles
- Person A: Infrastructure + Integration
- Person B: Algorithm + Tests

## 0:00-0:10 (Both)
- [ ] Lock output schema (`action`, `reason`, `confidence`, `fused_text`, `id_scenario`).
- [ ] Lock confidence thresholds for `GO`, `STOP`, `HUMAN_CONFIRM`.
- [ ] Confirm deterministic-only logic (no external AI/API calls).

## 0:10-0:25
### Person A
- [ ] Create backend structure: `src/`, `tests/`, entrypoint.
- [ ] Implement JSON loader + input validation (null-safe).

### Person B
- [ ] Draft fusion policy (sensor weights and tie-break rules).
- [ ] Draft normalization rules for noisy OCR text.

## 0:25-0:45
### Person A
- [ ] Build batch runner for all scenarios in `input.json`.

### Person B
- [ ] Implement `normalize_text` module:
- [ ] uppercase/trim/cleanup symbols.
- [ ] OCR fixes (example: `D1V1ET0` -> `DIVIETO`).
- [ ] basic phrase normalization (`ZTL`, `ECCETTO`, `BUS`, `NAVETTE`).

## 0:45-1:05
### Person A
- [ ] Add structured output writer (`output.json`).

### Person B
- [ ] Implement `fuse_readings` module:
- [ ] weighted fusion (`frontale > laterale > V2I`).
- [ ] handle offline sensors (`null`) without errors.
- [ ] output `fused_text`, `fusion_confidence`, evidence.

## 1:05-1:25
### Person A
- [ ] Integrate pipeline: load -> normalize -> fuse -> parse -> decide.

### Person B
- [ ] Implement semantic parser:
- [ ] detect divieto/ztl restrictions.
- [ ] detect exceptions (`ECCETTO BUS`, `ECCETTO NAVETTE L4`).
- [ ] parse time windows and weekday constraints.

## 1:25-1:40
### Person A
- [ ] Add fail-safe defaults for unexpected parse errors.

### Person B
- [ ] Implement decision engine:
- [ ] derive `GO`/`STOP`/`HUMAN_CONFIRM`.
- [ ] force `GO` for `ECCETTO BUS` cases.
- [ ] clear user-facing `reason` text.

## 1:40-1:50
### Person A
- [ ] Run full dataset smoke test.
- [ ] Confirm no crashes and one output row per input row.

### Person B
- [ ] Add quick edge-case tests:
- [ ] null sensor values.
- [ ] conflicting sensor texts.
- [ ] ambiguous low-confidence scenarios.
- [ ] time/day boundary cases.

## 1:50-2:00 (Both)
- [ ] Final end-to-end run.
- [ ] Verify deterministic behavior.
- [ ] Write backend README section:
- [ ] setup/run commands.
- [ ] fusion formula summary.
- [ ] edge-case behavior notes.

## Done Criteria
- [ ] Processes full `input.json` without crashing.
- [ ] Correctly handles null sensors and noisy OCR.
- [ ] Supports time/day and exception logic (`ECCETTO BUS`).
- [ ] Produces valid structured output for every scenario.
- [ ] Ready to ingest unseen secret scenarios without code changes.
