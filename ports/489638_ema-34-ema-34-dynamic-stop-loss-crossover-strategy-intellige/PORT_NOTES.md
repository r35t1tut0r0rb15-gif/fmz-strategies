# #489638 EMA-34-动态止损交叉策略趋势跟踪与风险管理的智能结合-EMA-34-Dynamic-Stop-Loss-Crossover-Strategy-Intelligent-Combination-of-Trend-Following-and-Risk-Management -> `fmz_489638_ema34_cross_prev_low_stop_10r_long`

- FMZ source id: 489638 (lineage).
- Source: https://www.fmz.com/strategy/489638 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 11:39:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and range-checked exits at the next open. |
| 2 | PASS | An EMA and bar levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [10.0, 3.0] x `be_r` [3.0, 1.0]: **4 trials**; defaults 10 / 3 (the source's); EMA 34 fixed.

## Ambiguities resolved

- `low <= stop` / `high >= target` -> `strategy.close`: close-checked exit signals at the next open (rule 3).
- The script's inTrade flag is tracked apart from the position: the checks run on the signal bar too, where a close
  does nothing but clears inTrade; the entry still fills and stays unmanaged until the next cross, as written.
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
