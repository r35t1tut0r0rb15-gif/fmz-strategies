# #488279 Multi Timeframe Liquidity Sweep Trend Confirmation Quantitative Trading Strategy -> `fmz_488279_sweep20_h4_bias_atr_bracket_reversal`

- FMZ source id: 488279 (lineage).
- Source: https://www.fmz.com/strategy/488279 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 15:18:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | 20-bar sweeps with a 4-hour bias and an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_factor` [1.5, 2.5] x `tp_factor` [3.0, 5.0]: **4 trials**; sweep 20, bias 10, ATR 14.

## Ambiguities resolved

- The 4-hour values are the day's last 4-hour bar. Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "liquidity_sweep"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
