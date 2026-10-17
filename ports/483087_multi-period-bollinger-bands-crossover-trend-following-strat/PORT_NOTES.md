# #483087 多周期布林带交叉趋势跟踪策略-Multi-Period-Bollinger-Bands-Crossover-Trend-Following-Strategy -> `fmz_483087_triple_bollinger_extremes_long`

- FMZ source id: 483087 (lineage).
- Source: https://www.fmz.com/strategy/483087 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:02:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 1.5] x `len1` [20, 50]: **4 trials**; defaults 2 / 20 (the source's); BB 120 / 240 fixed; one
multiplier for all three bands (each 2 in the source).

## Ambiguities resolved

- `ta.stdev` is the population standard deviation. Every bar in the condition is an entry signal.
- Long only: opposite entries cannot occur. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
