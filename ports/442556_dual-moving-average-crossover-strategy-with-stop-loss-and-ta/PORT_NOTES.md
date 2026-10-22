# #442556 Dual Moving Average Crossover Strategy with Stop Loss and Take Profit -> `fmz_442556_stoch_extreme_cross_atr_bracket`

- FMZ source id: 442556 (lineage).
- Source: https://www.fmz.com/strategy/442556 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 17:30:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442556. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `tp_atr` [0.03, 1.0]: **4 trials**; the levels and the stop multiple fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples; closes act on their own held id. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
