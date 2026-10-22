# #484580 布林带ATR风险回报比交易策略-Bollinger-Bands-ATR-Risk-Reward-Trading-Strategy -> `fmz_484580_bb20_2_extreme_state_atr2_2r_bracket_reversal`

- FMZ source id: 484580 (lineage).
- Source: https://www.fmz.com/strategy/484580 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 09:56:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Bollinger band extremes with an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bollinger_length` [20, 40] x `risk_reward_ratio` [2.0, 1.5]: **4 trials**; band 2 sd, ATR 14, stop 2 ATR.

## Ambiguities resolved

- Repeat state signals re-send the bracket; pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
