# #436220 Double Exponential Moving Average and ALMA Strategy -> `fmz_436220_ema_vs_alma`

- FMZ source id: 436220 (lineage).
- Source: https://www.fmz.com/strategy/436220 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-22 12:44:55). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average against an adaptive average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`windowsize` [50, 30] x `l2` [10, 5]: **4 trials**; offset 0.85 and sigma 6 fixed.

## Ambiguities resolved

- e1 is truthy; the rule is EMA 10 against ALMA. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
