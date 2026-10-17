# #433912 动态波幅捕捉RSI-布林带策略Volatility-Capture-RSI-Bollinger-Band-Strategy -> `fmz_433912_ratchet_band_rsi`

- FMZ source id: 433912 (lineage).
- Source: https://www.fmz.com/strategy/433912 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 14:17:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A band-following line and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 25] x `mult` [2.7183, 2.0]: **4 trials**; RSI 10 / SMA 5 and the levels fixed.

## Ambiguities resolved

- Statement order kept (entry crosses on the previous line, exits on the updated one). REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
