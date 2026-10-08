# #426995 Dynamic Price Channel Trading Strategy -> `fmz_426995_noro_bands_scalper`

- Source: https://www.fmz.com/strategy/426995 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-16 19:01:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426995` (Jaccard 0.65-0.80) with #430007 (PORT_CANDIDATE), #432340 (PORT_CANDIDATE), #435019 (PORT_CANDIDATE); best Jaccard 0.744 with #435019. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20, 40]: **3 trials**, default 20 (the source's); take 0 %, counter-trend off.

## Ambiguities resolved

- Counter-trend off: an entry against the trend has qty 0 and only closes the opposite position (Noro's idiom).
- Average price = the position's fill; na when flat (closing tests false).
- 2-day bars from broker days in fixed blocks from 1970-01-01 (decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
