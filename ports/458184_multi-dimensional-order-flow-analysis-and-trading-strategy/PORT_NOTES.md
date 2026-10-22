# #458184 Multi Dimensional Order Flow Analysis and Trading Strategy -> `fmz_458184_order_block_sweep_close_compare_reversal`

- FMZ source id: 458184 (lineage).
- Source: https://www.fmz.com/strategy/458184 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 16:32:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range sweeps with a close comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [5, 10] x `threshold` [1.0, 1.01]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
