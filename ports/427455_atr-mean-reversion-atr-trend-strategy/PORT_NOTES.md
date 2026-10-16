# #427455 Mean Reversion ATR Trend Strategy -> `fmz_427455_kl_atr_mean_reversion_long`

- FMZ source id: 427455 (lineage).
- Source: https://www.fmz.com/strategy/427455 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 11:42:06). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trailing line is tested on completed bars (exit signal). |
| 2 | PASS | ATR multiples, log returns. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tsl_mult` [2, 3] x `len_volat` [20, 40] x `len_drift` [20, 40]: **8 trials**; defaults 2 / 20 / 20 (the source's); TSL ATR 14 fixed.

## Ambiguities resolved

- The "trailing stop" is `strategy.close` when the completed bar's low touches the ratchet: a close-based exit signal (rule 2), no stop and no mark (the line ratchets on lows, not on the best price).
- The fill bar's own line starts the ratchet (Pine updates it at that bar's close, after the fill).
- Broker-day bars; the time inputs are the author's window. Long only. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
