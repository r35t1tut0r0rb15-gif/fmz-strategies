# #427453 KPL Swing Trading Strategy -> `fmz_427453_kpl_swing`

- FMZ source id: 427453 (lineage).
- Source: https://www.fmz.com/strategy/427453 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 11:09:04). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40]: **3 trials**; default 20 (the source's).

## Ambiguities resolved

- `valuewhen(avd != 0, avd, 1)` = the second most recent breakout direction; while undefined the line is the highest high (Pine's else branch on na).
- 2-day bars as worker A's #426995 (block phase decision owed). REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
