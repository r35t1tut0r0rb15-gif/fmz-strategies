# #427482 Logarithmic Moving Average Convergence Divergence Strategy -> `fmz_427482_log_macd`

- FMZ source id: 427482 (lineage).
- Source: https://www.fmz.com/strategy/427482 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-21 15:38:05). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Log ratio of averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 50] x `sma_source` [False, True]: **8 trials**; defaults 12 / 26 / False (the source's); signal 9 (EMA) fixed.

## Ambiguities resolved

- Broker-day bars. REVERSAL INTENDED. FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
