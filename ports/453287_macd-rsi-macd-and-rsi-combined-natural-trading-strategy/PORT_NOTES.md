# #453287 MACD和RSI结合的自然交易策略-MACD-and-RSI-Combined-Natural-Trading-Strategy -> `fmz_453287_macd_wma_rsi_gate_id_reversal`

- FMZ source id: 453287 (lineage).
- Source: https://www.fmz.com/strategy/453287 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 17:22:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD / WMA entries behind an RSI momentum gate |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `gate_len` [60, 30] x `wma_len` [20, 50]: **8 trials**; the MACD lengths and the RSI levels fixed.

## Ambiguities resolved

- Id-tracked closes; the gate is a 60-bar RSI change. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
