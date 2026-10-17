# #491914 价格行为结构突破-跟踪止损策略-Price-Action-Structural-Breakout-Strategy-with-Trailing-Stop -> `fmz_491914_smc_bos_candles_atr_trail`

- FMZ source id: 491914 (lineage).
- Source: https://www.fmz.com/strategy/491914 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-24 18:25:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed after their right bars; the trail is a house trail (approximations stated). |
| 2 | PASS | Percentage proximity bands, ATR-scaled candle tests, oscillators. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the trail via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_k` [0.5, 1.0] x `trail_activate` [0.0015, 0.003]: **4 trials**; defaults 0.5 / 0.0015; pivots 10 / 10,
EMA 20 / 200, RSI 14, CCI 20, ATR 14 and the 0.98-1.01 / 0.99-1.02 proximity bands fixed (the source's).

## Trailing stop (mark `trailing_stop`)

As written, on the entry bar: `strategy.exit(trail_points = ATR x 1.0, trail_offset = ATR x 0.5)`. Both arguments
take ticks, but the author passes ATR price distances; read as the author evidently meant (price distances, as
#427592). Ported as the house trail `{"type": "volatility", "atr_n": 14, "k": 0.5, "anchor": "high_low",
"activate_after": 0.0015}`. **Stated approximations:** Pine fixes the distances at the entry bar's ATR (the house
trail uses the last completed bar's); the 1-ATR activation becomes a 0.15 % gain (about one 2-minute ATR on
DOGE_USDT). Read literally in ticks, both distances are a tiny fraction of one tick (an exit on the first retrace);
decision owed if the literal reading is wanted. Promotion of a trailing trial needs the cTrader check
(gate `trailing_ctrader_check`).

## Ambiguities resolved

- Pivots strict (ties are not pivots), confirmed 10 bars later, the zone holding its last value.
- Candle shapes as written (the "bull pinbar" is an upper-wick shape; a doji counts for both sides).
- Both signals on one bar: the short (written last) wins. REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action_breakout"`.

## Marks

`trailing_stop`
