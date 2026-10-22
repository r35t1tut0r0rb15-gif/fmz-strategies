# #474630 Triple Bollinger Bands Touch Trend Following Quantitative Trading Strategy -> `fmz_474630_bb20_three_closes_outside_basis_cross_exit`

- FMZ source id: 474630 (lineage).
- Source: https://www.fmz.com/strategy/474630 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-11 11:01:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three closes outside the bands with a basis-cross exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**; three closes.

## Ambiguities resolved

- REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
