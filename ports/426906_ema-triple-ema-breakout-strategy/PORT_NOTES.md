# #426906 Triple EMA Breakout Strategy -> `fmz_426906_close_vs_tema`

- Source: https://www.fmz.com/strategy/426906 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-12-01 14:58:23). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [13, 26, 50]: **3 trials**, default 26 (the source's).

## Ambiguities resolved

- "Trade reverse" off.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
