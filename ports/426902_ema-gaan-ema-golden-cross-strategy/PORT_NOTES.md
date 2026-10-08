# #426902 Gaan EMA Golden Cross Strategy -> `fmz_426902_gaan_ema`

- Source: https://www.fmz.com/strategy/426902 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-12-01 14:57:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`fast` [9, 13] x `mid` [27, 34] x `slow` [81, 100]: **8 trials**, defaults 9 / 27 / 81 (the source's).

## Ambiguities resolved

- The closes sit inside the short block (as indented): positions change only by reversal.
- FREQ = "2min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
