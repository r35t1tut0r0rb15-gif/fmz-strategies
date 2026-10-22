# #455364 Dynamic Optimized Supertrend Trading Strategy -> `fmz_455364_supertrend3_14_flip_reversal`

- FMZ source id: 455364 (lineage).
- Source: https://www.fmz.com/strategy/455364 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-28 15:23:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar bracket pending (mark) |
| 2 | PASS | Supertrend flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [14, 10] x `factor` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- The per-bar bracket pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`
