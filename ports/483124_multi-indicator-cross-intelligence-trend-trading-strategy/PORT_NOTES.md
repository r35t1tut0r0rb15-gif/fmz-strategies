# #483124 Multi Indicator Cross Intelligence Trend Trading Strategy -> `fmz_483124_ema9_21_cross_rsi_macd_1_2pct_bracket_reversal`

- FMZ source id: 483124 (lineage).
- Source: https://www.fmz.com/strategy/483124 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:54:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | EMA crossings with RSI and MACD filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_perc` [1.0, 2.0] x `take_profit_perc` [2.0, 4.0]: **4 trials**; EMA 9 / 21, RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- The bracket is ported from the fill, active from the fill bar. MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
