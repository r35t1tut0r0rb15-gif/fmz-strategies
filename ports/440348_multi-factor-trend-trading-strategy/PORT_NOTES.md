# #440348 Multi factor Trend Trading Strategy -> `fmz_440348_sma_cross_fixed_breakout_levels`

- FMZ source id: 440348 (lineage).
- Source: https://www.fmz.com/strategy/440348 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 15:17:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Fixed price levels -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; level fractions 0.0381 / 0.0357 fixed.

## Ambiguities resolved

- Price levels as fractions (always long except cross-down bars); level-free exits. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
