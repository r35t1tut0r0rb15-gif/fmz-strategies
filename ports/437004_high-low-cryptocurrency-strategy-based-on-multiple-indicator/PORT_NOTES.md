# #437004 High Low Cryptocurrency Strategy Based on Multiple Indicators -> `fmz_437004_rising_highs_filters_pct_bracket`

- FMZ source id: 437004 (lineage).
- Source: https://www.fmz.com/strategy/437004 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 14:16:16). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the entry |
| 2 | PASS | Percent bracket, dimensionless filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.005, 0.01] x `tp` [0.15, 0.05]: **4 trials**; every indicator setting fixed.

## Ambiguities resolved

- Per-bar tick bracket read as fixed percents of the entry; CCI sign as the colour test. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
