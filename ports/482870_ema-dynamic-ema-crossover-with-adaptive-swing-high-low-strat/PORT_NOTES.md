# #482870 动态-EMA-交叉摆动高低点自适应策略-Dynamic-EMA-Crossover-with-Adaptive-Swing-High-Low-Strategy -> `fmz_482870_ema22_cross_swing_bracket_1d`

- FMZ source id: 482870 (lineage).
- Source: https://www.fmz.com/strategy/482870 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:32:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | An EMA and rolling swing extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND482870 (2 members, best partner #483066, Jaccard 0.746). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [22, 50] x `swing_len` [14, 20]: **4 trials**; defaults 22 / 14 (the source's).

## Trailing stop (mark `trailing_stop_pending`)

Every close below EMA 22 is a sell signal, so a held short has its stop and target re-placed each bar. The port keeps
the entry's bracket.

## Ambiguities resolved

- The swing levels become fractions of the signal close by side, re-based on the fill; a signal whose stop or target
  is not beyond the close emits no entry (as #490798). Same logic as its ND partner #483066 (L21) with EMA 22.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
