# #438048 Dual Moving Average Crossover Strategy -> `fmz_438048_sma10_21_cross_long_stop`

- FMZ source id: 438048 (lineage).
- Source: https://www.fmz.com/strategy/438048 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 15:59:34). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Moving-average crossings and percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-as-ticks bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `stop` [0.01, 0.02]: **4 trials**; slow 21 and the 200 % target fixed.

## Ambiguities resolved

- Percent-as-ticks bracket as fixed fractions (the 200 % target never reached); long side only. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
