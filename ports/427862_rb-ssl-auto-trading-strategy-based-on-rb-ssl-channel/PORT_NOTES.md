# #427862 Auto Trading Strategy Based on RB SSL Channel -> `fmz_427862_ssl_channel_flip`

- FMZ source id: 427862 (lineage).
- Source: https://www.fmz.com/strategy/427862 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 12:04:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [13, 20, 30, 50]: **4 trials**; default 13 (the source's).

## Ambiguities resolved

- The first "Period" input is unused. The closes coincide with the opposite entries: REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_channel"`.

## Marks

`none`
