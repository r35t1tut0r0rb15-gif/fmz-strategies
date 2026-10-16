# #430372 A Powerful System Combining Reversal and Trend Following Strategies -> `fmz_430372_combo_123_t3`

- FMZ source id: 430372 (lineage).
- Source: https://www.fmz.com/strategy/430372 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-27 16:22:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_t3` [5, 10] x `b` [0.7, 0.5]: **4 trials**; the 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
