# #482437 基于移动平均线的自适应趋势跟踪策略-Adaptive-Trend-Following-Strategy-Based-on-Moving-Average-Crossover -> `fmz_482437_sma74_70_cross_flat_atr_bracket`

- FMZ source id: 482437 (lineage).
- Source: https://www.fmz.com/strategy/482437 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:23:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket from the fill. |
| 2 | PASS | SMAs and ATR multiples; the USD distances converted. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Trade size 1; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.35, 1.0] x `fast` [74, 20]: **4 trials**; defaults 0.35 / 74 (the source's 353 USD and 74); SMA 70, ATR 14
and the 3 x target fixed.

## Ambiguities resolved

- 353 / 1059 USD on BTC_USDT 4-hour bars (ATR about 1000 in 2024-25) read as 0.35 / 1.05 ATR (criterion 2, as
  #489333); measured from `strategy.position_avg_price`, applied from the fill (decision owed as #489289).
- Entries from flat only: `simulate()` mirrors the house bracket from the fill (as #430254). The date window is off
  in the source. Stop module: `portfolio_kwargs` {} (D4). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
