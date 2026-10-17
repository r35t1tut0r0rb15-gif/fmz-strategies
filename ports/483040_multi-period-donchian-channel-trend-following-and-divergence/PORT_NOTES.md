# #483040 多重周期唐奇安指标趋势跟踪与背离交易策略-Multi-Period-Donchian-Channel-Trend-Following-and-Divergence-Trading-Strategy -> `fmz_483040_donchian_trend_state_reversal_1d`

- FMZ source id: 483040 (lineage).
- Source: https://www.fmz.com/strategy/483040 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:38:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Donchian channels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dlen` [20, 40]: **2 trials**; default 20 (the source's).

## Ambiguities resolved

- The ribbon's other lengths only colour plots. Every bar in a trend is an entry signal: stop-and-reverse on trend
  changes. REVERSAL INTENDED; no exits or stops.
- Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
