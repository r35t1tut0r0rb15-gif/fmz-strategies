# #484109 动态风险管理的快速均线交叉动量捕捉策略-Dynamic-Risk-Managed-Rapid-SMA-Crossover-Momentum-Capture-Strategy -> `fmz_484109_momentum_state_atr_bracket`

- FMZ source id: 484109 (lineage).
- Source: https://www.fmz.com/strategy/484109 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 10:29:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, oscillators and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.2, 2.0] x `tp_mult` [2.5, 4.0]: **4 trials**; defaults 1.2 / 2.5 (the source's); SMA 5 / 20, RSI 10
(45 / 55), MACD 5 / 13 / 3 and ATR 10 fixed.

## Trailing stop (mark `trailing_stop_pending`)

Every condition bar while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- Every condition bar is an entry. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Two-day bars are
  blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
