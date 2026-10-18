# #435903 Bollinger带动量突破策略Bollinger-Bands-Momentum-Breakout-Strategy -> `fmz_435903_bollinger_basis_cross`

- FMZ source id: 435903 (lineage).
- Source: https://www.fmz.com/strategy/435903 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-19 16:24:24). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30, 40]: **3 trials**.

## Ambiguities resolved

- Closes called only inside the entry blocks (never fire). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
