# #431956 FX Strategy Based on Fractal Waves and SMMA -> `fmz_431956_fractal_smma_atr_stop`

- FMZ source id: 431956 (lineage).
- Source: https://www.fmz.com/strategy/431956 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 16:39:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (rule 2) |
| 2 | PASS | Fractals, an SMMA and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smma_len` [30, 60] x `stop_coef` [2.7, 1.5]: **4 trials**; ATR 10 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the stop re-issued at the latest close; fixed at the signal bar here.
  Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
