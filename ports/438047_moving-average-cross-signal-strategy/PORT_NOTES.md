# #438047 Moving Average Cross Signal Strategy -> `fmz_438047_ma20_slope_cross`

- FMZ source id: 438047 (lineage).
- Source: https://www.fmz.com/strategy/438047 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-08 15:54:32). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average slope crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427510. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atype` [1, 2] x `len` [20, 50]: **4 trials**; smoothing 2 fixed.

## Ambiguities resolved

- Chart-resolution security; MA type swept over SMA / EMA. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
