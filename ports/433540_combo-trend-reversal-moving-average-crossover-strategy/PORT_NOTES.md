# #433540 Combo Trend Reversal Moving Average Crossover Strategy -> `fmz_433540_combo_123_williams_lines`

- FMZ source id: 433540 (lineage).
- Source: https://www.fmz.com/strategy/433540 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-28 13:47:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and average order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `l_len` [13, 21]: **4 trials**; the 123 smoothing / level, M / S lengths and the offsets fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
