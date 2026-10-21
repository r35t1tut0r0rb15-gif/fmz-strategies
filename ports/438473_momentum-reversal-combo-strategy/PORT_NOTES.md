# #438473 Momentum Reversal Combo Strategy -> `fmz_438473_reversal123_cmoav_combo`

- FMZ source id: 438473 (lineage).
- Source: https://www.fmz.com/strategy/438473 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 12:22:47). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and CMO bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `top_band` [70, 50]: **4 trials**; low band = -top band; K smoothing 1, D 3, level 50 and CMO 5 / 10 / 20 fixed.

## Ambiguities resolved

- 123 test as written; disagreement closes. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
