# #481091 量化动量交易VWAP-MACD双指标趋势跟踪策略-Quantitative-Momentum-Trading-VWAP-MACD-Dual-Indicator-Trend-Following-Strategy -> `fmz_481091_macd_cross_session_vwap_side_exit_2h_reversal`

- FMZ source id: 481091 (lineage).
- Source: https://www.fmz.com/strategy/481091 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 14:45:43). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings on the session-VWAP side with VWAP exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; signal 9, session VWAP.

## Ambiguities resolved

- Session VWAP reset on the broker day. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`none`
