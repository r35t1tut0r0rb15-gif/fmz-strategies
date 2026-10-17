# #431667 三EMA趋势追踪策略Three-EMA-Trend-Following-Strategy -> `fmz_431667_three_rising_emas`

- FMZ source id: 431667 (lineage).
- Source: https://www.fmz.com/strategy/431667 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-10 11:45:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA slopes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`e1` [10, 5] x `e3` [30, 60]: **4 trials**; EMA 2 = 20 fixed.

## Ambiguities resolved

- Stop off (default). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
