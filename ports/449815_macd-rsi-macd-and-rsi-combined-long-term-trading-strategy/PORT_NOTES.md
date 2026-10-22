# #449815 MACD与RSI结合的长线交易策略-MACD-and-RSI-Combined-Long-term-Trading-Strategy -> `fmz_449815_macd_cross_after_rsi_extreme_reversal`

- FMZ source id: 449815 (lineage).
- Source: https://www.fmz.com/strategy/449815 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 14:31:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | MACD crossings after RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `window` [10, 5]: **4 trials**; the RSI levels and the MACD lengths fixed.

## Ambiguities resolved

- Bracket armed only by repeated signals: pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
