# #431898 Comprehensive Automated Trading Moving Average Rainbow Strategy -> `fmz_431898_ma_rainbow_pullback`

- FMZ source id: 431898 (lineage).
- Source: https://www.fmz.com/strategy/431898 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-13 10:44:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; levels fixed at entry (rule 2) |
| 2 | PASS | EMA ribbons and reward ratios |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`target_factor` [1.6, 1.0] x `scale` [1.0, 2.0]: **4 trials**; scale multiplies all twelve EMA lengths.

## Ambiguities resolved

- Pending (not emitted as written): the turnover-trend limit at the highest high. Levels from the signal, re-based
  on the fill. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks

`trailing_stop_pending`
