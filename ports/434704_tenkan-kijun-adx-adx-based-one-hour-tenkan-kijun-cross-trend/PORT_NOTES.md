# #434704 基于一小时TENKAN-KIJUN交叉的ADX趋势跟踪策略ADX-Based-One-Hour-TENKAN-KIJUN-Cross-Trend-Tracking-Strategy -> `fmz_434704_tk_cross_adx`

- FMZ source id: 434704 (lineage).
- Source: https://www.fmz.com/strategy/434704 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-08 15:37:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Donchian-midline crosses and an ADX level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [18, 9] x `adx_min` [12, 25]: **4 trials**; Kijun 58 and ADX 14 / 14 fixed.

## Ambiguities resolved

- ADX level 12 as coded (input 20 unused). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
