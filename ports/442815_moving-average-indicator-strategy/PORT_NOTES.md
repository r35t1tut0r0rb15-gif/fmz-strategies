# #442815 Moving Average Indicator Strategy -> `fmz_442815_hpotter_obos_stoch_band_reversal`

- FMZ source id: 442815 (lineage).
- Source: https://www.fmz.com/strategy/442815 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-26 11:10:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic band state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `buy_band` [0.92, 0.8]: **4 trials**; the sell band fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
