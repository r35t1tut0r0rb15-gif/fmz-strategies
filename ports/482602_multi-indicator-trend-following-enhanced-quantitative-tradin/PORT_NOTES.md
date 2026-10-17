# #482602 多重指标趋势跟踪增强型量化交易策略-Multi-Indicator-Trend-Following-Enhanced-Quantitative-Trading-Strategy -> `fmz_482602_ema50_200_cross_adx_rsi_pct_bracket_4h`

- FMZ source id: 482602 (lineage).
- Source: https://www.fmz.com/strategy/482602 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 11:30:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | EMAs, ADX, RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [5, 3] x `sl_pct` [2, 3]: **4 trials**; defaults 5 / 2 (the source's); EMA 50 / 200, ADX 14 > 25 and
RSI 14 (70 / 30) fixed.

## Ambiguities resolved

- The 240-minute EMAs are the chart's own timeframe and feed no order.
- The RSI closes act on the position held at the bar's start and never undo an entry on that bar (#430850);
  `simulate()` mirrors the house bracket from the fill (as #430254).
- Same logic as #482684 (L32) with other distances and bars; no near-duplicate group, so ported (rule 7).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
