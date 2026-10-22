# #441142 Reversal Tracking Strategy -> `fmz_441142_avg_low_dip_above_sma200_pct_stop_long`

- FMZ source id: 441142 (lineage).
- Source: https://www.fmz.com/strategy/441142 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-06 10:03:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Average-low dips, average-high exits and the SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars` [5, 10] x `sl` [0.05, 0.03]: **4 trials**; SMA 200 fixed.

## Ambiguities resolved

- Stop active from the fill bar (the script's from the fill bar's close). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
