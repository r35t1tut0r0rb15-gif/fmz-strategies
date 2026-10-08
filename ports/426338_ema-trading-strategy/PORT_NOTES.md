# #426338 EMA Trading Strategy -> `fmz_426338_close_vs_ema_long`

- Source: https://www.fmz.com/strategy/426338 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-11 12:02:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

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

`length` [10, 21, 50]: **3 trials**, default 21 (the source's).

## Ambiguities resolved

- Long only: the source has no short entry.
- The counter `p` and the start flag only feed plots / are always true.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
