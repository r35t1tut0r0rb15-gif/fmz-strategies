# #426852 RSI Quantitative Trading Strategy Based on RSI Indicator Signals -> `fmz_426852_rsi_percent_b`

- Source: https://www.fmz.com/strategy/426852 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-14 20:26:49). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`smooth` [14, 28] x `length` [40, 80] x `mult` [2, 3]: **8 trials**, defaults 28 / 80 / 3 (the source's); RSI 14 and levels 0.2 / 0.8 fixed.

## Ambiguities resolved

- Fills in issue order: a reversing entry stands; a close of the side held goes flat.
- Pine population stdev.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
