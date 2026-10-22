# #477955 Intelligent Moving Average Crossover Strategy with Dynamic Profit Loss Management System -> `fmz_477955_sma7_40_cross_pct_bracket_long`

- FMZ source id: 477955 (lineage).
- Source: https://www.fmz.com/strategy/477955 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:39:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill |
| 2 | PASS | SMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 20] x `slow` [40, 100]: **4 trials**; stop 1 %, target 2 %.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
