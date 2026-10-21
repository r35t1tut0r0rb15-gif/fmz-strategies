# #439084 Ehlers Stochastic Cyber Cycle Strategy -> `fmz_439084_ehlers_stoch_cyber_cycle_opposite`

- FMZ source id: 439084 (lineage).
- Source: https://www.fmz.com/strategy/439084 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-17 16:03:30). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested loss exit |
| 2 | PASS | Cyber cycle stochastic turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, pyramiding and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND439084. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`alpha` [0.07, 0.15] x `len` [8, 16]: **4 trials**; opposite trade on; the 8-bar loss rule fixed.

## Ambiguities resolved

- Opposite trades; bar-count loss exit. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
