# #426487 Triple EMA Pullback Breakout Trading Strategy -> `fmz_426487_triple_ema_pullback`

- Source: https://www.fmz.com/strategy/426487 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-12 15:12:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Minimum price distance -> ATR(14) multiple on the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [1.5, 2.0, 3.0] x `min_atr` [0.0, 0.5, 1.0]: **9 trials**, defaults 2.0 (the source's) / 0.5 ATR (the source's 50 price units, converted; the step is a port choice). EMA 25 / 100 / 200 fixed.

## Ambiguities resolved

- Stop / target are fractions of the fill price from the signal bar's EMA 100 distance; simulate() mirrors them since entries need a flat position.
- Criterion 2 (ADAPT): the 50-unit minimum distance -> min_atr x ATR(14) on the signal bar.
- Date filter hard-coded off; lotB / lotS are sizing (original_sizing.txt).
- FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks (2026-10-07)

`none`
