# #473134 Adaptive Trend Following Strategy Based on Momentum Oscillator -> `fmz_473134_cmo9_dip_timed_or_overbought_exit_long`

- FMZ source id: 473134 (lineage).
- Source: https://www.fmz.com/strategy/473134 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 15:03:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CMO dips with a timed exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG473134. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cmo_period` [9, 14] x `hold` [5, 10]: **4 trials**; the levels fixed.

## Ambiguities resolved

- Flag cleared by every exit test (as written). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
