# #445836 Bollinger Band Dynamic Take Profit and Dynamic Position Adding Strategy -> `fmz_445836_band_extreme_flag_reversal`

- FMZ source id: 445836 (lineage).
- Source: https://www.fmz.com/strategy/445836 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 15:49:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band extremes with entry flags |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The qty (initial_capital / 10000) stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [12, 20] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- Add-ons never act (no pyramiding); asymmetric flags as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
