# #431409 Multi Indicator Scoring Trading Strategy -> `fmz_431409_technicals_rating`

- FMZ source id: 431409 (lineage).
- Source: https://www.fmz.com/strategy/431409 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-07 16:16:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop and trail are house stops |
| 2 | PASS | Indicator ratings and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 50 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_strength` [1.1, 0.7] x `activate` [0.15, 0.05]: **4 trials**; the indicator set, period 14, stop 3 ATR and trail 2 ATR fixed.

## Ambiguities resolved

- Stop fixed at the signal bar's ATR; the trail as the house volatility trail. Marks trailing_stop, coarse_bar_stop.
  REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`trailing_stop, coarse_bar_stop`
