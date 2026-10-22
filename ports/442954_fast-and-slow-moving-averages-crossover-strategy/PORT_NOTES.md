# #442954 Fast and Slow Moving Averages Crossover Strategy -> `fmz_442954_ema25_62_momentum_long`

- FMZ source id: 442954 (lineage).
- Source: https://www.fmz.com/strategy/442954 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 16:06:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA order changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_bars` [25, 10] x `slow_bars` [62, 100]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
