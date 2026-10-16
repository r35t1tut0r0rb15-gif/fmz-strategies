# #427388 Buying Strategy Based on Historical High Breakout -> `fmz_427388_ath_200_breakout_long`

- FMZ source id: 427388 (lineage).
- Source: https://www.fmz.com/strategy/427388 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-20 15:53:26). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | qty 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars` [200, 100, 400] x `range_ema` [90, 200]: **6 trials**; defaults 200 / 90 (the source's).

## Ambiguities resolved

- The breakout level excludes the current bar. The EMA default 90 is below its input's minval; the default runs.
- Long only. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
