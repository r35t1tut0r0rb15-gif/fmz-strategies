# #427186 JMA Crossing RSI Trading Strategy -> `fmz_427186_rsi_jma_cross_long`

- FMZ source id: 427186 (lineage).
- Source: https://www.fmz.com/strategy/427186 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-18 21:42:50). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry. |
| 2 | PASS | Oscillator crosses; stop as a fraction of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash qty 5000 stored; the stop is ported via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 9] x `jma_length` [7, 14] x `stop_factor` [1.08, 1.04]: **8 trials**; defaults 14 / 7 / 1.08 (the source's); phase 50, power 2 fixed.

## Ambiguities resolved

- `long_price` / `short_price` are reset to 0.0 every bar (not `var`): the long close never waits for a profit, and the short entry (`close < short_price` = its own close) can never fire. Ported as the script behaves: long only.
- The stop `avg / 1.08` = `sl_stop` 1 - 1/1.08 (7.4 %) of the fill.
- Broker-day bars; the date-window inputs are the author's backtest window.
- Daily bars with a stop: mark `coarse_bar_stop`. FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
