# #440998 Quadratic Momentum Double Indicators Timing Strategy -> `fmz_440998_four_supertrend_agreement_flip_exit`

- FMZ source id: 440998 (lineage).
- Source: https://www.fmz.com/strategy/440998 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 15:53:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C144). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Four SuperTrend states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length1` [7, 14] x `multiplier1` [4.0, 3.0]: **4 trials**; the other three SuperTrends fixed.

## Ambiguities resolved

- SuperTrend as written (nz starts). Opposite entries cannot occur (entries only from flat). FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
