# #483514 动态供需区间中线反转策略-Dynamic-Supply-Demand-Zone-Midline-Reversal-Strategy -> `fmz_483514_midline_candle_reversal_range_bracket`

- FMZ source id: 483514 (lineage).
- Source: https://www.fmz.com/strategy/483514 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-24 16:00:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Rolling range extremes, a moving average and candle colours. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 100] x `midline_len` [20, 50]: **4 trials**; defaults 50 / 20 (the source's).

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held runs `close_all` and a new entry, re-storing the zones from the new bar. The port keeps
the entry's trade and bracket.

## Ambiguities resolved

- The stored supply / demand zones become fractions of the signal bar's close, picked by the signal's side, re-based
  on the fill; both are always positive under the candle conditions.
- `close_all` + the opposite entry: REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`trailing_stop_pending`
