# #474670 Advanced Dynamic Trailing Stop with Risk Reward Targeting Strategy -> `fmz_474670_parallel_candles_3r_target_rsi_exit_long_ratchet_pending`

- FMZ source id: 474670 (lineage).
- Source: https://www.fmz.com/strategy/474670 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 14:57:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the R-multiple target as a fraction of the fill |
| 2 | PASS | Big-candle reversal pairs with an R target and an RSI exit; ratchet stop described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20] x `rr` [3.0, 2.0]: **4 trials**; ATR 14 x 1.0, RSI 75.

## Ambiguities resolved

- Ratchet stop pending (trailing_stop_pending). Side Long (default). Entries only from flat.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
