# #482836 基于动态ATR和双均线交叉的自适应风险管理策略-Adaptive-Risk-Management-Strategy-Based-on-Dynamic-ATR-and-Moving-Average-Crossover -> `fmz_482836_sma10_100_cross_cooldown10_atr1_5_rr2_bracket_reversal`

- FMZ source id: 482836 (lineage).
- Source: https://www.fmz.com/strategy/482836 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:07:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | SMA crossings with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (riskPercent unused). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_period` [10, 20] x `long_period` [100, 50]: **4 trials**; ATR 14 x 1.5, RR 2, cooldown 10, window 00:00-23:59 UTC.

## Ambiguities resolved

- The UTC window is kept; at the defaults it covers every 2-hour bar. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
