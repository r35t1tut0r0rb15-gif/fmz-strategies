# #483790 Multi Dimensional Adaptive Trend Following and Risk Management Strategy -> `fmz_483790_sma_high_low_atr_band_cross_trend_utc02_14_cooldown_tick_bracket_reversal`

- FMZ source id: 483790 (lineage).
- Source: https://www.fmz.com/strategy/483790 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-26 09:54:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick bracket as fractions of the fill, break-even step as an exit signal |
| 2 | ADAPT | Tick amounts read as fractions at ETH 3000 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `cooldown_bars` [15, 30]: **4 trials**; ATR 14 x 1.2, EMA 50 / 200, ticks read at ETH 3000.

## Ambiguities resolved

- Hours in UTC. Tick amounts read at ETH 3000. The marketable break-even stop is ported as a next-open exit, as written.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
