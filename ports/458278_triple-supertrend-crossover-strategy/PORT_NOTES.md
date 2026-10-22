# #458278 Triple Supertrend Crossover Strategy -> `fmz_458278_any_of_three_supertrend_cross_long`

- FMZ source id: 458278 (lineage).
- Source: https://www.fmz.com/strategy/458278 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:57:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (lengths and factors are constants).

## Ambiguities resolved

- Call order followed (entry, then close). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
