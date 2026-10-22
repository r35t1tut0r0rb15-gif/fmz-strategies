# #453648 Elliott-Wave-Stochastic-EMA-Strategy-Elliott-波动随机EMA策略 -> `fmz_453648_close_ema5_cross_reversal`

- FMZ source id: 453648 (lineage).
- Source: https://www.fmz.com/strategy/453648 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 14:56:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / EMA 5 crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [5, 10, 20]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
