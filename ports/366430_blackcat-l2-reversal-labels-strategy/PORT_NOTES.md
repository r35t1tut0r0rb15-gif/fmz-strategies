# #366430 [blackcat] L2 Reversal Labels Strategy -> `fmz_366430_macd_cross_divergence`

- Source: https://www.fmz.com/strategy/366430 (PineScript v5, author Zer3192, FMZ last
  modified 2022-05-29 11:35:50). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG366430` (Jaccard >= 0.80) with #434528 (DUPLICATE); best Jaccard 1.000 with #434528. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [21, 26] x `signal` [9, 12] = **8 trials**.

## Ambiguities resolved

- `barssince(cross[1])` points at the previous cross bar, so the comparison is cross-to-cross.
- Labels and alerts only draw.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks (2026-10-07)

`none`
