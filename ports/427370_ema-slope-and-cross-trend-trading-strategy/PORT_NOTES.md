# #427370 EMA Slope and Cross Trend Trading Strategy -> `fmz_427370_chartart_ema_slope_cross_fade`

- FMZ source id: 427370 (lineage).
- Source: https://www.fmz.com/strategy/427370 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-20 14:32:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths, signs of changes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [2, 3] x `ma2` [4, 8] x `ma3` [20, 50]: **8 trials**; defaults 2 / 4 / 20 (the source's).

## Ambiguities resolved

- Contrarian as written (a cross down buys).
- REVERSAL INTENDED. FREQ = "6h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
