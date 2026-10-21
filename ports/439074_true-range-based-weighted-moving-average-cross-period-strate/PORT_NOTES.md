# #439074 True Range Based Weighted Moving Average Cross Period Strategy -> `fmz_439074_true_range_wma_spread_turn_long`

- FMZ source id: 439074 (lineage).
- Source: https://www.fmz.com/strategy/439074 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 15:09:28). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested profit exit |
| 2 | PASS | True-range WMA spread turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The contract sizes and the add levels stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`corto` [10, 5] x `largo` [30, 60]: **4 trials**; smoothing 10 fixed.

## Ambiguities resolved

- Adds blocked (sizing); profit exit on closes. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
