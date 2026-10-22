# #483791 Advanced Trend Capturing EMA Crossover Multi Indicator Confirmation Trading Strategy -> `fmz_483791_ema9_21_cross_sma200_rsi50_bb_basis_atr_bracket_reversal`

- FMZ source id: 483791 (lineage).
- Source: https://www.fmz.com/strategy/483791 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:36:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with trend, RSI and band-basis filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_multiplier` [1.0, 1.5] x `take_profit_multiplier` [2.0, 3.0]: **4 trials**; EMA 9 / 21, SMA 200, RSI 14, BB 20.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
