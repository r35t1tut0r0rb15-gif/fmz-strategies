# #477562 Multi Indicator Dynamic Momentum Cross Strategy -> `fmz_477562_ema_order_rsi_signal_state_reversal`

- FMZ source id: 477562 (lineage).
- Source: https://www.fmz.com/strategy/477562 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 14:00:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA order / RSI signal state, as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_avg_length` [14, 28] x `rsi_mid` [50, 55]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- "Short" = EMA 40 above EMA 55, as written; the distance averages reduce to distance / 5.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
