# #484583 布林带精准风险优化策略-Bollinger-Precision-Risk-Optimization-Strategy -> `fmz_484583_bb_reentry_rsi_pct_bracket`

- FMZ source id: 484583 (lineage).
- Source: https://www.fmz.com/strategy/484583 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 10:07:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal close (re-placement marked). |
| 2 | PASS | Bands, an oscillator and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [4.0, 2.0] x `tp_pct` [8.0, 4.0]: **4 trials**; defaults 4 / 8 (the source's); BB 20 x 2 and RSI 14 (30 / 70)
fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new close (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The close after each entry is the reversal: REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
