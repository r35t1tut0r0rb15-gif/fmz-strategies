# #365419 Bollinger Awesome Alert R1.1 by JustUncleL -> `fmz_365419_bb_basis_cross_ao`

- Source: https://www.fmz.com/strategy/365419 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 18:31:33). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 34] x `fast_ma` [3, 5] = **4 trials**. AO 5 / 34 stays at the original.

## Ambiguities resolved

- AO state |1| = rising, |2| = not rising (falling or flat), as coded.
- Bollinger and squeeze filters default off; bands only draw.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
