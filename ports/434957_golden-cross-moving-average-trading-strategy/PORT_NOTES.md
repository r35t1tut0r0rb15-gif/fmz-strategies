# #434957 Golden Cross Moving Average Trading Strategy -> `fmz_434957_golden_cross_sma100_exit`

- FMZ source id: 434957 (lineage).
- Source: https://www.fmz.com/strategy/434957 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-11 11:37:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | Average crosses and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `sl_pct` [0.25, 0.05]: **4 trials**; SMA 100 / 200 and the 300 % target fixed.

## Ambiguities resolved

- Same-bar exit signal on an entry bar dropped; date window dropped. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
