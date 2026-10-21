# #436984 Dynamic Trailing Stop Loss Strategy -> `fmz_436984_ema_cross_close_trail_long`

- FMZ source id: 436984 (lineage).
- Source: https://www.fmz.com/strategy/436984 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 10:42:27). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; trail and stop tested on closes |
| 2 | PASS | Percent distances from the buy close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND363797. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.003, 0.01] x `stop_pct` [0.035, 0.02]: **4 trials**; arm 0.65 % and EMA 14 / 22 / 200 fixed.

## Ambiguities resolved

- Close-tested trail as an exit signal; percents kept; signals alternate. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
