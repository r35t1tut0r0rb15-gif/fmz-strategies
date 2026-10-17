# #483496 多重指标动量突破趋势交易策略-Multi-Indicator-Momentum-Breakout-Trend-Trading-Strategy -> `fmz_483496_wpr_macd_cross_ema55_tick_bracket`

- FMZ source id: 483496 (lineage).
- Source: https://www.fmz.com/strategy/483496 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 09:18:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed bracket from the fill. |
| 2 | PASS | %R, MACD, an EMA and distances relative to price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bracket_mult` [1.0, 2.0] x `ema_length` [55, 100]: **4 trials**; defaults 1 / 55 (the source as written); %R 14
(-20 / -80) and MACD 12 / 26 / 9 fixed.

## Tick arguments given prices

`strategy.exit(loss = avg_price x 0.98, profit = avg_price x 1.03)`: `loss` / `profit` are ticks, so the distances are
0.98 x price x mintick and 1.03 x price x mintick. With SOL_USDT's mintick 0.01 that is a 0.98 % stop and a 1.03 %
target for a long (1.02 % / 0.97 % for a short). Ported as written (as #427729); `bracket_mult` scales them.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_cross"`.

## Marks

`none`
