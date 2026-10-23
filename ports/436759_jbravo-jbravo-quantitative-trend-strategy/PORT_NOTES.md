# #436759 JBravo量化趋势策略JBravo-Quantitative-Trend-Strategy -> `fmz_436759_daily_hlc3_vs_ema20_state_reversal`

- FMZ source id: 436759 (lineage).
- Source: https://www.fmz.com/strategy/436759 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 14:53:07). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Typical price against an EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50]: **2 trials**.

## Ambiguities resolved

- Daily VWAP = the bar's hlc3 (volume drops out). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_state"`.

## Marks

`none`
