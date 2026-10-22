# #477949 Multi Period Phase Crossover with EMA Trend Following Strategy -> `fmz_477949_sma20_ema20_offset_cross_long`

- FMZ source id: 477949 (lineage).
- Source: https://www.fmz.com/strategy/477949 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:17:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA / EMA crossings with a small offset |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `offset_frac` [1.19e-05, 0.0]: **4 trials**.

## Ambiguities resolved

- The 0.5 offset is a price amount (fraction of 42000). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
