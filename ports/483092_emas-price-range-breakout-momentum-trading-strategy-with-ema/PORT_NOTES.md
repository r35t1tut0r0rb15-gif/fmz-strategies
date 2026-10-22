# #483092 基于日内价格区间突破的动量交易策略结合EMAs指标优化-Price-Range-Breakout-Momentum-Trading-Strategy-with-EMAs-Optimization -> `fmz_483092_prev_day_high_low_break_ema9_21_tick_bracket_reversal`

- FMZ source id: 483092 (lineage).
- Source: https://www.fmz.com/strategy/483092 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:20:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | ADAPT | Tick bracket read as percents at the header's SOL prices |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [0.0015, 0.005] x `risk_reward` [2.0, 1.5]: **4 trials**; EMA 9 / 21.

## Ambiguities resolved

- The tick bracket is read at SOL prices (about 200). The previous day is the previous broker day.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
