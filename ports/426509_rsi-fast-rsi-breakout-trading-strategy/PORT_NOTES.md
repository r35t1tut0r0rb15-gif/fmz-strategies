# #426509 RSI Fast RSI Breakout Trading Strategy -> `fmz_426509_noro_fast_rsi_v13`

- Source: https://www.fmz.com/strategy/426509 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-12 16:34:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426509` (Jaccard 0.65-0.80) with #430017 (PORT_CANDIDATE); best Jaccard 0.656 with #430017. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsiperiod` [5, 7] x `limit` [20, 30]: **4 trials**, defaults 7 / 30 (the source's); body ratios fixed.

## Ambiguities resolved

- Re-read in A27: rejected in A22 as a pyramided ladder, but SURVEY_README classes pyramiding adds as sizing; the net position is ported.
- Average price = the position's first fill.
- Orders fill in issue order; close_all closes whatever is open when it fills. Date window dropped.
- 2-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
