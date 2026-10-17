# #483120 多重均线交叉与RSI动量联动短线自适应交易策略-Multi-EMA-Crossover-with-RSI-Momentum-Adaptive-Scalping-Strategy -> `fmz_483120_ema9_21_ema50_rsi_band_pct_bracket`

- FMZ source id: 483120 (lineage).
- Source: https://www.fmz.com/strategy/483120 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:27:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.5, 2.0] x `tp_pct` [1.0, 4.0]: **4 trials**; defaults 0.5 / 1 (the source's); EMA 9 / 21 / 50 and the RSI
bands fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new close. The port keeps the entry's bracket.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
