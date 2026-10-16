# #428785 Dual Momentum Strategy -> `fmz_428785_simple_momentum_blocks`

- FMZ source id: 428785 (lineage).
- Source: https://www.fmz.com/strategy/428785 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-09 15:03:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Close comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() line stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`enter_after` [2, 3] x `exit_after` [1, 2]: **4 trials**; the same counts for both sides, as the defaults.

## Ambiguities resolved

- One target per bar: an entry signal wins over the other side's exit; otherwise the exits flatten.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
