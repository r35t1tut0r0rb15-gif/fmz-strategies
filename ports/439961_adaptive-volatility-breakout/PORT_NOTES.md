# #439961 Adaptive Volatility Breakout -> `fmz_439961_bollinger_breakout_ema_spread_vfi_1h_long_only`

- FMZ source id: 439961 (lineage).
- Source: https://www.fmz.com/strategy/439961 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 12:43:43). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts with EMA-spread and volume-flow confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [1.5, 2.0] x `vfi_len` [130, 65]: **4 trials**; Bollinger 20, EMA 20 / 50, VFI thresholds 14 / 19.

## Ambiguities resolved

- Sessions feed no order; VFI unsmoothed as written. Volume = broker tick volume (VFI). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
