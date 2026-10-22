# #483047 多周期均线带及MACD交叉策略系统-Multi-Period-Moving-Average-Ribbon-and-MACD-Crossover-Strategy-System -> `fmz_483047_ema9_21_and_macd_cross_same_bar_daily_reset_long`

- FMZ source id: 483047 (lineage).
- Source: https://www.fmz.com/strategy/483047 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:51:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA and MACD up-crosses together |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_length` [9, 5] x `ma2_length` [21, 50]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- The day reset uses UTC dates (the header exchange's zone). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
