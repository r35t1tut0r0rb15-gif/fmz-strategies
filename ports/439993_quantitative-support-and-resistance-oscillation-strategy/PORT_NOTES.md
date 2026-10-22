# #439993 Quantitative Support and Resistance Oscillation Strategy -> `fmz_439993_sentenzal_stochrsi_ha_trend`

- FMZ source id: 439993 (lineage).
- Source: https://www.fmz.com/strategy/439993 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 15:53:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI, Heikin-Ashi turns, SMA trend and channel breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_lengh` [100, 200] x `oversold` [20, 30]: **4 trials**; overbought = 100 - oversold; the other lengths fixed.

## Ambiguities resolved

- Closes before entries. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
