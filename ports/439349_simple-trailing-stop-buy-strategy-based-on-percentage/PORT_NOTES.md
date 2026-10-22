# #439349 Simple Trailing Stop Buy Strategy Based on Percentage -> `fmz_439349_rma_envelope_breakout_long`

- FMZ source id: 439349 (lineage).
- Source: https://www.fmz.com/strategy/439349 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-19 14:30:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C120). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Percent envelope crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`offset` [1.5, 3.0] x `buyoffset` [1.9, 3.0]: **4 trials**; RMA 6 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
