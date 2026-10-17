# #431668 RSI策略的回测与优化Backtesting-and-Optimization-of-RSI-Strategy -> `fmz_431668_rsi_extremes_loss_cooldown`

- FMZ source id: 431668 (lineage).
- Source: https://www.fmz.com/strategy/431668 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-10 11:59:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | RSI levels, percentage exits and a bar-count cooldown |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 50000 USDT per order stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_line` [20, 30] x `cooldown` [24, 8]: **4 trials**; RSI 14, exits 70 / 30, stop 3 % and target 1 % fixed.

## Ambiguities resolved

- Bracket from openPrice re-based on the fill; the cooldown from the house fills. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
