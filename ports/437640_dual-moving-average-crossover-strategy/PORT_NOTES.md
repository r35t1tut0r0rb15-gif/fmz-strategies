# #437640 Dual Moving Average Crossover Strategy -> `fmz_437640_sma_cross_atr_stop`

- FMZ source id: 437640 (lineage).
- Source: https://www.fmz.com/strategy/437640 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-04 15:03:14). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | ATR stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `atr_mult` [4.0, 2.0]: **4 trials**; slow 100 and ATR 14 fixed.

## Ambiguities resolved

- ATR stop from the signal bar. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
