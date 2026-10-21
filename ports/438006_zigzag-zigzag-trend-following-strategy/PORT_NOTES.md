# #438006 基于ZigZag指标的趋势追踪交易策略ZigZag-Trend-Following-Strategy -> `fmz_438006_zigtrend_turns`

- FMZ source id: 438006 (lineage).
- Source: https://www.fmz.com/strategy/438006 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-08 10:13:24). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed-EMA turns and 4-bar extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity lot, capital input and percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [4, 8] x `detection` [4, 8]: **4 trials**.

## Ambiguities resolved

- Signals only on turn bars; extremes include the current bar. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
