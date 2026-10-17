# #435105 Momentum Filtering Moving Average Strategy -> `fmz_435105_filtered_cmo_bands`

- FMZ source id: 435105 (lineage).
- Source: https://www.fmz.com/strategy/435105 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-12 12:35:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | The price-unit filter -> an ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 20] x `filt_atr` [0.015, 0.3]: **4 trials**; bands 70 / -70 and ATR 14 fixed.

## Ambiguities resolved

- Price-unit filter -> ATR multiple. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
