# #427680 Configurable Multi MA Crossover Voting System -> `fmz_427680_multi_ma_vote_atr_exit_long`

- FMZ source id: 427680 (lineage).
- Source: https://www.fmz.com/strategy/427680 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-23 15:52:06). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`profit_atr` [10, 5] x `loss_atr` [5, 2.5] x `ma_type` [1 WMA, 2 SMA]: **8 trials**; defaults 10 / 5 / WMA (the source's); pairs 2x4, 3x5, 4x6 and ATR 14 fixed.

## Ambiguities resolved

- Levels frozen from the signal bar. The close is a market exit signal on the bar's range (filled next open), only when the vote is not unanimous.
- The VWMA option (volume) is left out (check 8). Long only. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`none`
