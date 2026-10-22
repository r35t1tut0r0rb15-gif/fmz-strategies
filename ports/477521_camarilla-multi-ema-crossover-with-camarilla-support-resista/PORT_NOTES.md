# #477521 多重均线交叉结合Camarilla支撑阻力趋势交易系统-Multi-EMA-Crossover-with-Camarilla-Support-Resistance-Trend-Trading-System -> `fmz_477521_close_cross_ema200_ema20_side_tick_profit_close_reversal`

- FMZ source id: 477521 (lineage).
- Source: https://www.fmz.com/strategy/477521 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 11:13:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick exit as an ATR multiple |
| 2 | PASS | EMA 200 close crossings with a small profit exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital 50000 x 100 % / close qty stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`exit_atr` [0.002, 1.0] x `ema_long` [200, 100]: **4 trials**; EMA 20; ATR 14.

## Ambiguities resolved

- 20 ticks as 0.002 ATR 14 (1D ~1000). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
