# #490794 技术指标距离测量与MACD反转混合量化交易策略-Technical-Indicator-Distance-Measurement-and-MACD-Reversal-Hybrid-Quantitative-Trading-Strategy -> `fmz_490794_macd_cross_always_in`

- FMZ source id: 490794 (lineage).
- Source: https://www.fmz.com/strategy/490794 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-16 15:19:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 34]: **4 trials**; defaults 12 / 26 (the source's); signal 9 fixed.

## Ambiguities resolved

- The distance test is OR-ed with the bare MACD cross, so only the cross decides; the feature vector is not computed.
- Closes before entries on the same bar: stop-and-reverse. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
