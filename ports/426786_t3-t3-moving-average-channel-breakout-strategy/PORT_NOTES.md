# #426786 T3 Moving Average Channel Breakout Strategy -> `fmz_426786_t3_channel`

- Source: https://www.fmz.com/strategy/426786 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 15:51:25). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [12, 24, 36]: **3 trials**, default 24 (the source's); b 0.7 fixed.

## Ambiguities resolved

- Direction turns enter (always in).
- 4-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks (2026-10-07)

`none`
