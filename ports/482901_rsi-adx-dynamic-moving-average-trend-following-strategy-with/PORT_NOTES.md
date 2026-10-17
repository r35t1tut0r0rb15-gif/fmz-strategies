# #482901 均线动态趋势跟踪与RSI-ADX复合指标交易策略-Dynamic-Moving-Average-Trend-Following-Strategy-with-RSI-ADX-Composite-Indicators -> `fmz_482901_sma200_cross_confirm_flat_bracket`

- FMZ source id: 482901 (lineage).
- Source: https://www.fmz.com/strategy/482901 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:27:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar. |
| 2 | PASS | Moving averages, RSI, ADX, ATR multiples and a percentage target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [2.0, 5.0] x `sl_mult` [1.5, 2.5]: **4 trials**; defaults 2 / 1.5 (the source's); SMA 200, RSI 14, DMI
14 / 14 and ATR 14 fixed.

## Ambiguities resolved

- Entries only from flat: `simulate()` mirrors the house bracket from the fill bar (as #430254 `_run`); the sell close
  is an exit signal. Long only: opposite entries cannot occur.
- Stop module: `portfolio_kwargs` {} (D4). Broker days stamped with their first minute (as #430984); stops on daily
  bars: `coarse_bar_stop`. FREQ = "1D" ("BTC/USD" is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
