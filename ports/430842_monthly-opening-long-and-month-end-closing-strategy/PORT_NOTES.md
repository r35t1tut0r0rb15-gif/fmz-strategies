# #430842 Monthly Opening Long and Month end Closing Strategy -> `fmz_430842_monday_to_friday_long`

- FMZ source id: 430842 (lineage).
- Source: https://www.fmz.com/strategy/430842 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 14:23:40). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A weekday calendar rule. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_day` [0, 1] x `exit_day` [4, 3]: **4 trials**; weekday numbers Monday = 0 (Monday / Friday the source's).

## Ambiguities resolved

- Weekday of the broker day. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
