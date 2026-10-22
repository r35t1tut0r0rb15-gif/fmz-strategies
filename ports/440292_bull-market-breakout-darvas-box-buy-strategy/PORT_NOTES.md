# #440292 Bull Market Breakout Darvas Box Buy Strategy -> `fmz_440292_darvas_box_breakout_long`

- FMZ source id: 440292 (lineage).
- Source: https://www.fmz.com/strategy/440292 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 09:53:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving box bottom pending |
| 2 | PASS | Box levels from past highs and lows |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`box_len` [5, 10]: **2 trials**; target multiple 5 fixed.

## Ambiguities resolved

- Box-bottom stop from the signal bar; its later moves pending. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending`
