# #442502 Bollinger Bands Consolidation Strategy -> `fmz_442502_atr_band_squeeze_ratchet_low_exit_long`

- FMZ source id: 442502 (lineage).
- Source: https://www.fmz.com/strategy/442502 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 13:43:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR / deviation squeeze; ratchet level tested on the low |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials** (one multiplier on both the deviation and the ATR, as the author aligns them).

## Ambiguities resolved

- Exit read at the close on the bar's low, filled at the next open. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
