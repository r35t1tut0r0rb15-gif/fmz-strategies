# #473137 Multi Period Moving Average Crossover with Volume Analysis System -> `fmz_473137_ema9_21_cross_volume_reversal`

- FMZ source id: 473137 (lineage).
- Source: https://www.fmz.com/strategy/473137 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 15:08:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 9 / 21 crossings on above-average volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [21, 26]: **4 trials**; volume SMA 20.

## Ambiguities resolved

- Default EMA type only. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
