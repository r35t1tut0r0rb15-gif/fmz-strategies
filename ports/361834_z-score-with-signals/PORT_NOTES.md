# #361834 Z-Score-with-Signals -> `fmz_361834_hl_zscore_reversion`

- Source: https://www.fmz.com/strategy/361834 (PineScript v5, author ChaoZhang (Steversteves indicator), FMZ last
  modified 2022-05-08 16:33:16). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Z-scores are dimensionless. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [250, 500, 1000] x `threshold` [2, 2.5, 3] = **9 trials**.

## Ambiguities resolved

- Hard-coded 500 / 2.5 in the source become declared parameters with those defaults.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks (2026-10-07)

`none`
