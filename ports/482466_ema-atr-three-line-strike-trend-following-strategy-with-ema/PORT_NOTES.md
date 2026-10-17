# #482466 三线突破趋势跟踪策略结合EMA动态过滤和ATR风险管理系统-Three-Line-Strike-Trend-Following-Strategy-with-EMA-Dynamic-Filter-and-ATR-Risk-Management-System -> `fmz_482466_three_line_strike_ema200_atr_bracket`

- FMZ source id: 482466 (lineage).
- Source: https://www.fmz.com/strategy/482466 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:30:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | Candle colours and sizes, an EMA and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `tp_mult` [2, 3]: **4 trials**; defaults 200 / 2 (the source's); ATR 14 and the 1 ATR stop
fixed.

## Ambiguities resolved

- Engulfing = colour flip with a larger absolute body than the previous bar (as written).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
