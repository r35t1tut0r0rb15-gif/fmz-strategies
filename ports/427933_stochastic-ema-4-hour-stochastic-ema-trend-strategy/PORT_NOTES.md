# #427933 4-Hour Stochastic EMA Trend Strategy -> `fmz_427933_triple_cross_long`

- FMZ source id: 427933 (lineage).
- Source: https://www.fmz.com/strategy/427933 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 20:57:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA and oscillator lengths only. |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period3` [50, 30] x `period_k` [13, 9]: **4 trials**; defaults 50 / 13 (the source's hard-coded values); EMAs 5 / 15, D 15, K smoothing 5 fixed.

## Ambiguities resolved

- Lengths are hard-coded in the source. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
