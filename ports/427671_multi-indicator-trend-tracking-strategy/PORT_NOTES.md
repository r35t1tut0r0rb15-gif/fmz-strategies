# #427671 Multi-Indicator Trend Tracking Strategy -> `fmz_427671_ma_speed_three_vote`

- FMZ source id: 427671 (lineage).
- Source: https://www.fmz.com/strategy/427671 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-23 15:19:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Indicator lengths and levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`avg_len` [50, 20] x `avg_roc_len` [10, 5] x `stoch_len` [14, 7]: **8 trials**; defaults 50 / 10 / 14 (the source's); MACD 12/26/9 and stochastic 80/20 fixed.

## Ambiguities resolved

- Source input close (default). REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`none`
