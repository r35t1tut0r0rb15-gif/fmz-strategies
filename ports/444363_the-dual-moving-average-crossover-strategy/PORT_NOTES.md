# #444363 The Dual Moving Average Crossover Strategy -> `fmz_444363_sma14_28_cross_reversal`

- FMZ source id: 444363 (lineage).
- Source: https://www.fmz.com/strategy/444363 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-11 12:06:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG444363. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 10] x `slow` [28, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
