# #438826 ADX动态平均趋势指标策略ADX-Dynamic-Trend-Strategy -> `fmz_438826_adx_slope_dmi_ema200`

- FMZ source id: 438826 (lineage).
- Source: https://www.fmz.com/strategy/438826 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 15:32:45). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX slope and DI lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438826. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key_level` [23, 30] x `ma_length` [200, 100]: **4 trials**; ADX / DI 14 and slope 3 fixed.

## Ambiguities resolved

- Date window always true. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
