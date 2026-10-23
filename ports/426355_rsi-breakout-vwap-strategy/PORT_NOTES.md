# #426355 RSI Breakout VWAP Strategy -> `fmz_426355_rsi20_daily_vwap_band_cross_late_leave_reversal`

- FMZ source id: 426355 (lineage).
- Source: https://www.fmz.com/strategy/426355 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 14:13:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI band crossings with a timed exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Bet 0.1 coin, pyramiding 3 and commission 0.04 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 14] x `lateleave` [28, 14]: **4 trials**; 30 / 85.

## Ambiguities resolved

- VWAP of one daily bar = its close (no volume effect). Pyramiding adds not ported. REVERSAL INTENDED.
- FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
