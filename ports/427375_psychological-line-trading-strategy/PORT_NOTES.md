# #427375 Psychological Line Trading Strategy -> `fmz_427375_psychological_line`

- FMZ source id: 427375 (lineage).
- Source: https://www.fmz.com/strategy/427375 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-20 14:50:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Share of up-closes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 12, 40]: **3 trials**; default 20 (the source's).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "15min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
