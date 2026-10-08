# #426883 Quantitative Trading Strategy Based on Gann Swing Oscillator -> `fmz_426883_gann_swing_oscillator`

- Source: https://www.fmz.com/strategy/426883 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-15 11:37:37). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [3, 5, 8]: **3 trials**, default 3 (the source's).

## Ambiguities resolved

- The -1 test comes first (short_first), as in the source.
- "Trade reverse" off.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
