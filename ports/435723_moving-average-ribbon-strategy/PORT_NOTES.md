# #435723 Moving Average Ribbon Strategy -> `fmz_435723_ma_ribbon_counts`

- FMZ source id: 435723 (lineage).
- Source: https://www.fmz.com/strategy/435723 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 12:29:19). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average ribbon counts |
| 3 | PASS |  |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`matype` ["trima", "ema"] x `most` [8, 7]: **4 trials**; the ten lengths, the 6-of-10 exit and the confirmation of 3 bars fixed.

## Ambiguities resolved

- Confirmation tests on bars 1 to 3; orders in call order. REVERSAL INTENDED. FREQ = "bar_size_pending" (no bar size in the source).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending`
