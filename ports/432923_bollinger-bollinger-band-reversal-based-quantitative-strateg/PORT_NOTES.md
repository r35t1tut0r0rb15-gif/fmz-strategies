# #432923 基于波动带反转的-Bollinger-量化策略Bollinger-Band-Reversal-Based-Quantitative-Strategy -> `fmz_432923_bb_washout_pullback`

- FMZ source id: 432923 (lineage).
- Source: https://www.fmz.com/strategy/432923 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 17:44:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band ratios, band width in percent and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() cash quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `since_max` [57, 30]: **4 trials**; mult 20, RSI 5 / 70, the %B window and since_min 7 fixed.

## Ambiguities resolved

- Band multiplier 20 as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
