# #426625 Trend Following Strategy Based on Dual EMA -> `fmz_426625_ema_50_200_state`

- Source: https://www.fmz.com/strategy/426625 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 18:04:52). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

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

`fast` [20, 50] x `slow` [100, 200]: **4 trials**, defaults 50 / 200 (the source's).

## Ambiguities resolved

- Entries pass qty = 0 (sizing, out of scope; literally no order would be sized: decision owed). The signal rule is ported.
- The closes are redundant with the reversing entries.
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
