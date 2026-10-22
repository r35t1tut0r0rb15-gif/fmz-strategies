# #451723 Laguerre-RSI与ADX滤波交易信号策略-Laguerre-RSI-with-ADX-Filtered-Trading-Signals-Strategy -> `fmz_451723_laguerre_rsi_cross_adx_filter_reversal`

- FMZ source id: 451723 (lineage).
- Source: https://www.fmz.com/strategy/451723 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 15:01:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Laguerre RSI crossings with an ADX filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`alpha` [0.2, 0.5] x `adx_level` [20, 25]: **4 trials**; the levels 20 / 80 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
