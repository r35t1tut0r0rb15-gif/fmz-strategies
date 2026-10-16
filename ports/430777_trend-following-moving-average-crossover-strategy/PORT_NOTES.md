# #430777 Trend Following Moving Average Crossover Strategy -> `fmz_430777_trend_catcher_emas`

- FMZ source id: 430777 (lineage).
- Source: https://www.fmz.com/strategy/430777 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-01 17:18:13). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at the fill (rule 2). |
| 2 | PASS | Moving averages and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | A fixed quantity of 1 stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_long` [0.03, 0.05] x `sl_short` [0.02, 0.04]: **4 trials**; the EMA lengths and the targets fixed.

## Ambiguities resolved

- Pending (not emitted as written): the bracket re-sized from each close; fixed at the fill here.
- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
