# #468308 Crossover Moving Average with Smoothed Candlestick Momentum Strategy -> `fmz_468308_wickless_heikin_ashi_ema10_30_trend_from_flat`

- FMZ source id: 468308 (lineage).
- Source: https://www.fmz.com/strategy/468308 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 14:54:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Wickless Heikin Ashi candles in an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [30, 50]: **4 trials**.

## Ambiguities resolved

- Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
