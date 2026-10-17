# #432333 Heikin Ashi Reverse Strategy -> `fmz_432333_double_heikin_ashi_turn_long`

- FMZ source id: 432333 (lineage).
- Source: https://www.fmz.com/strategy/432333 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 15:44:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colour turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`passes` [2, 1]: **2 trials** (2 as written; 1 drops the second pass).

## Ambiguities resolved

- Two Heikin Ashi passes as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
