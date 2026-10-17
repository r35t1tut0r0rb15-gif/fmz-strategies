# #482876 多重指标协同交易系统-基于趋势动量复合信号策略-Multi-Indicator-Synergy-Trading-System-Trend-Momentum-Composite-Signal-Strategy -> `fmz_482876_sma_macd_joint_cross_bracket_trail`

- FMZ source id: 482876 (lineage).
- Source: https://www.fmz.com/strategy/482876 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:10:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket and trail from the fill (decision owed). |
| 2 | PASS | Moving averages, RSI, MACD and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the exits via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [1.0, 2.0] x `tp_pct` [4.0, 6.0]: **4 trials**; defaults 1 / 4 (the source's); SMA 50 / 200, RSI 14,
MACD 12 / 26 / 9 and the 2 % stop fixed.

## Bracket from strategy.position_avg_price (decision owed)

The exit is issued only on signal bars from `strategy.position_avg_price` (na while flat), so from flat nothing is
placed. The port applies the 2 % / 4 % bracket and the trail from the fill (the evident intent), as #489289.

## Trailing stop (mark `trailing_stop`)

`trail_price = avg x 0.99`, `trail_offset = 1 % of the close` becomes `{"type": "percent", "pct": 0.01, "anchor":
"high_low"}` with no activation (stated approximation: for a short the activation would first need a 1 % profit).
Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`). `exitLong` / `exitShort` are
never used.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
