# #436500 Dual Moving Average Reversal Strategy -> `fmz_436500_ma_pullback_dip_buyer`

- FMZ source id: 436500 (lineage).
- Source: https://www.fmz.com/strategy/436500 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-25 13:24:14). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Stop is a close test, a fraction of the buy price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the stop percent stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma2` [10, 20] x `trigger` [14, 20] x `stop_pct` [0.15, 0.10]: **8 trials**.

## Ambiguities resolved

- Stop tested on the close against the fill-bar open; no stop on the fill bar. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
