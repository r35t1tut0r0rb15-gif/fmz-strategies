# #437547 Stock Quant Trading Strategy Combining Exponential Moving Average with Trailing Stop Loss and Percentage Stop Loss -> `fmz_437547_ema_cross_pct_stop_trail`

- FMZ source id: 437547 (lineage).
- Source: https://www.fmz.com/strategy/437547 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-03 16:25:54). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry plus a house trail |
| 2 | PASS | Percent stop and trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop and trail percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.07, 0.03] x `stop_pct` [0.02, 0.01]: **4 trials**; EMA 20 / 50 fixed.

## Ambiguities resolved

- Bar-high ratchet as a house percent trail (stated approximation). REVERSAL INTENDED. Mark trailing_stop. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
