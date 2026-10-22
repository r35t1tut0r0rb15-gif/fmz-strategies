# #478748 多维度趋势判断与ATR动态止盈止损策略-Multi-Dimensional-Trend-Analysis-with-ATR-Based-Dynamic-Stop-Management-Strategy -> `fmz_478748_sma_cloud_macd_ema200_state_reversal`

- FMZ source id: 478748 (lineage).
- Source: https://www.fmz.com/strategy/478748 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 16:39:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar exit bracket described (pending) |
| 2 | PASS | SMA-cloud, MACD and EMA 200 trend states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conv_len` [9, 20] x `base_len` [26, 50]: **4 trials**; span B 52, MACD 12 / 26 / 9, EMA 200; the exit bracket pending.

## Ambiguities resolved

- SMA-of-high / low lines, as written. Exit bracket from the latest close kept pending (trailing_stop_pending).
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`trailing_stop_pending`
