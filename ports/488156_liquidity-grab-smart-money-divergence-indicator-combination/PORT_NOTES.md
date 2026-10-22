# #488156 Liquidity Grab Smart Money Divergence Indicator Combination Strategy -> `fmz_488156_sweep5_rsi_divergence_sma50_atr_bracket_reversal`

- FMZ source id: 488156 (lineage).
- Source: https://www.fmz.com/strategy/488156 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 15:12:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Swing sweeps with RSI divergence, trend filter and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [5, 10] x `atrMultiplier` [1.5, 2.5]: **4 trials**; RSI 14, SMA 50, ATR 14, target 2 x the stop.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "liquidity_sweep"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
