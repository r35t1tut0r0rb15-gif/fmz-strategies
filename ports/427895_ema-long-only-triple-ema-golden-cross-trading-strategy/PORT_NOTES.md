# #427895 Long Only Triple EMA Golden Cross Trading Strategy -> `fmz_427895_ema_golden_cross_long`

- FMZ source id: 427895 (lineage).
- Source: https://www.fmz.com/strategy/427895 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-26 16:23:53). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 13] x `slow` [50, 30]: **4 trials**; defaults 8 / 50 (the source's); profit-level EMA 50 fixed.

## Ambiguities resolved

- EMA 200 switch off by default. A same-bar close acts only on an open position. Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
