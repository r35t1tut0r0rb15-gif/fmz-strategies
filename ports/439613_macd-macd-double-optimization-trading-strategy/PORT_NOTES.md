# #439613 MACD双向优化交易策略MACD-Double-Optimization-Trading-Strategy -> `fmz_439613_macd_long_short_zero_cross_short_bracket`

- FMZ source id: 439613 (lineage).
- Source: https://www.fmz.com/strategy/439613 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 11:10:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short bracket fixed from the fill |
| 2 | PASS | MACD zero crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_long` [13, 12] x `slow_long` [19, 26]: **4 trials**; the short MACD 11 / 20 with delay 1 and its 21 % / 20 % bracket fixed.

## Ambiguities resolved

- Short-only bracket from the fill; long blocks short on one bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
