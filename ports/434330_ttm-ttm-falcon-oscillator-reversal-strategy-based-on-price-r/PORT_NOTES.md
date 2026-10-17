# #434330 基于价格反转的TTM银隼震荡策略TTM-Falcon-Oscillator-Reversal-Strategy-Based-on-Price-Reversion -> `fmz_434330_ttm_scalper_switch`

- FMZ source id: 434330 (lineage).
- Source: https://www.fmz.com/strategy/434330 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-05 15:07:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close-to-close patterns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True]: **2 trials**.

## Ambiguities resolved

- Switch starts short; trigger names as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
