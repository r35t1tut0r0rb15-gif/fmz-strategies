# #443099 Dynamic Engulfing Trend Strategy -> `fmz_443099_supertrend_engulfing_bar_range_bracket`

- FMZ source id: 443099 (lineage).
- Source: https://www.fmz.com/strategy/443099 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-29 11:24:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | ADAPT | Tick offset -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `engulf_pct` [50, 70]: **4 trials**; the ATR period, the boring share and the tick offset fixed.

## Ambiguities resolved

- Signal-bar bracket with the tick offset as a fraction. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
