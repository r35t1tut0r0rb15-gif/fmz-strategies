# #482917 基于Nadaraya-Watson的多维度整合交易策略-Multi-Dimensional-Integration-Trading-Strategy-Based-on-Nadaraya-Watson -> `fmz_482917_kernel_blend_cross_trend_rsi_bracket`

- FMZ source id: 482917 (lineage).
- Source: https://www.fmz.com/strategy/482917 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:21:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed bracket from the fill. |
| 2 | PASS | A smoothed blend crossing its own average; percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.5, 1.0] x `tp_pct` [3.0, 2.0]: **4 trials**; defaults 1.5 / 3 (the source's); weights, smoothing 20,
bandwidth 20, SMA 200 and RSI 50 fixed.

## Ambiguities resolved

- The kernel puts its heaviest weight on the oldest bar of the window, as written; the blend is dominated by price.
- The bracket uses `strategy.position_avg_price` on every bar while held: fixed from the fill.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "kernel_regression"`.

## Marks

`none`
