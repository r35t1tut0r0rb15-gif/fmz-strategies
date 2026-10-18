# #436112 最后K线趋势跟踪策略Last-Candle-Strategy -> `fmz_436112_follow_last_day_bracket`

- FMZ source id: 436112 (lineage).
- Source: https://www.fmz.com/strategy/436112 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 12:15:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick amounts -> fractions of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.001, 0.01] x `tp_frac` [0.1, 0.02]: **4 trials**.

## Ambiguities resolved

- Previous bar's colour; tick amounts -> fractions. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
