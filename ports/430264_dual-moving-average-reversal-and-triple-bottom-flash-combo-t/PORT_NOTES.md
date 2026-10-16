# #430264 Dual Moving Average Reversal and Triple Bottom Flash Combo Trading Strategy -> `fmz_430264_combo_ema20_three_day_pattern`

- FMZ source id: 430264 (lineage).
- Source: https://www.fmz.com/strategy/430264 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-26 16:26:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An EMA against two-bar extremes and a bar pattern. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20, 30]: **3 trials**.

## Ambiguities resolved

- The daily security with lookahead_on and [1] is the previous bar's pattern state. REVERSAL INTENDED. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
