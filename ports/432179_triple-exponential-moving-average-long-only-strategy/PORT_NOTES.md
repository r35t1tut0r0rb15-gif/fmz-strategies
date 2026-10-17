# #432179 Triple Exponential Moving Average Long Only Strategy -> `fmz_432179_tema_close_long`

- FMZ source id: 432179 (lineage).
- Source: https://www.fmz.com/strategy/432179 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-15 10:54:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against a TEMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tema_len` [7, 14, 21]: **3 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
