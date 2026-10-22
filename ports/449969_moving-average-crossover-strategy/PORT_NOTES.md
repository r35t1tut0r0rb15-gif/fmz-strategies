# #449969 Moving Average Crossover Strategy -> `fmz_449969_sma5_20_cross_four_bar_side_tick_target_reversal`

- FMZ source id: 449969 (lineage).
- Source: https://www.fmz.com/strategy/449969 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-30 17:33:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed on the signal bar |
| 2 | PASS | SMA crossings with a four-bar side filter, tick target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick target quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.1, 1.0] x `slow` [20, 50]: **4 trials**; the SMA 5 and the four-bar filter fixed.

## Ambiguities resolved

- Tick target as 0.1 ATR(14). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
