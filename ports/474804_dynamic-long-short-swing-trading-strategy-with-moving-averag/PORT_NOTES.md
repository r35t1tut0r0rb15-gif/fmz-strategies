# #474804 Dynamic Long Short Swing Trading Strategy with Moving Average Crossover Signal System -> `fmz_474804_ema20_sma50_cross_rsi_atr_bracket_from_replaced_avg`

- FMZ source id: 474804 (lineage).
- Source: https://www.fmz.com/strategy/474804 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 11:11:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the bracket base, as written |
| 2 | PASS | EMA / SMA crossings with an RSI filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size from a typed capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [20, 10] x `long_len` [50, 100]: **4 trials**; ATR multiples fixed.

## Ambiguities resolved

- Bracket from the replaced position's price (na from flat), as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
