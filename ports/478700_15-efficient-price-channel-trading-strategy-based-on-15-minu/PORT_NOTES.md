# #478700 基于15分钟突破的高效价格通道交易策略-Efficient-Price-Channel-Trading-Strategy-Based-on-15-Minute-Breakout -> `fmz_478700_0915utc_candle_range_breakout_reversal`

- FMZ source id: 478700 (lineage).
- Source: https://www.fmz.com/strategy/478700 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:49:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Opening-range breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`capture_hour` [9, 13] x `capture_minute` [15, 30]: **4 trials**.

## Ambiguities resolved

- UTC capture bar, no DST; the backtest start-date close_all not ported. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "opening_range"`.

## Marks

`none`
