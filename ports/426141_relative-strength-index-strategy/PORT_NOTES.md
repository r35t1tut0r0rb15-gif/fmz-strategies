# #426141 QuantNomad - RSI Strategy - LTCUSDT - 5m -> `fmz_426141_rsi3_47_56_flip`

- Source: https://www.fmz.com/strategy/426141 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-08 16:10:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [3, 5, 7] x `over_sold` [40, 47] x `over_bought` [56, 60] = **12 trials**.

## Ambiguities resolved

- Title says 5m; the backtest header runs daily bars (used).
- Entries reverse; no other exits.
- Daily bars are broker days (17:00 New York), `FREQ = "1D"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
