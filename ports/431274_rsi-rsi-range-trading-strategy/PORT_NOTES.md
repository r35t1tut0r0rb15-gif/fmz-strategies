# #431274 RSI区间震荡交易策略RSI-Range-Trading-Strategy -> `fmz_431274_rsi2_alternating_extremes`

- FMZ source id: 431274 (lineage).
- Source: https://www.fmz.com/strategy/431274 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-06 16:12:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked stops |
| 2 | PASS | RSI levels and a percentage stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-risk value (unused by the orders) stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_level` [11, 20] x `stop_pct` [0.5, 2.0]: **4 trials**; RSI 2 fixed; short level = 102 - buy level (91 at 11, 82 at 20).

## Ambiguities resolved

- Close-checked stops from the signal close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
