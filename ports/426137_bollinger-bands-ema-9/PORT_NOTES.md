# #426137 Bollinger Bands + EMA 9 -> `fmz_426137_bb_lower_ema9_exit_long`

- Source: https://www.fmz.com/strategy/426137 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-08 16:00:29). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

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

`length` [10, 20] x `mult` [1.5, 2.0, 2.5] = **6 trials**. EMA 9 exit stays at the original.

## Ambiguities resolved

- Close not applied on its own entry bar; entries while long ignored (mirrored position). Long only (rule 6).
- Entry tests close[1] against the current lower band, as coded. Qty 1 -> sizing.
- Daily bars are broker days (17:00 New York), `FREQ = "1D"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`
