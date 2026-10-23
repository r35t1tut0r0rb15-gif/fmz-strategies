# #437780 Reversal Tracking Strategy with Double Mechanisms -> `fmz_437780_reversal123_positive_volume_index_combo_reversal`

- FMZ source id: 437780 (lineage).
- Source: https://www.fmz.com/strategy/437780 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 15:09:19). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and positive-volume-index states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [255, 100] x `length` [14, 9]: **4 trials**; K smoothing 1, D 3, level 50.

## Ambiguities resolved

- Volume = broker tick volume (PVI). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`
