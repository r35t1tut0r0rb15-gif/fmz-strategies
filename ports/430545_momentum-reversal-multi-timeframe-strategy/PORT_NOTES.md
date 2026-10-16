# #430545 Momentum Reversal Multi Timeframe Strategy -> `fmz_430545_combo_123_range_hist`

- FMZ source id: 430545 (lineage).
- Source: https://www.fmz.com/strategy/430545 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-30 10:42:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a range against its own average. |
| 3 | PASS | No exchange or market named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [13, 26] x `bars_back` [4, 1]: **4 trials**; the 123 settings fixed.

## Ambiguities resolved

- No bar size: bar_size_pending (driver supplies bar_size). Disagreement closes all. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`bar_size_pending`
