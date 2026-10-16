# #428060 Rate of Change Trading Strategy -> `fmz_428060_roc_dip_buyer_armed_trail`

- FMZ source id: 428060 (lineage).
- Source: https://www.fmz.com/strategy/428060 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 11:26:44). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.
- Near-duplicate group: **ND428060** (2 members, best partner #435831, Jaccard 0.785); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trailing exit approximated (mark). |
| 2 | PASS | MA lengths and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Order stake stored; trailing exit quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND428060. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [3.62, 2] x `lookback` [12, 6]: **4 trials**; defaults 3.62 / 12 (the source's); SMAs 14 / 100 / 30 and ROC thresholds fixed.

## Trailing stop (mark `trailing_stop_pending`)

The only exit is `strategy.exit(stop = longStopPrice)` issued on "sell setup" bars in profit, at a close-ratchet level (max of close x (1 - 3.62 %)). The house spec cannot express a condition-armed resting stop. **Stated approximation:** a bar whose low reaches the armed level gives an exit signal filled at the next open (Pine fills at the level intrabar). The level refreshes on each later setup bar.

## Ambiguities resolved

- Entry price = the fill (next open); a touch plus a new entry on one bar keeps the position (stated).
- Order stake is sizing. Long only. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`trailing_stop_pending`
