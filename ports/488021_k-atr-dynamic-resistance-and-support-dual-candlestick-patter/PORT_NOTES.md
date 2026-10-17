# #488021 动态阻力与支撑的双K线形态ATR风险控制量化交易策略-Dynamic-Resistance-and-Support-Dual-Candlestick-Pattern-ATR-Risk-Management-Quantitative-Trading-Strategy -> `fmz_488021_engulfing_in_range_atr_bracket`

- FMZ source id: 488021 (lineage).
- Source: https://www.fmz.com/strategy/488021 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-24 14:24:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Candle patterns, rolling extremes and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `lookback` [50, 20]: **4 trials**; defaults 1.5 / 50 (the source's); target 2 x the stop and
ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The windows include the current bar, as written. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  Three-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "3D":
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
