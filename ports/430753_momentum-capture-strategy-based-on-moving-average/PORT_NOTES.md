# #430753 Momentum Capture Strategy Based on Moving Average -> `fmz_430753_heikin_kaufman_cross`

- FMZ source id: 430753 (lineage).
- Source: https://www.fmz.com/strategy/430753 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-01 15:55:51). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Heikin Ashi values and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sloma` [20, 50] x `length` [5, 10]: **4 trials**; fast 2.5 and slow 20 fixed.

## Ambiguities resolved

- Same-timeframe HA securities = the chart's HA bars. Non-recursive Kaufman as written. REVERSAL INTENDED. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
