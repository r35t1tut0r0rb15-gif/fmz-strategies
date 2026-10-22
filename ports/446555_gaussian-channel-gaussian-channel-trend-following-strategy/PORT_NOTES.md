# #446555 Gaussian-Channel趋势追踪策略-Gaussian-Channel-Trend-Following-Strategy -> `fmz_446555_gaussian_channel_v2_upper_break_long`

- FMZ source id: 446555 (lineage).
- Source: https://www.fmz.com/strategy/446555 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 16:26:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the recursive filter uses past values only |
| 2 | PASS | Gaussian channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored; the commission and slippage are costs, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND446461. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`poles` [4, 2] x `period` [144, 72]: **4 trials**; the TR multiplier fixed.

## Ambiguities resolved

- Same rules as #446461 (rule 7). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
