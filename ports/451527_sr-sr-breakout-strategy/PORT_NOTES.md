# #451527 SR-突破策略-SR-Breakout-Strategy -> `fmz_451527_pivot_zone_breakout_reversal`

- FMZ source id: 451527 (lineage).
- Source: https://www.fmz.com/strategy/451527 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 16:30:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Breakouts of multi-tested pivot zones |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd` [5, 10] x `bo_len` [71, 150] x `width_pct` [3.0, 5.0]: **8 trials**; minimum tests 2 fixed.

## Ambiguities resolved

- SL / TP off by default: no exits. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
