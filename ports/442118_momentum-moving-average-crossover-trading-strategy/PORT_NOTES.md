# #442118 Momentum Moving Average Crossover Trading Strategy -> `fmz_442118_macd_hist_signal_side_reversal`

- FMZ source id: 442118 (lineage).
- Source: https://www.fmz.com/strategy/442118 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-19 14:53:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram and signal side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; signal 9 and EMA 5 fixed.

## Ambiguities resolved

- Entries reduce as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
