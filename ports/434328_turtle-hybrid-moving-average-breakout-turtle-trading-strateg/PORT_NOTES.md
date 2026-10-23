# #434328 混合均线突破Turtle交易策略Hybrid-Moving-Average-Breakout-Turtle-Trading-Strategy -> `fmz_434328_turtle_6bar_breakout_daily_reversal`

- FMZ source id: 434328 (lineage).
- Source: https://www.fmz.com/strategy/434328 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 15:01:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Short-period channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): default qty 10, pyramiding 0, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`turtle_speed` [6, 20]: **2 trials**.

## Ambiguities resolved

- Plain candles (the author's Heikin-Ashi note not applied). Later call wins on a two-way bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
