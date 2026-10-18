# #436137 Mean Reversion Reverse Strategy Based on Moving Average -> `fmz_436137_ema_layer_dip_long_profit_exit`

- FMZ source id: 436137 (lineage).
- Source: https://www.fmz.com/strategy/436137 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 15:45:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | EMA layers and candle rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity inputs and the pyramiding multiplier stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG436137. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`profit_pct` [1.0, 2.0, 0.5]: **3 trials**; the EMA lengths and the layers fixed.

## Ambiguities resolved

- Single position; quantity-only entry ids; exit gated by the average price. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
