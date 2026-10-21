# #439050 RSI指标追踪止盈止损策略RSI-Target-and-Stop-Loss-Tracking-Strategy -> `fmz_439050_rsi_60_40_point_bracket`

- FMZ source id: 439050 (lineage).
- Source: https://www.fmz.com/strategy/439050 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 11:52:23). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; the short's immediate exit as a signal |
| 2 | ADAPT | Price-unit bracket -> fractions of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [0.00114, 0.01] x `rsi_len` [14, 21]: **4 trials**; target = 2 x stop.

## Ambiguities resolved

- Price-unit bracket -> fractions (longs); shorts closed after one bar (wrong target). REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
