# #441178 基于Heikin-Ashi的超级趋势-trailing-stop损策略SuperTrend-Trailing-Stop-Strategy-Based-on-Heikin-Ashi -> `fmz_441178_ha_supertrend_pullback_cci_line_reversal`

- FMZ source id: 441178 (lineage).
- Source: https://www.fmz.com/strategy/441178 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-06 14:43:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C148). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Heikin-Ashi SuperTrend, CCI line and time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pd` [4, 10] x `factor` [2.0, 3.0]: **4 trials**; the CCI line, HMA / EMA and the exit hour fixed.

## Ambiguities resolved

- Same-timeframe securities; UTC exit hour. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
