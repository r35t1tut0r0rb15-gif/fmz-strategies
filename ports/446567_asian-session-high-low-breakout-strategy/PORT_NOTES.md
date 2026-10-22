# #446567 Asian Session High Low Breakout Strategy -> `fmz_446567_asia_session_range_contrarian_break_reversal`

- FMZ source id: 446567 (lineage).
- Source: https://www.fmz.com/strategy/446567 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-29 17:12:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the session range from completed bars; the moving bracket not ported (mark) |
| 2 | PASS | Contrarian session-range breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the 300-tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_start` [19, 22] x `offset_hours` [3, 6]: **4 trials**; the session end 01:00 fixed.

## Ambiguities resolved

- UTC hours; moving bracket pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop_pending`
