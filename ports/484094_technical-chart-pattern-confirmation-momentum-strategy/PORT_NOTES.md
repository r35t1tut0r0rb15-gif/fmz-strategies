# #484094 技术图形确认型多周期动量策略-Technical-Chart-Pattern-Confirmation-Momentum-Strategy -> `fmz_484094_chart_pattern_set_bracket`

- FMZ source id: 484094 (lineage).
- Source: https://www.fmz.com/strategy/484094 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:50:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Bar patterns and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.5] x `atr_len` [14, 7]: **4 trials**; defaults 1.5 / 14 (the source's); target 2 x the stop.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The pattern tests as written (the "head and shoulders" equals the double-top test and sits on the long side, as
  written). Both directions on one bar: the short wins. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  Daily bars are broker days; FREQ = "1D": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "chart_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
