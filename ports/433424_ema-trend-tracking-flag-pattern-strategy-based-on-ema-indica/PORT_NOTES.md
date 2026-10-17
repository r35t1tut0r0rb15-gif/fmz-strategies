# #433424 基于EMA指标的旗形趋势追踪策略Trend-Tracking-Flag-Pattern-Strategy-Based-on-EMA-Indicators -> `fmz_433424_ewo_open_threshold`

- FMZ source id: 433424 (lineage).
- Source: https://www.fmz.com/strategy/433424 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-27 15:30:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit oscillator levels -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`th_atr` [0.002, 0.2] x `slow` [13, 34]: **4 trials**; fast EMA 5 and ATR 14 fixed.

## Ambiguities resolved

- Price-unit levels as ATR fractions (criterion 2 ADAPT). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
