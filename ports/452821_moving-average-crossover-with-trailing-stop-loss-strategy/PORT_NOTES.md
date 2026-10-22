# #452821 Moving Average Crossover with Trailing Stop Loss Strategy -> `fmz_452821_sma10_30_cross_up_price_unit_target_long`

- FMZ source id: 452821 (lineage).
- Source: https://www.fmz.com/strategy/452821 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 17:02:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the price-unit target as a fraction of 42000; re-issued target pending (mark) |
| 2 | PASS | SMA cross-ups with a fixed target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [30, 50] x `tp_frac` [0.000143, 0.01]: **8 trials**.

## Ambiguities resolved

- Price-unit target as a fraction of 42000; re-issued target pending. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
