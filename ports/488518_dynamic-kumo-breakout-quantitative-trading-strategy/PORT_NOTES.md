# #488518 Dynamic Kumo Breakout Quantitative Trading Strategy -> `fmz_488518_kumo_top_breakout_long_sma14_28_cross_short_reversal`

- FMZ source id: 488518 (lineage).
- Source: https://www.fmz.com/strategy/488518 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 15:16:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku cloud breakouts with an SMA-cross short side |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lenKijun` [26, 20] x `lenSenkou` [52, 40]: **4 trials**; Tenkan 9, SMA 14 / 28.

## Ambiguities resolved

- The undisplaced cloud and unused exit are as written. REVERSAL INTENDED. FREQ = "1h". MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
