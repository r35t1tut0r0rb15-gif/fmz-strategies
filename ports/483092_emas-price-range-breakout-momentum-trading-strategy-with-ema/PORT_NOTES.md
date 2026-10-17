# #483092 基于日内价格区间突破的动量交易策略结合EMAs指标优化-Price-Range-Breakout-Momentum-Trading-Strategy-with-EMAs-Optimization -> `fmz_483092_prev_day_breakout_ema_tick_bracket`

- FMZ source id: 483092 (lineage).
- Source: https://www.fmz.com/strategy/483092 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:20:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill (decision owed). |
| 2 | PASS | Previous-day extremes, EMAs; tick distances as ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_k` [0.17, 0.5] x `rr` [2.0, 3.0]: **4 trials**; defaults 0.17 / 2 (the source's 30 ticks on SOL_USDT, RR 2);
EMA 9 / 21 and ATR 14 fixed.

## Bracket from strategy.position_avg_price (decision owed)

The exit is issued only on signal bars from `strategy.position_avg_price`, which is na while flat, so a trade opened
from flat gets no stop or target until a later same-side signal. The port applies the bracket from the fill (the
evident intent), as #489289. Decision owed: keep this, or port the literal behaviour.

## Tick distances (criterion 2)

30 ticks x mintick 0.01 on SOL_USDT = 0.30 USD against a 1-hour ATR of about 1.8 USD: 0.17 ATR; the target 2 R.
"GER40" in the title is a label.

## Ambiguities resolved

- Previous day = the last completed broker day from the port's own bars (as #430771); the author's chart used UTC
  days. The time filter is off and inert as written (shadowed variable).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
