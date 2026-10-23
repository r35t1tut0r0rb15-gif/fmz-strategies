# #482509 动态成交量均线趋势跟踪与HLCC4突破交易策略-Dynamic-Volume-Weighted-Moving-Average-Trend-Following-with-HLCC4-Breakout-Trading-Strategy -> `fmz_482509_vwma200_hlcc4_weekly_vwma50_filter_long_only`

- FMZ source id: 482509 (lineage).
- Source: https://www.fmz.com/strategy/482509 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 18:12:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly filter from completed weeks |
| 2 | PASS | VWMA 200 trend entries above a weekly VWMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wvma_len` [200, 100] x `weekly_len` [50, 20]: **4 trials**.

## Ambiguities resolved

- The exit is gated by the weekly filter too. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "vwma_trend"`.

## Marks

`none`
