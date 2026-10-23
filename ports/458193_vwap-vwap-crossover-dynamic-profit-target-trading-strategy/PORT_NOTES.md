# #458193 VWAP交叉动态利润目标交易策略-VWAP-Crossover-Dynamic-Profit-Target-Trading-Strategy -> `fmz_458193_rolling_vwap14_cross_3pct_close_target_1h_reversal`

- FMZ source id: 458193 (lineage).
- Source: https://www.fmz.com/strategy/458193 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-07-30 17:01:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based targets from the fill |
| 2 | PASS | Rolling-VWAP crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 28] x `target` [0.03, 0.05]: **4 trials**.

## Ambiguities resolved

- Close-based targets from the fill, followed in the signals. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`none`
