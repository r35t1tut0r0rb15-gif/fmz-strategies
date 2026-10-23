# #442333 Quantitative Breakthrough Uptrend Reference Strategy -> `fmz_442333_close_above_pivot_confirm_level_late_bracket_long_only`

- FMZ source id: 442333 (lineage).
- Source: https://www.fmz.com/strategy/442333 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 10:58:01). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; late-armed bracket followed in the signals |
| 2 | PASS | Closes above a pivot-confirmation level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 1500, commission 0.01 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`left` [46, 20] x `right` [32, 10]: **4 trials**; TP 2 %, SL 1.75 %.

## Ambiguities resolved

- Level = close at the pivot's confirmation; late-armed bracket in the signals. Volume not used. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`trailing_stop_pending`
