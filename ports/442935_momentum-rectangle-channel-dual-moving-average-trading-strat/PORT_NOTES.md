# #442935 Momentum Rectangle Channel Dual Moving Average Trading Strategy -> `fmz_442935_close_vs_tema5_reversal`

- FMZ source id: 442935 (lineage).
- Source: https://www.fmz.com/strategy/442935 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-27 14:54:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs TEMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_period` [5, 10]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
