# #426804 晨星K线突破策略Morning-Star-Breakout-Strategy -> `fmz_426804_doji_morning_star_ema60_lowest_low_stop_trail_long`

- FMZ source id: 426804 (lineage).
- Source: https://www.fmz.com/strategy/426804 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-14 16:36:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lowest-low stop, percent target and a house trail |
| 2 | PASS | Doji / morning-star candles in an EMA 60 up-trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity, capital 10000, commission 0.075 %, slippage 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_len` [100, 50] x `tp` [0.09, 0.05]: **4 trials**; trail 1 % / 0.5 %, EMA 60.

## Ambiguities resolved

- Lowest-low stop fixed at the signal; trail approximated by the house percent trail. The MFI close never acts.
- Long only. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop, trailing_stop_pending`
