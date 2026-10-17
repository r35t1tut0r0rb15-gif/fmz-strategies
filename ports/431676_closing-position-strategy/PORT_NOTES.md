# #431676 Closing Position Strategy -> `fmz_431676_end_of_day_sma200`

- FMZ source id: 431676 (lineage).
- Source: https://www.fmz.com/strategy/431676 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-10 14:25:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | A clock time and an SMA comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [200, 100] x `entry_hour` [20, 16]: **4 trials** (UTC hours).

## Ambiguities resolved

- The 09:30 exit never fires on hourly bars; the 20:00 entry in UTC. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
