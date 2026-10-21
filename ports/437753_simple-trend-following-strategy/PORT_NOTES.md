# #437753 Simple Trend Following Strategy -> `fmz_437753_channel_close_breakout_fast`

- FMZ source id: 437753 (lineage).
- Source: https://www.fmz.com/strategy/437753 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-05 13:09:37). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [20, 10]: **2 trials**; the slow 55 system is unreachable.

## Ambiguities resolved

- Slow system unreachable (pyramiding 0). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
