# #363588 Fukuiz Octa-EMA + Ichimoku -> `fmz_363588_octa_ema_ichimoku`

- Source: https://www.fmz.com/strategy/363588 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-16 18:21:00). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Inactive sizing lines (commented-out strategy() etc.) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG363588` (Jaccard >= 0.80) with #434982 (REJECTED); best Jaccard 0.855 with #434982. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [8, 11] x `ema_slow` [34, 55] x `displacement` [26, 52] = **8 trials**. Tenkan 9, Kijun 26, span 52 stay at the originals.

## Ambiguities resolved

- The author's SenkouA/SenkouB names are swapped against the usual Ichimoku; kept as coded (both are past values).
- Six ribbon EMAs and the barssince buy/sell conditions only draw; the date window is dropped.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`none`
