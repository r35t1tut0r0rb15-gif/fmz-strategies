# #473121 基于ATR波动率和均线的自适应趋势跟踪退出策略-ATR-Volatility-and-Moving-Average-Based-Adaptive-Trend-Following-Exit-Strategy -> `fmz_473121_close_cross_sma50_bands_never_hit_long`

- FMZ source id: 473121 (lineage).
- Source: https://www.fmz.com/strategy/473121 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:07:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA cross-ups (the exits never hold, as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [50, 20]: **2 trials**; the ATR bands never act.

## Ambiguities resolved

- Exit tests can never hold (as written). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
