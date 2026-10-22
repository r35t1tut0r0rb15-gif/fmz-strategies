# #458071 Multi Indicator Divergence Trading Strategy with Adaptive Take Profit and Stop Loss -> `fmz_458071_rsi_macd_stoch_signal_cross_pct_bracket_reversal`

- FMZ source id: 458071 (lineage).
- Source: https://www.fmz.com/strategy/458071 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 17:02:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions |
| 2 | PASS | Oscillator signal-line crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.20, 0.05] x `sl_pct` [0.10, 0.03]: **4 trials**; the oscillator lengths fixed.

## Ambiguities resolved

- Bracket from the fill bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
