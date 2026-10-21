# #438774 即时突破波动率EMA趋势策略Zero-Lag-Volatility-Breakout-EMA-Trend-Strategy -> `fmz_438774_ema_ratio_band_breakout`

- FMZ source id: 438774 (lineage).
- Source: https://www.fmz.com/strategy/438774 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 12:00:25). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ratio to an EMA and its Bollinger band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lx` [200, 100] x `bbmult` [2.0, 1.5]: **4 trials**; binary mode on.

## Ambiguities resolved

- Binary mode: exits only at the opposite entry. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
