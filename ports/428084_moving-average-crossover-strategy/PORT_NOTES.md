# #428084 Moving Average Crossover Strategy -> `fmz_428084_ema_20_120_cross`

- FMZ source id: 428084 (lineage).
- Source: https://www.fmz.com/strategy/428084 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-28 15:15:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.
- Duplicate group: **DG428084** (2 members, best partner #433446, Jaccard 1.000); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428084. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [20, 10] x `ma2` [120, 60]: **4 trials**; defaults 20 / 120 (the source's).

## Ambiguities resolved

- The chart-period security is the close itself. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
