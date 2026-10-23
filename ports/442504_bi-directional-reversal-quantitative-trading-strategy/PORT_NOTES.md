# #442504 Bi directional Reversal Quantitative Trading Strategy -> `fmz_442504_reversal123_volume_sma_combo_reversal`

- FMZ source id: 442504 (lineage).
- Source: https://www.fmz.com/strategy/442504 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 13:46:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and volume states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `vol_len` [40, 20]: **4 trials**; K smoothing 1, D 3, level 50.

## Ambiguities resolved

- Volume state sign as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`
