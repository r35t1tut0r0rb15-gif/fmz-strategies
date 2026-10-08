# #426616 RSI K Reversal Strategy Based on Fast RSI and Candlestick Colors -> `fmz_426616_noro_hundred`

- Source: https://www.fmz.com/strategy/426616 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-13 17:24:54). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`fast` [5, 7] x `limit` [20, 30] x `cbars` [3, 4]: **8 trials**, defaults 7 / 30 / 4 (the source's); only-profit on.

## Ambiguities resolved

- Entry price = the fill (next open), tracked in simulate(); pyramiding 0, and entries need no opposite position, so positions end only by exit.
- Leverage lot is sizing; date window dropped.
- 4-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
