# #481365 Multi-Indicator-Trend-Following-Strategy-with-Dynamic-Risk-Management-多指标趋势跟踪策略与动态风险管理 -> `fmz_481365_ema20_50_cross_filters_reversal_bracket`

- FMZ source id: 481365 (lineage).
- Source: https://www.fmz.com/strategy/481365 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 15:05:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the bracket base, as written |
| 2 | PASS | EMA crossings with trend, momentum and band filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity and capital stored, not ported; commission not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [20, 10] x `ema_slow` [50, 100]: **4 trials**; EMA 200, RSI 14, BB 20, MACD 12 / 26 / 9; stop 2 %, R:R 1.5.

## Ambiguities resolved

- The bracket exists only on a reversal, and the short's levels are on the wrong side, as written.
- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
