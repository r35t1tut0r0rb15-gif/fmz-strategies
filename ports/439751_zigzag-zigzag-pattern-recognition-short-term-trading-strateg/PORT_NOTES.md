# #439751 基于ZigZag的多种形态识别短线交易策略ZigZag-Pattern-Recognition-Short-term-Trading-Strategy -> `fmz_439751_zigzag_harmonic_patterns_fib_window`

- FMZ source id: 439751 (lineage).
- Source: https://www.fmz.com/strategy/439751 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 15:09:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lower-time-frame zigzag from its last bar |
| 2 | PASS | Zigzag ratios and Fibonacci levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The trade size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND365711. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ew_rate` [0.382, 0.5] x `tp_rate` [0.618, 1.0]: **4 trials**; stop rate -0.618 and the pattern boxes fixed.

## Ambiguities resolved

- 1-hour zigzag read from the last 1-hour bar of each 2-hour bar. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
