# #437501 MacD200日均线信号交叉交易策略MACD-200-Day-Moving-Average-Crossover-Trading-Strategy -> `fmz_437501_macd_side_sma200`

- FMZ source id: 437501 (lineage).
- Source: https://www.fmz.com/strategy/437501 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 11:50:56). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD side and SMA test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `ma_length` [200, 100]: **4 trials**; slow 26, signal 9 fixed.

## Ambiguities resolved

- State entries. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
