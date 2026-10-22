# #440871 Bollinger Bands and Moving Averages Combination Strategy -> `fmz_440871_band_breakout_on_golden_cross`

- FMZ source id: 440871 (lineage).
- Source: https://www.fmz.com/strategy/440871 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 17:47:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakout with an SMA cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_length` [50, 20] x `ma2_length` [200, 100]: **4 trials**; BB 20 / 2 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
