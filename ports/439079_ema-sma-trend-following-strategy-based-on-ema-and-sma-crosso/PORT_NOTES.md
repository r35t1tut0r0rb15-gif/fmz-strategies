# #439079 基于EMA和SMA交叉的趋势跟踪策略Trend-Following-Strategy-Based-on-EMA-and-SMA-Crossover -> `fmz_439079_ema5_sma20_1h_4h_cross_held`

- FMZ source id: 439079 (lineage).
- Source: https://www.fmz.com/strategy/439079 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 15:42:22). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 4-hour values from completed bars |
| 2 | PASS | EMA / SMA crossings on two bar sizes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 9] x `slow` [20, 50]: **4 trials**; the same lengths on both bar sizes.

## Ambiguities resolved

- Completed 4-hour values; close of an unused id: one long held. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
