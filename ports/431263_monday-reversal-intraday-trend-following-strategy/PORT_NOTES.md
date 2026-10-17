# #431263 Monday Reversal Intraday Trend Following Strategy -> `fmz_431263_turnaround_monday_long`

- FMZ source id: 431263 (lineage).
- Source: https://www.fmz.com/strategy/431263 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 15:34:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Weekday and close comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital / close lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`down_bars` [2, 1] x `weekday` [0, 1]: **4 trials**; weekday 0 = Monday (the source's deltaDay 0), 1 = Tuesday.

## Ambiguities resolved

- Monday on the UTC calendar. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
