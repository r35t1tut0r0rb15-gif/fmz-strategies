# #443136 Adaptive Channel Breakout Strategy -> `fmz_443136_turtle_channel_touch_alternating_reversal`

- FMZ source id: 443136 (lineage).
- Source: https://www.fmz.com/strategy/443136 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-29 14:49:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel touches with an alternation test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 55]: **2 trials**; the exit length only feeds the empty exits.

## Ambiguities resolved

- Empty exits place nothing. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
