# #436479 Dual MA Crossover Strategy -> `fmz_436479_ohlc4_ema_dema_cross`

- FMZ source id: 436479 (lineage).
- Source: https://www.fmz.com/strategy/436479 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-25 11:06:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed order size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dema_len` [34, 21] x `ema_len` [8, 5]: **4 trials**.

## Ambiguities resolved

- Only the DEMA 34 trades; explicit closes equal the reversal. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
