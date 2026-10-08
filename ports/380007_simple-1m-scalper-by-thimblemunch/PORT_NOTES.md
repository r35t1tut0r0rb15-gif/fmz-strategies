# #380007 Simple 1m Scalper by thimblemunch -> `fmz_380007_stc_trail_scalper`

- Source: https://www.fmz.com/strategy/380007 (PineScript v4, author Zer3192, FMZ last
  modified 2022-08-25 19:55:23). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

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

`trend_len` [14, 21] x `trend_mult` [2.0, 3.0] x `stc_len` [10, 12] = **8 trials**. STC 26/50 and EMA 200 stay at the originals.

## Ambiguities resolved

- STC stages keep their last value when the range is 0 (nz(prev)), as coded.
- The title says 1m but there is no backtest header: `FREQ = "bar_size_pending"` (rule 1).
- Trend line from highest/lowest of the previous 21 bars -+ 3 x WMA(ATR(1)).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`bar_size_pending`
