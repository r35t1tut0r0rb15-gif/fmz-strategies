# #432914 Bollinger Band Trend Chaser -> `fmz_432914_band_tsi_adx_trend_chaser`

- FMZ source id: 432914 (lineage).
- Source: https://www.fmz.com/strategy/432914 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 16:51:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bands, an SMA, a TSI and the ADX |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [0.382, 1.0] x `ma_len` [200, 100]: **4 trials**; TSI 25 / 13 / 52 and ADX 13 / 20 fixed.

## Ambiguities resolved

- Band test as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
