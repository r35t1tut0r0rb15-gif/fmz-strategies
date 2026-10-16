# #427438 Mean Reversal Breakout Strategy -> `fmz_427438_buy_the_dip_atr`

- FMZ source id: 427438 (lineage).
- Source: https://www.fmz.com/strategy/427438 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-21 10:35:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a bar-count exit signal. |
| 2 | PASS | ATR multiple. |
| 3 | PASS | No exchange header at all. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dipness` [2, 1] x `smoothness` [10, 20] x `lookforward` [20, 10]: **8 trials**; defaults 2 / 10 / 20 (the source's); ATR 20 fixed. The bar size is the driver's (`bar_size_pending`), searched per the run spec.

## Ambiguities resolved

- No backtest header: `FREQ = "bar_size_pending"` (rule 1) and `precompute` builds the bars from `params["bar_size"]` with the house `bar_sizes.build_bars` (FMZ-C rule C3, skill section 5a).
- The 20-bar exit counts from the signal bar (`buyCondition[20]`), as written. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`bar_size_pending`
