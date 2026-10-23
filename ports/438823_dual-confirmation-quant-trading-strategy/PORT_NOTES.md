# #438823 Dual Confirmation Quant Trading Strategy -> `fmz_438823_reversal123_percentage_volume_oscillator_combo_15m_reversal`

- FMZ source id: 438823 (lineage).
- Source: https://www.fmz.com/strategy/438823 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 15:21:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and volume-oscillator states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `pvo_signal` [9, 5]: **4 trials**; K smoothing 1, D 3, level 50, PVO 12 / 26.

## Ambiguities resolved

- PVO state sign as written (below the signal = +1). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`
