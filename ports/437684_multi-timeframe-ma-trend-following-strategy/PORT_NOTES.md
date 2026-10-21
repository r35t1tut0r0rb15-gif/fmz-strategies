# #437684 Multi timeframe MA Trend Following Strategy -> `fmz_437684_early_trend_dip_pct_bracket_long`

- FMZ source id: 437684 (lineage).
- Source: https://www.fmz.com/strategy/437684 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-04 17:43:17). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the entry |
| 2 | PASS | Percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 7, the percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.03, 0.015] x `sl` [0.03, 0.015]: **4 trials**; SMA 9 / 100 / 200 fixed.

## Ambiguities resolved

- Pyramiding adds left out; per-bar tick bracket read as fixed percents. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
