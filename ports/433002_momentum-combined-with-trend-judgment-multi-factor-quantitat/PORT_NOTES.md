# #433002 Momentum Combined with Trend Judgment Multi factor Quantitative Trading Strategy -> `fmz_433002_confluence_state`

- FMZ source id: 433002 (lineage).
- Source: https://www.fmz.com/strategy/433002 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-23 14:58:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Score ladders of moving-average differences (the sin / cos terms are scale-bound, as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND433002. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`harmonic` [10, 5, 20]: **3 trials**; the bands +/- 9 fixed (they never bind).

## Ambiguities resolved

- Transcribed as written (pi as 3.14, degrees of a price). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
