# #436645 Quantitative Reversal Index Strategy Integrating Dual Trend Signals -> `fmz_436645_reversal123_negative_volume_index_combo_1m_reversal`

- FMZ source id: 436645 (lineage).
- Source: https://www.fmz.com/strategy/436645 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 15:47:36). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and negative-volume-index states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 100] x `length` [14, 9]: **4 trials**; K smoothing 1, D 3, level 50.

## Ambiguities resolved

- Volume = broker tick volume (NVI). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`
