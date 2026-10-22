# #458047 多周期Hull移动平均线交叉策略-Multi-Timeframe-Hull-Moving-Average-Crossover-Strategy -> `fmz_458047_hull20_25m_75m_cross_reversal`

- FMZ source id: 458047 (lineage).
- Source: https://www.fmz.com/strategy/458047 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:44:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the odd-minute values from completed bars |
| 2 | PASS | Hull MA crossings across time frames |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10]: **2 trials**; the 25 / 75-minute time frames fixed.

## Ambiguities resolved

- Day-anchored 25 / 75-minute bars, last completed at the chart close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
