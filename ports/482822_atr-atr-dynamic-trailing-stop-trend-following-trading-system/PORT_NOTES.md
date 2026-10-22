# #482822 ATR动态追踪止损的趋势跟踪交易系统-ATR-Dynamic-Trailing-Stop-Trend-Following-Trading-System -> `fmz_482822_ut_bot1_1_atr200_ema50_side_reversal`

- FMZ source id: 482822 (lineage).
- Source: https://www.fmz.com/strategy/482822 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:53:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ROI stop ladder pending |
| 2 | PASS | ATR trailing-line crossings with an EMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key_value` [1.1, 2.0] x `atr_period` [200, 100]: **4 trials**; EMA 50.

## Ambiguities resolved

- The ROI stop ladder is pending (not ported); the two closes naming never-entered ids close nothing, as written.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`trailing_stop_pending`
