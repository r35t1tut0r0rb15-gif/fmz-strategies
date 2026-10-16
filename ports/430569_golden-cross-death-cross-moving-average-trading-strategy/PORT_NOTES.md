# #430569 Golden Cross Death Cross Moving Average Trading Strategy -> `fmz_430569_sma64_close_cross_trend`

- FMZ source id: 430569 (lineage).
- Source: https://www.fmz.com/strategy/430569 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-30 14:42:09). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the shared-id exit read as written, the moving levels fixed at the fill. |
| 2 | PASS | Moving averages and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exit percentages quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_length` [64, 32] x `trend_length` [200, 100]: **4 trials**; short-side 1 % / 3 % fixed.

## Ambiguities resolved

- Pending (as written, not emitted for longs): the shared exit id leaves longs without a bracket; the short bracket
  moves with each close and is fixed at the fill here.
- Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
