# #442966 Quantitative Oscillation Indicator Combination Strategy -> `fmz_442966_ehlers_eo_decycler_itrend_spearman_combo`

- FMZ source id: 442966 (lineage).
- Source: https://www.fmz.com/strategy/442966 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 16:46:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Squared-price constant -> scaled to the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `rms_length` [50, 100]: **4 trials**.

## Ambiguities resolved

- Squared-price constant scaled to the close; sort loops as written. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "cycle_filter"`.

## Marks

`none`
