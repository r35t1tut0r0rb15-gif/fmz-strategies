# #444007 EMA9 20Dual Moving Average Crossover Strategy EMA9 20 -> `fmz_444007_ema9_20_ohlc4_named_ids_reversal`

- FMZ source id: 444007 (lineage).
- Source: https://www.fmz.com/strategy/444007 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 15:22:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-id tick trail pending |
| 2 | PASS | EMA crossings under named ids (as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity and per-contract commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [20, 50]: **4 trials**; the trail settings fixed (pending).

## Ambiguities resolved

- The duplicated crossover test as written; per-id trail pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
