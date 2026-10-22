# #440454 基于Vix修复线性回归的低点捕捉策略Vix-Fix-Linear-Regression-Bottom-Fishing-Strategy -> `fmz_440454_vix_fix_linreg_bottoms_long`

- FMZ source id: 440454 (lineage).
- Source: https://www.fmz.com/strategy/440454 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 16:56:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested ratcheting line |
| 2 | PASS | Vix Fix, its regression and ATR line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent of equity, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [5, 3] x `pd` [22, 14]: **4 trials**; BB 20 / 2 and percentile 50 / 0.85 fixed.

## Ambiguities resolved

- Close-tested exit; flat-state latch as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_spike_reversal"`.

## Marks

`none`
