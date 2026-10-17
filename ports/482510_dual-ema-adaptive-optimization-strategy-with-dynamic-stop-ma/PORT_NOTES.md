# #482510 双均线自适应优化策略与动态止盈止损系统-Dual-EMA-Adaptive-Optimization-Strategy-with-Dynamic-Stop-Management-System -> `fmz_482510_ema5_10_cross_pct_bracket`

- FMZ source id: 482510 (lineage).
- Source: https://www.fmz.com/strategy/482510 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 18:14:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | Two EMAs and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1, 2] x `tp_pct` [1, 2]: **4 trials**; defaults 1 / 1 (the source's); EMA 5 / 10 fixed.

## Ambiguities resolved

- The "AI optimisation" copies the inputs into the "best" values on every new net-profit high, so the bracket is
  the fixed inputs (it reads no performance into the levels).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
