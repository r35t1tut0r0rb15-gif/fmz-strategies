# #482600 自适应趋势跟踪与动态风控策略-Adaptive-Trend-Following-with-Dynamic-Risk-Control-Strategy -> `fmz_482600_sar_cross_ema50_rsi_flat_atr_pct_bracket`

- FMZ source id: 482600 (lineage).
- Source: https://www.fmz.com/strategy/482600 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 11:26:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (marked). |
| 2 | PASS | The SAR, an EMA, RSI, an ATR multiple and a percentage target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.3, 2.0] x `tp_pct` [0.7, 1.5]: **4 trials**; defaults 1.3 / 0.7 (the source's); SAR 0.02 / 0.02 / 0.2,
EMA 50, RSI 14 (40 / 60) and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

Both exits run every bar from the current close and ATR, so stop and target move with the price. The port fixes
them at the entry's signal bar (re-based on the fill).

## Ambiguities resolved

- Entries from flat only: `simulate()` mirrors the house bracket from the fill (as #430254); re-entry is allowed on
  the bar a stop is hit. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`trailing_stop_pending`
