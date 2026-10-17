# #482242 三段趋势突破与动量跟踪策略-Trinity-Bar-Based-Trend-Breakthrough-and-Momentum-Tracking-Strategy -> `fmz_482242_trinity_bar_thirds_always_in`

- FMZ source id: 482242 (lineage).
- Source: https://www.fmz.com/strategy/482242 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-17 10:53:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Thirds of each bar's range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | `ND482242` with #482428 (Jaccard 0.770, similar, not a duplicate). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`GRID = {}`: **1 trial**. The pattern has no parameter.

## Ambiguities resolved

- A zero-range bar meets both patterns: neither is taken. REVERSAL INTENDED (always in). FREQ = "1h".
- #482428 (L36) adds a previous-bar trailing stop on daily bars.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
