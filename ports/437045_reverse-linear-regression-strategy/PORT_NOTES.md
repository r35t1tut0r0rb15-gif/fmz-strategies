# #437045 Reverse Linear Regression Strategy -> `fmz_437045_counter_candle_linreg_slope`

- FMZ source id: 437045 (lineage).
- Source: https://www.fmz.com/strategy/437045 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 17:15:07). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colour and regression slope sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 2 and the percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slope_len` [14, 28] x `bars_run` [1, 2]: **4 trials**; the up and down run counts are swept together.

## Ambiguities resolved

- Pyramiding adds left out (sizing); call-order fills. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
