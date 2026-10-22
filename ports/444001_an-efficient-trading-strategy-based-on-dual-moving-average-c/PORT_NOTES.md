# #444001 An Efficient Trading Strategy Based on Dual Moving Average Crossover and Stop Loss -> `fmz_444001_sma10_20_cross_pct_stop_reversal`

- FMZ source id: 444001 (lineage).
- Source: https://www.fmz.com/strategy/444001 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 14:55:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND444001. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [0.02, 0.05] x `slow` [20, 50]: **4 trials**; the SMA 10 fixed.

## Ambiguities resolved

- Stop as a fixed fraction of the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
