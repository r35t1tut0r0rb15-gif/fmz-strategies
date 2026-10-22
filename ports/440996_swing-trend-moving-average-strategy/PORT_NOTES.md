# #440996 Swing Trend Moving Average Strategy -> `fmz_440996_ema200_atr_margin_trend_long`

- FMZ source id: 440996 (lineage).
- Source: https://www.fmz.com/strategy/440996 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 15:44:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA and ATR levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [200, 100] x `atr_mult` [1.0, 2.0]: **4 trials**; ATR 10 fixed.

## Ambiguities resolved

- Long only (shorts off by default). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
