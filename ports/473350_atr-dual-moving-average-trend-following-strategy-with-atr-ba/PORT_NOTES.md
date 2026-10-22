# #473350 双均线趋势跟踪与ATR风控自适应交易策略-Dual-Moving-Average-Trend-Following-Strategy-with-ATR-Based-Risk-Management-System -> `fmz_473350_sma21_49_cross_long_tp_pending`

- FMZ source id: 473350 (lineage).
- Source: https://www.fmz.com/strategy/473350 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 14:56:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA cross-ups; per-bar limit described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 10] x `slow` [49, 100]: **4 trials**; Strategy 1 (default); the per-bar limit pending.

## Ambiguities resolved

- strategy.opentrades.size(strategy.opentrades - 1) when flat (trade -1) read as flat; if it is na the source never trades. Strategy 2 not ported. Per-bar limit pending. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
