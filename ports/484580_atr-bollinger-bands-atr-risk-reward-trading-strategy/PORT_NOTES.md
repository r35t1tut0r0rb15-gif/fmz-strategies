# #484580 布林带ATR风险回报比交易策略-Bollinger-Bands-ATR-Risk-Reward-Trading-Strategy -> `fmz_484580_outside_bollinger_atr_bracket`

- FMZ source id: 484580 (lineage).
- Source: https://www.fmz.com/strategy/484580 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 09:56:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Bands and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_dev` [2.0, 2.5] x `rr` [2.0, 1.5]: **4 trials**; defaults 2 / 2 (the source's); BB 20, ATR 14 and the 2 ATR stop
fixed.

## Trailing stop (mark `trailing_stop_pending`)

Every bar outside the band while held re-places the stop and target from the new bar (its `strategy.exit`). The port
keeps the entry's bracket.

## Ambiguities resolved

- Every condition bar is an entry. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars are broker
  days; FREQ = "1D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
