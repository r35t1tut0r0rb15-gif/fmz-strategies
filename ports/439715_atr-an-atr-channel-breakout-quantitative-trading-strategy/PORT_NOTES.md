# #439715 基于ATR通道突破的量化交易策略An-ATR-Channel-Breakout-Quantitative-Trading-Strategy -> `fmz_439715_sma150_atr_channel_breakout`

- FMZ source id: 439715 (lineage).
- Source: https://www.fmz.com/strategy/439715 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 12:00:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR channel and SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`offset` [4.0, 2.0] x `sma_length` [150, 50]: **4 trials**; ATR 30 fixed, the same offset both sides.

## Ambiguities resolved

- Closes after entries. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
