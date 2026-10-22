# #483679 Dual Moving Average Crossover with Stochastic Filter and Adaptive Trailing Stop Strategy -> `fmz_483679_close_sma34_cross_sma200_trend_stoch_2_4pct_bracket_reversal`

- FMZ source id: 483679 (lineage).
- Source: https://www.fmz.com/strategy/483679 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-25 11:05:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | SMA crossings with a trend and Stochastic filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_percent` [2.0, 1.0] x `take_profit_percent` [4.0, 2.0]: **4 trials**; SMA 34 / 200, Stochastic 9 / 3 / 3.

## Ambiguities resolved

- The bracket is ported from the fill; the break-even re-send on repeat signals is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
