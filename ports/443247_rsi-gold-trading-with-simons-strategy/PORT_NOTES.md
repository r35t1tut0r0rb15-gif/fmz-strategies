# #443247 黄金复合移动平均线交叉RSI混入策略Gold-Trading-with-Simons-Strategy -> `fmz_443247_sma21_200_cross_engulfing_long_bracket`

- FMZ source id: 443247 (lineage).
- Source: https://www.fmz.com/strategy/443247 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-01 12:28:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed at entry; the short's wrong-side levels read as a close |
| 2 | PASS | SMA crossings with an engulfing bar |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length21` [21, 10] x `length200` [200, 100]: **4 trials**; the SMA 50, the RSI and the bracket fixed.

## Ambiguities resolved

- Long bracket fixed; the short closes after its first bar (wrong-side levels). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
