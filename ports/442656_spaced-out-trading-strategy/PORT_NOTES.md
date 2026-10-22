# #442656 Spaced Out Trading Strategy -> `fmz_442656_close_ema30_cross_pct_bracket_long`

- FMZ source id: 442656 (lineage).
- Source: https://www.fmz.com/strategy/442656 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 15:09:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The contract quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [30, 60] x `tp_pct` [0.03, 0.06]: **4 trials**; the stop fraction fixed.

## Ambiguities resolved

- Bracket as fixed fractions of the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
