# #452615 布林带RSI多均线趋势策略-Bollinger-Bands-RSI-Multi-MA-Trend-Strategy -> `fmz_452615_sma20_34_89_alignment_long`

- FMZ source id: 452615 (lineage).
- Source: https://www.fmz.com/strategy/452615 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-27 15:20:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA alignment state |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | The quantity rule stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`basis_len` [20, 10] x `mid_len` [34, 50] x `slow_len` [89, 144]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
