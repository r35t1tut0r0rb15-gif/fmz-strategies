# #482502 多周期均线趋势判断与RSI超买策略-Multi-Period-EMA-Trend-Detection-with-RSI-Overbought-Strategy -> `fmz_482502_ema20_cross_rising_emas_rsi70_exit_long`

- FMZ source id: 482502 (lineage).
- Source: https://www.fmz.com/strategy/482502 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 17:50:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and an RSI level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `rsi_exit` [70, 80]: **4 trials**; defaults 20 / 70 (the source's); EMA 50 / 100 and RSI 14 fixed.

## Ambiguities resolved

- The close acts on the position held at the bar's start and never undoes an entry on that bar (#430850).
- Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
