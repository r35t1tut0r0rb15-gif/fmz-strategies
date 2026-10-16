# #430020 Dual Moving Average Turning Point Strategy -> `fmz_430020_hma_turning_point`

- FMZ source id: 430020 (lineage).
- Source: https://www.fmz.com/strategy/430020 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-24 12:19:04). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A percentage rate of change of a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430020. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [25, 15, 40] x `strength` [2.5, 5.0]: **6 trials**; lookback 1 fixed.

## Ambiguities resolved

- The slope threshold is 0.025 % of the HMA per bar (0.01 x the input, against a percent ROC), as written.
- Default HMA only. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
