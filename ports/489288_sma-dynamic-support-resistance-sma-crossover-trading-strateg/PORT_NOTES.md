# #489288 动态支撑阻力SMA交叉黄金交易策略三重确认与风险管理优化框架-Dynamic-Support-Resistance-SMA-Crossover-Trading-Strategy-Triple-Confirmation-with-Risk-Management-Optimization-Framework -> `fmz_489288_sma10_20_cross_breakout_retest_reversal`

- FMZ source id: 489288 (lineage).
- Source: https://www.fmz.com/strategy/489288 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:51:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | SMA crossings with breakout and retest filters |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [20, 50]: **4 trials**; 3-bar windows.

## Ambiguities resolved

- The per-bar bracket is pending. REVERSAL INTENDED. FREQ = "1h". MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
