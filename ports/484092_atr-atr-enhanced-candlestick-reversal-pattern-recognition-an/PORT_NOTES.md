# #484092 ATR增强型蜡烛反转模式识别与风险管理策略-ATR-Enhanced-Candlestick-Reversal-Pattern-Recognition-and-Risk-Management-Strategy -> `fmz_484092_wide_hammer_star_bracket`

- FMZ source id: 484092 (lineage).
- Source: https://www.fmz.com/strategy/484092 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:48:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar (re-issue marked). |
| 2 | PASS | Candle proportions and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_atr` [1.5, 1.0] x `tp_atr` [2.5, 4.0]: **4 trials**; defaults 1.5 / 2.5 (the source's); ATR 14 and the 1.5 ATR
stop buffer fixed.

## Trailing stop (mark `trailing_stop_pending`)

As written, both exits are re-issued every bar with the stop beyond the CURRENT bar's low / high and the target from
the current close (a moving bracket). The port fixes it at the signal bar, picked by the signal's side.

## Ambiguities resolved

- `crossover(close, open)`: green now and not green on the previous bar. REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). Daily bars are broker days; FREQ = "1D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
