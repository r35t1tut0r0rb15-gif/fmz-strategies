# #490042 多重背离综合指标交易策略-Multi-Indicator-Divergence-Trading-System-with-Advanced-Risk-Management -> `fmz_490042_triple_cross_sma50_bracket_trail_long`

- FMZ source id: 490042 (lineage).
- Source: https://www.fmz.com/strategy/490042 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-11 09:22:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill; the trail a house trail (approximation stated). |
| 2 | ADAPT | Tick trail -> ATR multiple / fraction; percentage bracket. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; exits via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_k` [0.002, 0.5] x `ma_len` [50, 100]: **4 trials**; defaults 0.002 / 50 (the source's equivalents); RSI,
MACD and stochastic settings, SL 1.5 %, TP 3 % and the activation fixed.

## Trailing stop (mark `trailing_stop`)

As written, every bar: `strategy.exit(stop = avg x 0.985, limit = avg x 1.03, trail_points = 10, trail_offset = 5)`
(ticks). Ported as `sl_stop` 0.015, `tp_stop` 0.03 plus the house trail `{"type": "volatility", "atr_n": 14,
"k": 0.002, "anchor": "high_low", "activate_after": 0.000033}`. **Stated approximation:** on hourly ETH_USDT (tick
0.01 at about 3000) 5 ticks are about 0.002 ATR and 10 ticks a 0.0033 % gain: as written the trail exits on the
first small retrace. The grid also tries k = 0.5. Promotion of a trailing trial needs the cTrader check
(gate `trailing_ctrader_check`).

## Ambiguities resolved

- The sell condition is computed but never traded: long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop`
