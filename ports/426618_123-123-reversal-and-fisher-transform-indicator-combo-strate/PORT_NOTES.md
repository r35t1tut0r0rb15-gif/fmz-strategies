# #426618 123 Reversal and Fisher Transform Indicator Combo Strategy -> `fmz_426618_combo_123_reversal_fisher`

- Source: https://www.fmz.com/strategy/426618 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-13 17:35:36). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [14, 15, 21] x `length_fti` [10, 14]: **6 trials**, defaults 15 / 10 (the source's); k 1, d 3, level 50 fixed.

## Ambiguities resolved

- A flat hl2 window gives na for that bar, restarting from nz() next bar (as Pine).
- "Trade reverse" off.
- FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
