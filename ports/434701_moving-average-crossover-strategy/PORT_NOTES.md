# #434701 Moving Average Crossover Strategy -> `fmz_434701_sma20_sma60_close_cross_long`

- FMZ source id: 434701 (lineage).
- Source: https://www.fmz.com/strategy/434701 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-08 15:23:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exit follows the opening entry (tracked) |
| 2 | PASS | Price against averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [60, 120]: **4 trials**.

## Ambiguities resolved

- Exit tied to the opening entry id; start date dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
