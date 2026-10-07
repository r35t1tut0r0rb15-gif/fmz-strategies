# #262467 TD狄马克序列 -> `fmz_262467_td_count_fade`

- Source: https://www.fmz.com/strategy/262467 (Python, author btccccrazy, FMZ last modified
  2021-03-16 11:18:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls every 15 min on the forming hourly bar; the port evaluates on completed bars. |
| 2 | PASS | Bar counts only. |
| 3 | PASS (screen: REVIEW) | Quarterly contract is the venue only. |
| 4 | DONE | One contract per order, repeated orders on later polls (adds) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`lookback` [3, 4, 5] x `exit_count` [1, 2, 3] = **9 trials**. Setup levels 9/13/22 fixed.

## Ambiguities resolved

- The source's position check (`len(position) > 0 ... position[0]`) only looks at the first leg;
  the port keeps one net position.
- `FREQ = "1h"` from `GetRecords(PERIOD_H1)`.

## FAMILY (proposed, user to confirm)

`FAMILY = "td_sequential"`: counter-trend fade of DeMark-style setup counts.

## Marks (2026-10-07)

`none`
