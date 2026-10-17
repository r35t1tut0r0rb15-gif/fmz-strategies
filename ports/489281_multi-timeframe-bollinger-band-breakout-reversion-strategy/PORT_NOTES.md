# #489281 多周期布林带突破回归交易策略-Multi-Timeframe-Bollinger-Band-Breakout-Reversion-Strategy -> `fmz_489281_bb_outside_candle_reversal_3r`

- FMZ source id: 489281 (lineage).
- Source: https://www.fmz.com/strategy/489281 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:26:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a close-checked target; the break-even stop pending (mark). |
| 2 | PASS | Band positions and candle ranges. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed-loss (INR 4000) quantity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.5, 2.0] x `rr` [3.0, 2.0]: **4 trials**; defaults 1.5 / 3 (the source's); BB 20 and the 2 R break-even
fixed.

## Break-even stop (rule 2, mark `trailing_stop_pending`)

Once a close reaches 2 R in profit (R = the outside candle's high - low), `strategy.exit(stop = entry level)` places a
stop at the signal's reference price (low[1] for a short, high[1] for a long). The trigger is a per-trade multiple of
the candle range, which the house `lock_in` (a fixed gain) cannot express: not emitted. There is no initial stop.

## Ambiguities resolved

- The 3 R target is checked on closes: a close-based exit (rule 3). Shared level variables are overwritten by each
  signal, as written.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
