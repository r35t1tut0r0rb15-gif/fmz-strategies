# #483082 基于动态波动率调整的双均线交叉与RSI-ATR复合过滤交易系统-Dynamic-Volatility-Adjusted-Dual-Moving-Average-Crossover-System-with-RSI-ATR-Composite-Filter -> `fmz_483082_sma9_21_cross_rsi_atr_floor_0_5pct_rr2_bracket_reversal`

- FMZ source id: 483082 (lineage).
- Source: https://www.fmz.com/strategy/483082 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:58:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | ADAPT | The ATR floor read as a fraction of the close at the header's prices |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity and 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_perc` [0.5, 1.0] x `risk_reward_ratio` [2.0, 3.0]: **4 trials**; SMA 9 / 21, RSI 14 / 70 / 30, ATR 14 over 2.5e-05 x close.

## Ambiguities resolved

- The ATR floor is read at SOL prices. The bracket is ported from the fill, active from the fill bar.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
