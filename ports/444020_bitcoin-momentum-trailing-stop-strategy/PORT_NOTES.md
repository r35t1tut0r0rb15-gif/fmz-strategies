# #444020 Bitcoin Momentum Trailing Stop Strategy -> `fmz_444020_weekly_ema_momentum_ratchet_swing_stop_long`

- FMZ source id: 444020 (lineage).
- Source: https://www.fmz.com/strategy/444020 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 16:20:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks |
| 2 | PASS | Weekly trend with a caution filter; ratcheting swing stop at the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [20, 10] x `trail_lookback` [7, 14]: **4 trials**; the ATR length and the caution multiplier fixed.

## Ambiguities resolved

- Weekly EMA from completed weeks, then one daily bar back. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
