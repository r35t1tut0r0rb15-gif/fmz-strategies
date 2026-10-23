# #435975 The Relative Volume Indicator Strategy -> `fmz_435975_rsi_pop_relative_volume_daily_reversal`

- FMZ source id: 435975 (lineage).
- Source: https://www.fmz.com/strategy/435975 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 15:12:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI breakouts on relative-volume spikes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): margin_long 100, margin_short 100, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rvol_threshold` [1.5, 2.0] x `rsi_len` [14, 7]: **4 trials**; RSI 70 / 35, exits 69 / 35, RVOL 14.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
