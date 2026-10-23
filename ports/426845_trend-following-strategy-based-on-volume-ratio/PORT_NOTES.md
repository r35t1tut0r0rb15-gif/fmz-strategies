# #426845 Trend Following Strategy Based on Volume Ratio -> `fmz_426845_bull_bear_volume_flow_roc_filter_pct_stop_reversal`

- FMZ source id: 426845 (lineage).
- Source: https://www.fmz.com/strategy/426845 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 19:53:55). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Volume-flow balance with a rate-of-change filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [6, 12] x `sl` [0.02, 0.04]: **4 trials**; ROC 12, change 2 %, TP 900 %.

## Ambiguities resolved

- Re-entry after a stop while the condition holds, as written. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`coarse_bar_stop`
