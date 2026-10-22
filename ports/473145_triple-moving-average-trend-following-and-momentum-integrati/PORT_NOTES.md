# #473145 Triple Moving Average Trend Following and Momentum Integration Quantitative Trading Strategy -> `fmz_473145_tema_macd_armed_ema_cross_up_long`

- FMZ source id: 473145 (lineage).
- Source: https://www.fmz.com/strategy/473145 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:08:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Armed EMA cross-ups; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [14, 21] x `fast` [13, 12] x `slow` [18, 26]: **8 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending); the first long is held. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
