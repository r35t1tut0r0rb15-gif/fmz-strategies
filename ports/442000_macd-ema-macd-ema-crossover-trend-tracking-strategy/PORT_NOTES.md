# #442000 MACD-EMA黄金交叉趋势追踪策略MACD-EMA-Crossover-Trend-Tracking-Strategy -> `fmz_442000_macd_cross_ltf_ema206_swing_bracket`

- FMZ source id: 442000 (lineage).
- Source: https://www.fmz.com/strategy/442000 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-18 15:17:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from signal-bar data |
| 2 | PASS | Lower-timeframe EMA, MACD crossings and swing bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [206, 100] x `profit_long` [1.9, 1.0]: **4 trials**; the short factor, lookbacks and MACD lengths fixed.

## Ambiguities resolved

- 15-minute EMA from the hour's last 15-minute bar; swing stop from the signal bar. Opposite entries cannot occur (entries only from flat). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
