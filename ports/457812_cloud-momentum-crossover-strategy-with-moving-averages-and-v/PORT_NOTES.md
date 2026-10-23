# #457812 Cloud Momentum Crossover Strategy with Moving Averages and Volume Confirmation -> `fmz_457812_sma_cloud_span_a_two_sma_volume_rise_reversal`

- FMZ source id: 457812 (lineage).
- Source: https://www.fmz.com/strategy/457812 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-26 17:38:28). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close above / below an undisplaced cloud line and two SMAs on rising volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [20, 10] x `vol_pct` [20.0, 50.0]: **4 trials**; conversion 9, base 26, slow SMA 50.

## Ambiguities resolved

- Cloud lines as SMAs of hl2, undisplaced. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
