# #477583 Mean Reversion Bollinger Bands Trading Strategy with Rational Return Signal -> `fmz_477583_bb20_break_distance_flag_reversal`

- FMZ source id: 477583 (lineage).
- Source: https://www.fmz.com/strategy/477583 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 15:33:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts gated by a distance flag |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `threshold` [0.035, 0.05]: **4 trials**; 2 sd.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
