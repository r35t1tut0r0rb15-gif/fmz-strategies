# #434345 自适应ATR-ADX趋势策略V2An-Adaptive-ATR-ADX-Trend-Strategy-V2 -> `fmz_434345_adaptive_atr_adx_trend`

- FMZ source id: 434345 (lineage).
- Source: https://www.fmz.com/strategy/434345 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-05 18:08:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR lines with an ADX-switched multiplier |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`m1` [3.5, 2.5] x `adx_thresh` [30, 20]: **4 trials**; m2 1.75, ATR 21, ADX 14 fixed.

## Ambiguities resolved

- Author's running DI sums; m held when the ADX is flat. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
