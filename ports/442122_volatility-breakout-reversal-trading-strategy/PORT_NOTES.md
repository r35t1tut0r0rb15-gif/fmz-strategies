# #442122 Volatility Breakout Reversal Trading Strategy -> `fmz_442122_wilder_volatility_system_sar_reversal`

- FMZ source id: 442122 (lineage).
- Source: https://www.fmz.com/strategy/442122 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-19 15:12:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR stop-and-reverse levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length` [9, 14] x `arc_factor` [1.8, 2.8]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
