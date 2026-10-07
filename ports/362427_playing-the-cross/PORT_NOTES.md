# #362427 Playing-the-cross -> `fmz_362427_ema_kijun_cross_faded`

- Source: https://www.fmz.com/strategy/362427 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-11 15:07:20). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

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

`kijun` [9, 26, 52] x `ema_len` [34, 55, 89] = **9 trials**.

## Ambiguities resolved

- **Direction as written**: the EMA falling through the Kijun sends a long. Flagged in the worker report.
- No backtest header: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`bar_size_pending`
