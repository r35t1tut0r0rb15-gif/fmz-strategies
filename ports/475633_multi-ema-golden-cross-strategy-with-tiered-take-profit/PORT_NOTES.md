# #475633 Multi EMA Golden Cross Strategy with Tiered Take Profit -> `fmz_475633_ema25_50_100_stack_cross_1r_close_target_long`

- FMZ source id: 475633 (lineage).
- Source: https://www.fmz.com/strategy/475633 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-20 16:54:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend EMA crossings with a 1 R close target and an EMA 100 exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed qty 0.5 per id stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 10] x `tp_mult1` [1.0, 2.0]: **4 trials**; the EMA lengths constants.

## Ambiguities resolved

- Only Buy1 fills (pyramiding 1); Buy2's stop never acts. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
