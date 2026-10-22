# #468349 Bollinger Band Overbought Oversold Strategy -> `fmz_468349_connors_percent_b_three_day_dip_long`

- FMZ source id: 468349 (lineage).
- Source: https://www.fmz.com/strategy/468349 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 17:18:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | %b dips in an uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10] x `low_b` [0.2, 0.1] x `high_b` [0.8, 0.5]: **8 trials**; the SMA 200 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
