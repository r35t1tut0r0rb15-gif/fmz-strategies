# #432774 Quantitative Zigzag Strategy -> `fmz_432774_candle_colour_change_wave_count_28_reversal`

- FMZ source id: 432774 (lineage).
- Source: https://www.fmz.com/strategy/432774 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 15:01:07). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle-colour change counting |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): capital 1000 only, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wave_number` [28, 14] x `start_direction` [1, -1]: **4 trials**.

## Ambiguities resolved

- Count starts at the first loaded bar (data-start dependent). Volume and coin-flip parts off. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bar_pattern"`.

## Marks

`none`
