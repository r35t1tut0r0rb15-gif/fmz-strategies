# #431901 Dual Moving Average Crossover Persistent Uptrend Strategy -> `fmz_431901_ma_cross_angle_fade`

- FMZ source id: 431901 (lineage).
- Source: https://www.fmz.com/strategy/431901 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-13 10:47:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | PASS | SMA crosses, an ATR-scaled angle and percentage levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`angle` [7, 3] x `tp_sl` [1.0, 2.0]: **4 trials**; SMA 8 / 21, ATR 10, look-back 15 and BB 20 / 2 fixed; TP = SL.

## Ambiguities resolved

- Swapped entries as written; close-checked exits. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
