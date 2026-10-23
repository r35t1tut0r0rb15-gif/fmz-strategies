# #436244 基于RSI和交易量的阴阳双轨趋势交易策略YinYang-RSI-Volume-Trend-Trading-Strategy -> `fmz_436244_yinyang_rsi_volume_purchase_zone_reentry_reversal`

- FMZ source id: 436244 (lineage).
- Source: https://www.fmz.com/strategy/436244 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 14:29:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; zone-based close conditions in the signals |
| 2 | PASS | Volume-weighted RSI purchase-zone re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [80, 40] x `sl_mult` [0.1, 0.5]: **4 trials**.

## Ambiguities resolved

- Flags as written (reset after Entry). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "zone_reentry"`.

## Marks

`none`
