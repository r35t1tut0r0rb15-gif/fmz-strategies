# #439106 8周期和21周期的移动平均线策略Dual-Moving-Average-Strategy -> `fmz_439106_sma8_21_cross_angle`

- FMZ source id: 439106 (lineage).
- Source: https://www.fmz.com/strategy/439106 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 17:45:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA crossings and an ATR-normalised slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`angle` [7, 3] x `lookback` [15, 5]: **4 trials**; SMA 8 / 21, angle period 2 and ATR 10 fixed.

## Ambiguities resolved

- Look-back excludes the current bar. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
