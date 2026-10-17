# #483505 多周期动量驱动型自适应波动率过滤策略-Multi-Period-Momentum-Driven-Adaptive-Volatility-Filtered-Strategy -> `fmz_483505_composite_momentum_vol_filter_long`

- FMZ source id: 483505 (lineage).
- Source: https://www.fmz.com/strategy/483505 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 09:38:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed bracket from the fill. |
| 2 | PASS | Momentum ratios, return volatility and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_threshold` [0.5, 1.0] x `tp_pct` [15.0, 8.0]: **4 trials**; defaults 0.5 / 15 (the source's); momentum periods
63 / 126 / 189 / 252 bars, the 252-bar volatility, the 0 momentum threshold and the 5 % stop fixed.

## Ambiguities resolved

- The periods are bars on the 1-hour chart (named months in the source), as written; the composite averages the
  momenta that exist during the warm-up. `ta.stdev` is the population standard deviation.
- The bracket uses `strategy.position_avg_price` on every bar while held: fixed from the fill.
- Long only: opposite entries cannot occur. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum"`.

## Marks

`none`
