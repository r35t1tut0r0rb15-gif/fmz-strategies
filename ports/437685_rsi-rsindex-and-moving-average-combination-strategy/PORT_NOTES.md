# #437685 阻力与支撑带动的拉里金叉RSI策略RSIndex-and-Moving-Average-Combination-Strategy -> `fmz_437685_connors_rsi2_sma_exits`

- FMZ source id: 437685 (lineage).
- Source: https://www.fmz.com/strategy/437685 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-04 17:46:07). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and SMA comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG437685. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_len` [120, 200] x `exit_len` [5, 10]: **4 trials**; RSI 2 and its 1 / 10 / 90 / 98 bounds fixed.

## Ambiguities resolved

- Call-order fills. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
