# #490794 技术指标距离测量与MACD反转混合量化交易策略-Technical-Indicator-Distance-Measurement-and-MACD-Reversal-Hybrid-Quantitative-Trading-Strategy -> `fmz_490794_macd_signal_cross_reversal`

- FMZ source id: 490794 (lineage).
- Source: https://www.fmz.com/strategy/490794 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-16 15:19:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD signal crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; signal 9.

## Ambiguities resolved

- The distance filter is absorbed by the OR, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
