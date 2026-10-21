# #438775 基于双EMA和AC指标的趋势跟踪策略Dual-EMA-and-AC-Indicator-Based-Trend-Following-Strategy -> `fmz_438775_ema2_20_accelerator_combo`

- FMZ source id: 438775 (lineage).
- Source: https://www.fmz.com/strategy/438775 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 12:02:54). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA band position and accelerator oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430896. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `slow` [33, 21]: **4 trials**; AC fast 6 fixed; reverse off.

## Ambiguities resolved

- Disagreement closes. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
