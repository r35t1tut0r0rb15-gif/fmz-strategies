# #436614 Trend Tracking Strategy Based on Dynamic Pivot Bands -> `fmz_436614_pivot_atr_band_reversal`

- FMZ source id: 436614 (lineage).
- Source: https://www.fmz.com/strategy/436614 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 11:57:20). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C93). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | REVIEW | Tick stop -> ATR multiple; pivot via a deviation test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed size, the tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434486. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrmult` [3.0, 2.0] x `k_atr` [0.07, 1.0]: **4 trials**; pivot length 24, ATR 22 and the trend index settings fixed.

## Ambiguities resolved

- Pivot read as an unchanged 24-bar extreme; tick stop -> ATR multiple; entry with an exit true on its own bar dropped. Entries from flat.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
