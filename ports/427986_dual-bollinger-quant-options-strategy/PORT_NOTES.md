# #427986 Dual Bollinger Quant Options Strategy -> `fmz_427986_outer_bollinger_rsi_extreme`

- FMZ source id: 427986 (lineage).
- Source: https://www.fmz.com/strategy/427986 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-27 16:19:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Standard deviations and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length2` [20, 40] x `mult2` [3, 2.5]: **4 trials**; defaults 20 / 3 (the source's); RSI 14 (20 / 80) fixed.

## Ambiguities resolved

- Meant for binary options; as a strategy() each position is held to the opposite entry (ported). The 2-stdev band is drawn only.
- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
