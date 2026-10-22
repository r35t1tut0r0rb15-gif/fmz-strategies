# #458272 SMA-FVG-SMA交叉策略与公平价值缺口回调结合的综合交易系统Comprehensive-Trading-System-Combining-SMA-Crossover-Strategy-with-Fair-Value-Gap-Pullback -> `fmz_458272_sma8_20_cross_after_first_outside_bar_reversal`

- FMZ source id: 458272 (lineage).
- Source: https://www.fmz.com/strategy/458272 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:38:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [8, 5] x `long_len` [20, 50]: **4 trials**.

## Ambiguities resolved

- Prices used as truth values (as written): the gap levels never filter after the first outside bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
