# #483021 高级双均线与超级趋势组合交易策略-Advanced-Dual-EMA-and-Supertrend-Combination-Trading-Strategy -> `fmz_483021_ema5_20_cross_supertrend_long`

- FMZ source id: 483021 (lineage).
- Source: https://www.fmz.com/strategy/483021 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:20:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages and Supertrend (ATR bands). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `slow` [20, 50]: **4 trials**; defaults 3 / 20 (the source's); EMA 5 and ATR 10 fixed.

## Ambiguities resolved

- `ta.supertrend` as TradingView documents it. Long only: opposite entries cannot occur. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
