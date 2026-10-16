# #427674 Welles Wilder's Trend Balance Point System -> `fmz_427674_wilder_trend_balance_point`

- FMZ source id: 427674 (lineage).
- Source: https://www.fmz.com/strategy/427674 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-23 15:30:58). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | Tick-scaled distances -> percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored; bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mom_per` [2, 4] x `bracket_pct` [10, 2]: **4 trials**; defaults 2 / 10 (10 % is the source's distance on BTC_USDT with a 0.1 tick).

## Ambiguities resolved

- `strategy.exit(profit = longTP, loss = longStop)` passes PRICES as tick counts: the distances are about tick size x price. Ported as written as a symmetric percent bracket.
- Entries are the raw triggers (Pine enters when not on that side; a trigger after a stop-out re-enters).
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "5min".

## Decision owed

Intended version: stop at hlc3[1] - range[1] and limit at 2 hlc3[1] - low[1] (the Wilder levels) as price levels.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
