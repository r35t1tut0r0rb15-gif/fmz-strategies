# #426617 Long Reversal Strategy Based on Ultimate Oscillator -> `fmz_426617_ultimate_oscillator_cross45_alligator_long_close_stop`

- FMZ source id: 426617 (lineage).
- Source: https://www.fmz.com/strategy/426617 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 17:32:53). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop |
| 2 | PASS | Ultimate Oscillator turns with an Alligator trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 10 % / (close x 3 %), 20 % of equity, pyramiding 2 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_line` [45.0, 35.0] x `exit_line` [70.0, 60.0]: **4 trials**; UO 5 / 10 / 15, stop 3 %.

## Ambiguities resolved

- position_size < 1 read as flat. VWAP unused. Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_threshold"`.

## Marks

`none`
