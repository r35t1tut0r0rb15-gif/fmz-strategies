# #483040 Multi Period Donchian Channel Trend Following and Divergence Trading Strategy -> `fmz_483040_donchian20_trend_state_reversal`

- FMZ source id: 483040 (lineage).
- Source: https://www.fmz.com/strategy/483040 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:38:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Donchian channel trend state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dlen` [20, 40, 10]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
