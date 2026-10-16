# #427733 MACD Momentum Indicator Backtest Strategy -> `fmz_427733_macd_cross_after_rsi_turn`

- FMZ source id: 427733 (lineage).
- Source: https://www.fmz.com/strategy/427733 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-24 13:21:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry. |
| 2 | PASS | Oscillator levels and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() sizing stored; stop quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_lookback` [7, 14] x `loss_pct` [15, 5]: **4 trials**; defaults 7 / 15 (the source's); RSI 14 (30 / 70) and MACD 12/26/9 fixed.

## Ambiguities resolved

- The look-back covers the previous 7 bars, not the current one (`for i = 1 to _lookback`).
- strategy() commented out: one position. Percent-of-entry stop: `sl_stop` 0.15.
- Date range dropped. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
