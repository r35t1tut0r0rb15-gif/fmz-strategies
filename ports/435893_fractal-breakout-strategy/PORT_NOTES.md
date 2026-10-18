# #435893 Fractal Breakout Strategy -> `fmz_435893_fractal_top_breakout_long`

- FMZ source id: 435893 (lineage).
- Source: https://www.fmz.com/strategy/435893 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-19 15:32:57). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Valuewhen occurrence and lagged copies as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n_time` [3, 5] x `use_longer` [True, False]: **4 trials**.

## Ambiguities resolved

- Fractal price taken at the confirming bar; occurrence 1. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "fractal_breakout"`.

## Marks

`none`
