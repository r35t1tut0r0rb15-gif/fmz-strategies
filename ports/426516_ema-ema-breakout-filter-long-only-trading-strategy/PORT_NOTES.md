# #426516 EMA Breakout Filter Long Only Trading Strategy -> `fmz_426516_ema_atr_breakout_long`

- Source: https://www.fmz.com/strategy/426516 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-12 17:12:22). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

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

`length` [10, 21, 30]: **3 trials**, default 21 (the source's).

## Ambiguities resolved

- Long only (short entry commented out).
- Weekly bars: calendar weeks of broker-day dates, stamped with the first session start.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
