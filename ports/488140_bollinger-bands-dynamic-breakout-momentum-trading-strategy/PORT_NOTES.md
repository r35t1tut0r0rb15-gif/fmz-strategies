# #488140 Bollinger Bands Dynamic Breakout Momentum Trading Strategy -> `fmz_488140_bb20_19_upper_breakout_stall4_basis_exit_long`

- FMZ source id: 488140 (lineage).
- Source: https://www.fmz.com/strategy/488140 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 14:10:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts with a stall-count and basis exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.9, 2.5] x `tolerance` [4, 2]: **4 trials**; BB 20.

## Ambiguities resolved

- The stall counter is followed in a loop as written. Long only. FREQ = "1D" (broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
