# #438026 双向追Momentum止盈止损策略Consecutive-Up-Down-Strategy-with-Reverse-and-SL-TP-Extension -> `fmz_438026_consecutive_closes_atr_trail`

- FMZ source id: 438026 (lineage).
- Source: https://www.fmz.com/strategy/438026 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 11:58:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; house trail |
| 2 | PASS | Close runs and ATR distances |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434998. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars_up` [3, 2] x `k_atr` [5.0, 3.0]: **4 trials**; bars down 4, ATR 14 and reward 5 fixed.

## Ambiguities resolved

- ATR stop from the signal bar; fixed-distance trail as the house volatility trail. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop`
