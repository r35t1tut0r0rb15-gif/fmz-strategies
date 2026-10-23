# #477531 Dynamic Trading Theory Exponential Moving Average and Cumulative Volume Period Crossover Strategy -> `fmz_477531_ema25_vs_ema_rolling_vwap100_cross_long_only`

- FMZ source id: 477531 (lineage).
- Source: https://www.fmz.com/strategy/477531 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 11:45:38). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA of price against the EMA of a rolling VWAP |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital, qty 1 and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [25, 50] x `cvp` [100, 50]: **4 trials**.

## Ambiguities resolved

- Default LONG direction only. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`none`
