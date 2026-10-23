# #430551 动态RSI矩形Grid策略RSI-Box-Grid-Strategy -> `fmz_430551_rsi_anchored_vwma_box_line_cross_long`

- FMZ source id: 430551 (lineage).
- Source: https://www.fmz.com/strategy/430551 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-30 11:29:30). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI-anchored box line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (1 % of equity, pyramiding 33) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 21] x `oblvl` [70, 80]: **4 trials**; oversold 100 - oblvl.

## Ambiguities resolved

- One position (pyramiding commented out). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "grid_lines"`.

## Marks

`none`
