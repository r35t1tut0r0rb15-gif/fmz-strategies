# #486571 SMA-ATR动态风险回报比趋势跟踪策略-SMA-ATR-Dynamic-Risk-Reward-Trend-Following-Strategy -> `fmz_486571_sma7_25_cross_bar_extreme_atr`

- FMZ source id: 486571 (lineage).
- Source: https://www.fmz.com/strategy/486571 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:45:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar (re-issue marked). |
| 2 | PASS | Moving averages and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.0, 1.5] x `rr` [2.0, 3.0]: **4 trials**; defaults 1 / 2 (the source's effective values); SMA 7 / 25 / 99
and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

As written, `strategy.exit` is re-issued every bar with the stop beyond the CURRENT bar's low / high and the target
from the current close (a moving bracket). The port fixes it at the signal bar, picked by the signal's side.

## Ambiguities resolved

- `riskRewardRatio = 6.0` inside the `if` declares a new local variable (`=`, not `:=`): the ratio is always 2.
  REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
