# #439351 Cross Trend Reversal Combined with Three Ten Oscillator Dual Strategies -> `fmz_439351_reversal123_daily_three_ten_combo`

- FMZ source id: 439351 (lineage).
- Source: https://www.fmz.com/strategy/439351 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 14:41:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C120). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed days |
| 2 | PASS | Close pattern, stochastic and an oscillator of daily hl2 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length3` [16, 8]: **4 trials**; the 3-10 EMAs and the 123 smoothing fixed.

## Ambiguities resolved

- Daily hl2 from the last completed broker day. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
