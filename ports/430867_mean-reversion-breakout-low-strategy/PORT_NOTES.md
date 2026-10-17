# #430867 Mean Reversion Breakout Low Strategy -> `fmz_430867_broken_low_reversion_long`

- FMZ source id: 430867 (lineage).
- Source: https://www.fmz.com/strategy/430867 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 15:34:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rolling extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars` [9, 20, 5]: **3 trials**; one broken low.

## Ambiguities resolved

- Entry and close on one bar: flat if already long, long if flat. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
