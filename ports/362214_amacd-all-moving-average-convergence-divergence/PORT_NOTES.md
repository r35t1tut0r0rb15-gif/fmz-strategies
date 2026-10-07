# #362214 AMACD-All-Moving-Average-Convergence-Divergence -> `fmz_362214_amacd_deal_state`

- Source: https://www.fmz.com/strategy/362214 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-10 16:13:20). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MACD histogram zero crosses. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [26, 34] x `signal` [9, 12] = **8 trials**. MA types at the defaults (EMA / SMA / SMA).

## Ambiguities resolved

- **As written, one-sided**: the deal state turns every opposite cross into a close, so only the side of the first cross is ever traded. Flagged in the worker report.
- Only the default MA types and the crossover signal set are ported (18 MA types and 4 optional signal sets are inputs).
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
