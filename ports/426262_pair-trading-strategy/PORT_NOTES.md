# #426262 Pair trading strategy -> `fmz_426262_bollinger_cross_reversion`

- Source: https://www.fmz.com/strategy/426262 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-10 00:17:24). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [20, 30] x `zscore` [1.5, 2.0, 2.5]: **6 trials**, defaults 20 / 2.0 (the source's).

## Ambiguities resolved

- The title says pair trading, but the code trades one instrument against its own bands; ported as coded.
- `cross` either direction, as written; Pine population stdev.
- `close_all(immediately=true)` fills at the signal close in Pine, at the next open here; same-bar entries leave their side (short wins when both fire).
- Start-year filter is a backtest window: dropped.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`
