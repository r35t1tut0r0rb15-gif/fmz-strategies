# #443125 The Compound Breakout Strategy -> `fmz_443125_connors_7bar_low_above_sma200_long`

- FMZ source id: 443125 (lineage).
- Source: https://www.fmz.com/strategy/443125 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-29 14:07:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Short-term lows in an uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`value1` [7, 5] x `value2` [7, 10]: **4 trials**; the SMA 200 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
