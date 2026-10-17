# #482887 Bollinger-Bands与RSI结合的动量反转量化交易策略-Momentum-Reversal-Quantitative-Trading-Strategy-Combining-Bollinger-Bands-and-RSI -> `fmz_482887_bollinger_rsi_reentry_mid_exit`

- FMZ source id: 482887 (lineage).
- Source: https://www.fmz.com/strategy/482887 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:38:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands and RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 2.5] x `rsi_os` [30, 35]: **4 trials**; defaults 2 / 30 (the source's; the short side uses 100 minus it,
70); BB 20 and RSI 14 fixed.

## Ambiguities resolved

- The middle-band closes act on the position held at the bar's start (as #430850). Target-position state machine.
- REVERSAL INTENDED. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
