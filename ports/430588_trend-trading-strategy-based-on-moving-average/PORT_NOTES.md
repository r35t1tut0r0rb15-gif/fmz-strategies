# #430588 Trend Trading Strategy Based on Moving Average -> `fmz_430588_vwma400_hl2_rising5_long_quarterly_copy`

- FMZ source id: 430588 (lineage).
- Source: https://www.fmz.com/strategy/430588 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 15:53:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Long VWMA slope trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 1000, commission 0.1 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [400, 300] x `rise_len` [5, 3]: **4 trials**.

## Ambiguities resolved

- Twin of #430385. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_slope"`.

## Marks

`none`
