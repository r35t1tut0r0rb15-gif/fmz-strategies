# #434706 Crypto Bull Run Tracking Strategy -> `fmz_434706_tema_dema_cross`

- FMZ source id: 434706 (lineage).
- Source: https://www.fmz.com/strategy/434706 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-08 15:45:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dema_len` [230, 100] x `tema_len` [210, 90]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
