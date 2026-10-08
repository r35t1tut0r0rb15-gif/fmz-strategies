# #426783 Williams R Indicator Trading Strategy -> `fmz_426783_williams_r_long`

- Source: https://www.fmz.com/strategy/426783 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-14 15:38:51). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

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

`length` [7, 14, 21] x `oversold` [-80, -90]: **6 trials**, defaults 14 / -80 (the source's); overbought -20 fixed.

## Ambiguities resolved

- Long only.
- FREQ = "12h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "williams_r_oscillator"`.

## Marks (2026-10-07)

`none`
