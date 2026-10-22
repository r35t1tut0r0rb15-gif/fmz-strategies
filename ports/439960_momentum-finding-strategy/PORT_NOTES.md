# #439960 Momentum Finding Strategy -> `fmz_439960_noro_squeeze_momentum_mode2`

- FMZ source id: 439960 (lineage).
- Source: https://www.fmz.com/strategy/439960 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-25 12:34:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression momentum and an entry-price test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity lot and leverage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND436540. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_kc` [20, 30, 14]: **3 trials**.

## Ambiguities resolved

- Mode 2; the final close_all leaves the bar flat. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
