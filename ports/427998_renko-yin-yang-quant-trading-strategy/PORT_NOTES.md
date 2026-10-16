# #427998 Renko Yin Yang Quant Trading Strategy -> `fmz_427998_renko_close_open_bricks_long`

- FMZ source id: 427998 (lineage).
- Source: https://www.fmz.com/strategy/427998 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 17:11:30). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR bricks only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 5, 14, 20]: **4 trials**; default 10 (the source's).

## Ambiguities resolved

- The bricks start at 0 and move one ATR per bar at most (as written: a slow climb from 0 at the start).
- barssince na before the first event; Renko2 unused. Shorts off: Long only. Date window dropped. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "renko_bricks"`.

## Marks

`none`
