# #486571 SMA-ATR动态风险回报比趋势跟踪策略-SMA-ATR-Dynamic-Risk-Reward-Trend-Following-Strategy -> `fmz_486571_sma7_25_cross_sma99_side_reversal`

- FMZ source id: 486571 (lineage).
- Source: https://www.fmz.com/strategy/486571 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:45:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | SMA crossings with a long-SMA side filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 10] x `slow` [25, 50]: **4 trials**; SMA 99.

## Ambiguities resolved

- The per-bar bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
