# #438507 Dual Moving Average Crossover Strategy -> `fmz_438507_parker_ma_state_short_held`

- FMZ source id: 438507 (lineage).
- Source: https://www.fmz.com/strategy/438507 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-12 14:59:18). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA state comparison (degenerate as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [30, 10] x `len2` [60, 120]: **4 trials**; the signal does not depend on them (as written).

## Ambiguities resolved

- Degenerate state logic: a short sent on every bar, one short held. Short only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
