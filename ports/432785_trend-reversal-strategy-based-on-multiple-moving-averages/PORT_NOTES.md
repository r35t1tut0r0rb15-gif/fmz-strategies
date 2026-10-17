# #432785 Trend Reversal Strategy Based on Multiple Moving Averages -> `fmz_432785_trend_detection_index_long`

- FMZ source id: 432785 (lineage).
- Source: https://www.fmz.com/strategy/432785 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 14:53:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum sums (both sides in price units, compared with each other) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity / ATR position size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40]: **3 trials**.

## Ambiguities resolved

- TDI only (the default). Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
