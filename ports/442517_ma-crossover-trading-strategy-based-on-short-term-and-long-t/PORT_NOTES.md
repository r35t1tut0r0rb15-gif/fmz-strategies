# #442517 MA Crossover Trading Strategy Based on Short term and Long term Moving Average Crossovers -> `fmz_442517_sma34_89_cross_three_bar_exit`

- FMZ source id: 442517 (lineage).
- Source: https://www.fmz.com/strategy/442517 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 15:36:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a bar-count exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`exit_candles` [3, 6] x `long_length` [89, 200]: **4 trials**; the SMA 34 fixed.

## Ambiguities resolved

- Bar-count exit from the latest crossing (exit at open). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
