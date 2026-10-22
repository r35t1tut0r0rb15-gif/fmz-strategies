# #478743 Adaptive Trend Following and Multi Confirmation Trading Strategy -> `fmz_478743_coral14_donchian20_trend_agree_reversal`

- FMZ source id: 478743 (lineage).
- Source: https://www.fmz.com/strategy/478743 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:29:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Coral and Donchian trend agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dlen` [20, 55] x `coral_period` [14, 30]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
