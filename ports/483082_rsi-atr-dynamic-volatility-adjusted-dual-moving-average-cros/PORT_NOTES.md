# #483082 基于动态波动率调整的双均线交叉与RSI-ATR复合过滤交易系统-Dynamic-Volatility-Adjusted-Dual-Moving-Average-Crossover-System-with-RSI-ATR-Composite-Filter -> `fmz_483082_sma9_21_cross_rsi_pct_bracket_rr`

- FMZ source id: 483082 (lineage).
- Source: https://www.fmz.com/strategy/483082 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:58:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill (decision owed). |
| 2 | PASS | Moving averages, RSI and percentage distances; the price-unit ATR floor is inert. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty quoted, not ported; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.5, 1.0] x `rr` [2.0, 3.0]: **4 trials**; defaults 0.5 / 2 (the source's); SMA 9 / 21 and RSI 14 (70 / 30)
fixed.

## Bracket from strategy.position_avg_price (decision owed)

The exit is issued only on signal bars from `strategy.position_avg_price` (na while flat), so a trade opened from flat
gets its bracket only from a later same-side signal. The port applies it from the fill (the evident intent), as
#489289. Decision owed: keep this, or port the literal behaviour.

## Ambiguities resolved

- `atr > 0.005` (price units) is always true on SOL_USDT: dropped as inert (as #492009).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
