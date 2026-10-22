# #458043 Adaptive Moving Average Crossover with Trailing Stop Loss Strategy -> `fmz_458043_sma5_50_cross_up_ratchet_stop_pending_long`

- FMZ source id: 458043 (lineage).
- Source: https://www.fmz.com/strategy/458043 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:27:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ratcheting stdev stop pending (mark) |
| 2 | PASS | SMA cross-ups |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The balance-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 10] x `slow` [50, 100]: **4 trials**; the 2-stdev ratchet (pending) fixed.

## Ambiguities resolved

- Ratcheting stdev stop pending; no exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
