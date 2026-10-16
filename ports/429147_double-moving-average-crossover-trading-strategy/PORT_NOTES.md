# #429147 Double Moving Average Crossover Trading Strategy -> `fmz_429147_ema15_95_session_cross`

- FMZ source id: 429147 (lineage).
- Source: https://www.fmz.com/strategy/429147 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-13 15:40:49). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; clock-time exits as signals. |
| 2 | PASS | Moving-average crosses only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy(), contract size and the off-by-default TP / SL stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len1` [15, 10] x `ma_len2` [95, 50]: **4 trials**; EMA type and the UTC sessions fixed.

## Ambiguities resolved

- Exchange time taken as UTC. A cross on the start bar wins over the start-bar entry (same direction anyway).
- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
