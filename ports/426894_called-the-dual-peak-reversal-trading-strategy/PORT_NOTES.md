# #426894 Dual Peak Reversal Trading Strategy -> `fmz_426894_hhll_reversed`

- Source: https://www.fmz.com/strategy/426894 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-15 12:33:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A28). Not run.

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

`length` [20, 29, 40] x `reverse` [True, False]: **6 trials**, defaults 29 / True (the source's).

## Ambiguities resolved

- The low test wins when both fire, then reversed (default): such a bar goes short.
- 2018 start date dropped.
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks (2026-10-07)

`none`
