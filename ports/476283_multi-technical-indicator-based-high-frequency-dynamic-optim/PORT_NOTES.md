# #476283 Multi Technical Indicator Based High Frequency Dynamic Optimization Strategy -> `fmz_476283_ema9_21_cross_adx20_rsi_extreme_close_flat_only`

- FMZ source id: 476283 (lineage).
- Source: https://www.fmz.com/strategy/476283 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:58:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the na bracket places nothing, as written |
| 2 | PASS | EMA crossings with ADX and RSI filters, RSI extreme closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported; the ATR bracket inputs stored (never placed). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [20, 25] x `fast` [9, 5]: **4 trials**; slow EMA 21, RSI 14 / 70 / 30.

## Ambiguities resolved

- The avg-price bracket is na from flat and never placed, as written. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
