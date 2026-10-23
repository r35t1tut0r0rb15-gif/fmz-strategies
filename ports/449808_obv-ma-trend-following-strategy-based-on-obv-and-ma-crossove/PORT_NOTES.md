# #449808 基于OBV与MA交叉信号的趋势跟踪策略-Trend-Following-Strategy-Based-on-OBV-and-MA-Crossover-Signals -> `fmz_449808_obv_sma190_202_cross_long_only`

- FMZ source id: 449808 (lineage).
- Source: https://www.fmz.com/strategy/449808 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 13:48:58). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | OBV crossings of long SMAs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, margin 0.1, commission 0.1 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_len` [190, 100] x `exit_len` [202, 100]: **4 trials**.

## Ambiguities resolved

- OBV counts flat closes as up. Volume = broker tick volume (OBV). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "obv"`.

## Marks

`none`
