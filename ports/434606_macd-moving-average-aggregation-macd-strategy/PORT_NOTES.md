# #434606 移动平均线聚合MACD策略Moving-Average-Aggregation-MACD-Strategy -> `fmz_434606_five_ma_136_slope_agreement_reversal`

- FMZ source id: 434606 (lineage).
- Source: https://www.fmz.com/strategy/434606 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-07 17:35:41). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average slope agreement |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [8, 20] x `len2` [144, 100]: **4 trials**; length = len2 - len1.

## Ambiguities resolved

- All five averages share len2 - len1. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "bar_size_pending".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_slope"`.

## Marks

`bar_size_pending`
