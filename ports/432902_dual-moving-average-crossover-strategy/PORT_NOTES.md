# #432902 Dual Moving Average Crossover Strategy -> `fmz_432902_ha_awesome_oscillator_long`

- FMZ source id: 432902 (lineage).
- Source: https://www.fmz.com/strategy/432902 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-22 16:10:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 3] x `slow` [34, 21]: **4 trials**.

## Ambiguities resolved

- Shorts off: the short side only closes the long. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
