# #484584 Multi Moving Average Trend Capture and Crossover Confirmation Trading System -> `fmz_484584_ema14_50_100_200_stack_flag_loop_reversal`

- FMZ source id: 484584 (lineage).
- Source: https://www.fmz.com/strategy/484584 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 10:11:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked EMA trend states with an ATR filter for shorts |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`instant` [14, 10] x `longperiod` [200, 100]: **4 trials**; EMA 50 / 100, ATR 14.

## Ambiguities resolved

- The flags are followed in the source's order. REVERSAL INTENDED (via a same-bar close and short). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
