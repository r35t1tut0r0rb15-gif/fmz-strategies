# #439860 利用RSI指标和均线指标的量化策略RSI-and-Moving-Average-Breakout-Strategy -> `fmz_439860_gms_rsi_sma5_exit_sma200_above`

- FMZ source id: 439860 (lineage).
- Source: https://www.fmz.com/strategy/439860 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 14:31:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and SMA sides |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND439860. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `trend_length` [200, 100]: **4 trials**; 70 / 30 and the SMA 5 exits fixed.

## Ambiguities resolved

- Both sides above the SMA 200, as written. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
