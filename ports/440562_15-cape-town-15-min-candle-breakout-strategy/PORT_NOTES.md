# #440562 坎普敦15分钟蜡烛突破策略Cape-Town-15-min-Candle-Breakout-Strategy -> `fmz_440562_cape_town_1400_candle_long`

- FMZ source id: 440562 (lineage).
- Source: https://www.fmz.com/strategy/440562 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 17:15:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colour at a fixed hour |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`utc_hour` [14, 13]: **2 trials**.

## Ambiguities resolved

- Hour read on the UTC bar open. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
