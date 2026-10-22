# #442813 埃利奥特波动叠加200日均线交易策略Elliott-Wave-Strategy-with-200-Day-Moving-Average -> `fmz_442813_five_bar_wave_pattern_sma200_reversal`

- FMZ source id: 442813 (lineage).
- Source: https://www.fmz.com/strategy/442813 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-26 10:49:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Lagged high / low pattern with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [200, 100]: **2 trials**.

## Ambiguities resolved

- Call order, one position at a time. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
