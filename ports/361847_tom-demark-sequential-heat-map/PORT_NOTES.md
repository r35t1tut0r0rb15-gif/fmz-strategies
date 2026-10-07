# #361847 Tom-DeMark-Sequential-Heat-Map -> `fmz_361847_td_setup13_fade`

- Source: https://www.fmz.com/strategy/361847 (PineScript v5, author ChaoZhang (Indicator-Jones indicator), FMZ last
  modified 2022-05-08 17:29:16). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | No venue code. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same idea as #262467 (different counts and exits). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [3, 4, 5] x `count` [9, 13] = **6 trials** (13 is the source; 9 the classic setup).

## Ambiguities resolved

- Counts wrap from 13 to 1, so a 13 appears every 13 bars of a persistent run.
- No backtest header: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "td_sequential"`.

## Marks (2026-10-07)

`bar_size_pending`
