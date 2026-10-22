# #458074 Multi Indicator Trend Following Strategy -> `fmz_458074_rsi3_extreme_stacked_ema_flags_reversal`

- FMZ source id: 458074 (lineage).
- Source: https://www.fmz.com/strategy/458074 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 17:07:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes in a stacked EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [3, 7] x `long_th` [80, 70] x `short_th` [20, 30]: **8 trials**; the EMA lengths and the exit levels fixed.

## Ambiguities resolved

- Flags followed as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
