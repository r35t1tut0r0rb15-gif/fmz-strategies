# #443118 基于MACD和布林带的Momentum-Trend策略Momentum-Trend-Strategy-Based-on-MACD-and-Bollinger-Bands -> `fmz_443118_ma_diff_own_band_reentry_reversal`

- FMZ source id: 443118 (lineage).
- Source: https://www.fmz.com/strategy/443118 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-29 13:49:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA difference against its own bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [40, 20] x `mult` [2.0, 1.5]: **4 trials**; the SMA lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
