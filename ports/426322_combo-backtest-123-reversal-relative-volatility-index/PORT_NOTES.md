# #426322 Combo Backtest 123 Reversal Relative Volatility Index -> `fmz_426322_combo_123_reversal_rvi`

- Source: https://www.fmz.com/strategy/426322 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 09:01:03). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426322` (Jaccard 0.65-0.80) with #438498 (PORT_CANDIDATE); best Jaccard 0.694 with #438498. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `rvi_period` [10, 14] x `buy_zone` [30, 40]: **8 trials**, defaults 14 / 10 / 30 (the source's); k smoothing 1, d 3, level 50 and sell zone 70 fixed.

## Ambiguities resolved

- RVI below the buy zone maps to -1 and above the sell zone to +1, as HPotter's code does.
- nz() restarts the nU / nD recursions from 0 after the stdev warm-up; na inputs propagate as in Pine.
- Pine population stdev; stoch over a zero range is na.
- "Trade reverse" off (source default).
- FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
