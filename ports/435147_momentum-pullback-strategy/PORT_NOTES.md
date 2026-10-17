# #435147 Momentum Pullback Strategy -> `fmz_435147_momentum_pullback_ema5`

- FMZ source id: 435147 (lineage).
- Source: https://www.fmz.com/strategy/435147 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 16:34:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; rolling target fixed at entry (approximation stated); ATR exit on closes |
| 2 | PASS | RSI extremes, EMA pullbacks and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 2, commission and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_inp` [2.75, 1.5] x `look` [12, 24]: **4 trials**; RSI 6 90 / 10, EMA 5 and the 6-bar window fixed.

## Ambiguities resolved

- Rolling target fixed at the signal bar (trailing_stop_pending); ATR exit on closes. Marks trailing_stop_pending, coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
