# #482465 Hybrid EMA Momentum Trading System with Trend Persistence Analysis Strategy -> `fmz_482465_ema21_55_cross_supertrend_rsi_volume_atr_cooldown_2h_long_only`

- FMZ source id: 482465 (lineage).
- Source: https://www.fmz.com/strategy/482465 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:27:29). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Filtered EMA crossings with supertrend / RSI / volume / volatility confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cooldown_min` [360, 720] x `vol_mult` [1.5, 1.0]: **4 trials**; EMA 21 / 55 / 200, supertrend 3 / 14.

## Ambiguities resolved

- Cooldown on bar times. Volume = broker tick volume. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
