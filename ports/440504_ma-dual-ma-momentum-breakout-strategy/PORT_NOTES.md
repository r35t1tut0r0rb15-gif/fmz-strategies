# #440504 双MA动量突破策略Dual-MA-Momentum-Breakout-Strategy -> `fmz_440504_converging_ma_qqe_threshold`

- FMZ source id: 440504 (lineage).
- Source: https://www.fmz.com/strategy/440504 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 10:33:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Adaptive average and smoothed RSI threshold |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`thresh` [10, 20] x `atr_mult` [0.3, 1.0]: **4 trials**; the MA and RSI lengths fixed.

## Ambiguities resolved

- Stop from the signal bar's low / high; the step grows as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
