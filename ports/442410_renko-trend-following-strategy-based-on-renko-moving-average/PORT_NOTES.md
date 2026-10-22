# #442410 基于Renko平均线的趋势追踪策略Trend-Following-Strategy-Based-on-Renko-Moving-Average -> `fmz_442410_hl2_ema22_cross_atr_bracket`

- FMZ source id: 442410 (lineage).
- Source: https://www.fmz.com/strategy/442410 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-21 16:36:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [22, 50] x `tp_atr` [0.2, 1.0]: **4 trials**; the stop multiple and the hours fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples; offset-free trail places nothing. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
