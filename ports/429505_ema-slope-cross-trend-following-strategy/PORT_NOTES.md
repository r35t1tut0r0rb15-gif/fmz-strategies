# #429505 EMA Slope Cross Trend Following Strategy -> `fmz_429505_ema_slope_compare`

- FMZ source id: 429505 (lineage).
- Source: https://www.fmz.com/strategy/429505 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 17:02:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Slope fractions and a moving-average side. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [130, 50] x `len2` [400, 200]: **4 trials**; smoothing 3 and trend EMA 200 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks

`none`
