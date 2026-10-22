# #452691 基于相对强弱指数RSI和滑动平均SMA的波动率标准差DEV交易策略-Standard-Deviation-DEV-Trading-Strategy-Based-on-Relative-Strength-Index-RSI-and-Simple-Moving-Average-SMA -> `fmz_452691_sd_band_reentry_rsi_extreme_reversal`

- FMZ source id: 452691 (lineage).
- Source: https://www.fmz.com/strategy/452691 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 10:57:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SD-band re-entries with RSI extremes |
| 3 | PASS | Spot pair in the header only (the source sends shorts as written). |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `entry_sd` [1.5, 2.0] x `exit_sd` [0.5, 0.0]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
