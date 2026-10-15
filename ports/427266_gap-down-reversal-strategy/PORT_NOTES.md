# #427266 Gap Down Reversal Strategy -> `fmz_427266_gap_down_reversal_trail`

- FMZ source id: 427266 (lineage).
- Source: https://www.fmz.com/strategy/427266 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 16:19:51). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; trailing stop = the house trail. |
| 2 | PASS | Candle rule, percent trail. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash qty stored; the trail via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [5, 2, 10]: **3 trials**; default 5 (the source's).

## Trailing stop (FMZ-C rule 1, mark `trailing_stop`)

As written: `longStopPrice = max(close x 0.95, longStopPrice[1])` while long, placed as `strategy.exit(stop = ...)` for the next bar. On the source's 1-minute bars that is the house trail `{"type": "percent", "pct": 0.05, "anchor": "close"}`: the best minute close up to the previous minute x (1 - pct), never retreating. Ported natively; under the 2026-10-07 rules this would have been `trailing_stop_pending`. Promotion of a trailing trial still needs the cTrader trade-by-trade check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- Entries only from flat (pyramiding 1): long only.
- The 2009 start date is the author's backtest window: dropped.
- FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop`
