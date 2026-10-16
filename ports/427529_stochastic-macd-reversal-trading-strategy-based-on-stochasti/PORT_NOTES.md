# #427529 Reversal Trading Strategy Based on Stochastic and MACD Indicators -> `fmz_427529_combo_123_macd_stop`

- FMZ source id: 427529 (lineage).
- Source: https://www.fmz.com/strategy/427529 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 21:39:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed stop at entry; the profit-lock step pending. |
| 2 | PASS | Oscillator states, stops as fractions of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Leveraged quantity stored; stops quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `level` [1, 50] x `sl_pct` [10, 5]: **8 trials**; defaults 100 / 1 / 10 (the source's); K 1, D 2, MACD 10 / 19 / 24 fixed.

## Trailing / lock step (rule 2, mark `trailing_stop_pending`)

As written: `longStopPrice = max(avg x 0.90, high > avg x 1.10 ? avg x 1.05 : 0, longStopPrice[1])` (short mirrors), recomputed at each bar close (the fill bar included) and placed for the next bar. The fixed 10 % part is ported as `sl_stop`; the step to +5 % after a 10 % move cannot be expressed by the house trail (its lock-in moves the stop to the entry price only): not emitted. The extra stop lines (`longStopPrice2/3`, `lastStop*`) are never used by an order.

## Ambiguities resolved

- Entries on every bar of the combined state (re-entry after a stop-out, as Pine), close on disagreement.
- Leverage / equity quantity is sizing; the date window is dropped. Broker-day bars; mark `coarse_bar_stop`.
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
