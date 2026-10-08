# #426855 RSI Reversal Trading Strategy Based on Multi Period RSI -> `fmz_426855_noro_triple_rsi`

- Source: https://www.fmz.com/strategy/426855 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 20:42:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

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

`indi` [2, 3] x `accuracy` [3, 5, 7]: **6 trials**, defaults 3 / 3 (the source's).

## Ambiguities resolved

- Orders fill in issue order; a close_all closes whatever is open when it fills (a reversal bar that also meets the exit ends flat). pyramiding 0.
- Leverage lot is sizing; date window dropped.
- FREQ = "45min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
