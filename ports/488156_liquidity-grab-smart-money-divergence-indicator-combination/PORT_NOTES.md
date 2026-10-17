# #488156 流动性捕捉与智能资金分歧指标结合策略-Liquidity-Grab-Smart-Money-Divergence-Indicator-Combination-Strategy -> `fmz_488156_sweep_rsi_divergence_bracket`

- FMZ source id: 488156 (lineage).
- Source: https://www.fmz.com/strategy/488156 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 15:12:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Rolling extremes, an oscillator, a moving average and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [5, 10] x `atr_mult` [1.5, 2.5]: **4 trials**; defaults 5 / 1.5 (the source's); target 2 x the stop, RSI
14, SMA 50 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The windows include the current bar, as written. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  Daily bars are broker days; FREQ = "1D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "liquidity_sweep"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
