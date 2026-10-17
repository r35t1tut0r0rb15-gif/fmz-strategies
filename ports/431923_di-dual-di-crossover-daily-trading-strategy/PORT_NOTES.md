# #431923 基于DI交叉的日内交易策略Dual-DI-Crossover-Daily-Trading-Strategy -> `fmz_431923_di_cross_atr_bracket`

- FMZ source id: 431923 (lineage).
- Source: https://www.fmz.com/strategy/431923 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 11:32:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (rule 2) |
| 2 | PASS | DI crosses and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `atr_mult` [1.0, 2.0]: **4 trials**; target = 2 x the stop distance.

## Ambiguities resolved

- Pending (not emitted as written): the bracket re-sized by the current ATR; fixed at the signal bar here.
  Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
