# #477552 Multi Indicator Dynamic Moving Average Crossover Quantitative Strategy -> `fmz_477552_sma50_200_golden_cross_long`

- FMZ source id: 477552 (lineage).
- Source: https://www.fmz.com/strategy/477552 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:46:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA golden / death crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; the other MA types and modes not swept.

## Ambiguities resolved

- Defaults ported (SMA, crossing in and out, no shorts). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
