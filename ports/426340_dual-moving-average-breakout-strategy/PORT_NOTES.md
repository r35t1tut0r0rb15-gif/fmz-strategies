# #426340 Dual Moving Average Breakout Strategy -> `fmz_426340_noro_multima`

- Source: https://www.fmz.com/strategy/426340 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-11 12:31:51). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`len_sma` [20, 40, 80] x `len_ema` [20, 40, 80]: **9 trials**, defaults 40 / 40 (the source's).

## Ambiguities resolved

- Warm-up: `close > na` is false, so signal1 = -1 until SMA 40 exists (as Pine).
- Both MAs and the colour filter on (source defaults); long / short both enabled.
- FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
