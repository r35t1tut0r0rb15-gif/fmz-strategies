# #436877 Moving Average Rebound Strategy -> `fmz_436877_new_support_buy_resistance_exit`

- FMZ source id: 436877 (lineage).
- Source: https://www.fmz.com/strategy/436877 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-28 15:25:29). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rolling extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 10 and margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_rs` [13, 21]: **2 trials**.

## Ambiguities resolved

- Pyramiding adds left out (sizing); the 0.95 x close stop can never fire. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
