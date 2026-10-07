# #365373 Super Scalper - 5 Min 15 Min -> `fmz_365373_super_scalper_rsi_pair`

- Source: https://www.fmz.com/strategy/365373 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-24 16:20:58). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365373` (Jaccard >= 0.80) with #442079 (DUPLICATE), #442083 (DUPLICATE), #442547 (DUPLICATE); best Jaccard 0.966 with #442079. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [7, 14, 28] x `mult` [0.5, 1.0, 1.5] = **9 trials**. RSI 25 / 100 stay at the originals.

## Ambiguities resolved

- stopLoss/takeProfit computed but never passed to an order; EMA crosses only draw.
- Variant of #363803 with an RSI-pair filter.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`none`
