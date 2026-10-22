# #442921 Dual Moving Average Crossover Strategy -> `fmz_442921_bmsb_sma20_ema21_cross_reversal`

- FMZ source id: 442921 (lineage).
- Source: https://www.fmz.com/strategy/442921 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 13:51:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA / EMA band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [20, 50] x `ema_length` [21, 50]: **4 trials**.

## Ambiguities resolved

- Later short wins a tie. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
