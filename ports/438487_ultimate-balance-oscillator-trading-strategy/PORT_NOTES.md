# #438487 Ultimate Balance Oscillator Trading Strategy -> `fmz_438487_ultimate_balance_oscillator_long`

- FMZ source id: 438487 (lineage).
- Source: https://www.fmz.com/strategy/438487 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:08:33). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Normalised oscillators and ADX |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ob_level` [0.75, 0.65] x `os_level` [0.25, 0.35]: **4 trials**; weights and lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
