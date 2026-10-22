# #458178 Dynamic Position Dual Moving Average Crossover Strategy -> `fmz_458178_sma9_21_cross_open_vs_sma21_switch_reversal`

- FMZ source id: 458178 (lineage).
- Source: https://www.fmz.com/strategy/458178 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 16:04:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with open-price switches |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash order size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`shortlen` [9, 5] x `longlen` [21, 50]: **4 trials**.

## Ambiguities resolved

- Call order followed (later call wins). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
