# #434711 基于SuperTrend和DEMA的趋势跟踪策略SuperTrend-and-DEMA-Based-Trend-Following-Strategy -> `fmz_434711_supertrend_ema200_flips`

- FMZ source id: 434711 (lineage).
- Source: https://www.fmz.com/strategy/434711 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-08 16:42:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands and an average side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `ema_len` [200, 100]: **4 trials**; ATR 10 fixed.

## Ambiguities resolved

- Same-bar entry beats the close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
