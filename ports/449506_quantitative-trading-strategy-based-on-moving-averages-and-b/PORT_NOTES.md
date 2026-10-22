# #449506 Quantitative Trading Strategy Based on Moving Averages and Bollinger Bands -> `fmz_449506_ema4_sma50_corridor_cross_reversal`

- FMZ source id: 449506 (lineage).
- Source: https://www.fmz.com/strategy/449506 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-26 11:45:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C179). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings of an SMA corridor with wider-corridor exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_open` [1.2, 1.0] x `k_close` [1.6, 2.0]: **4 trials**; the SMA 50, EMA 4 and sd 30 fixed.

## Ambiguities resolved

- Closes act on held, non-reversed positions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
