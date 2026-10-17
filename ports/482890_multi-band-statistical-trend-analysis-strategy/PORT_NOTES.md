# #482890 多波段统计趋势分析策略-Multi-Band-Statistical-Trend-Analysis-Strategy -> `fmz_482890_quantile_band_trigger_long`

- FMZ source id: 482890 (lineage).
- Source: https://www.fmz.com/strategy/482890 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 16:45:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rolling quantile and standard deviation of closes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `confirm_bars` [1, 3]: **4 trials**; defaults 20 / 1 (the source's); upper quantile 0.95 fixed
(entry and exit confirmations share the value, 1 / 1 in the source).

## Ambiguities resolved

- The quantile is the source's `f_percentile` (sorted window incl. the current close, index round((n - 1) q)).
- With one-bar confirmations the position is long exactly while the trigger holds. The other bands only colour plots.
- Long only: opposite entries cannot occur. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
