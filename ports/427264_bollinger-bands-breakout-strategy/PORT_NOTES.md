# #427264 Bollinger Bands Breakout Strategy -> `fmz_427264_bb_ots_long`

- FMZ source id: 427264 (lineage).
- Source: https://www.fmz.com/strategy/427264 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 16:06:56). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bands in standard deviations. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [20, 40] x `lb_offset` [2.0, 2.5] x `ub_offset` [2.0, 1.0]: **8 trials**; defaults 20 / 2.0 / 2.0 (the source's); stdev length 20 fixed.

## Ambiguities resolved

- The 2010-2030 testPeriod() is the author's backtest window: dropped.
- Long only, entries from flat. FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
