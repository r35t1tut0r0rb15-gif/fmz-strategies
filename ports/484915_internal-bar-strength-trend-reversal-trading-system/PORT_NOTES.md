# #484915 内部价格强度趋势反转交易系统-Internal-Bar-Strength-Trend-Reversal-Trading-System -> `fmz_484915_ibs_reversal_time_exit`

- FMZ source id: 484915 (lineage).
- Source: https://www.fmz.com/strategy/484915 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-05 09:55:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-range ratios, an EMA and bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 50 % of equity and pyramiding quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ibs_entry` [0.09, 0.2] x `max_bars` [14, 28]: **4 trials**; defaults 0.09 / 14 (the source's); IBS exit 0.985, EMA 220
and the 0 % entry distance fixed.

## Ambiguities resolved

- Adds (pyramiding 2) are sizing: net position only (#490570); a same-side entry while held still moves
  `lastEntryPrice` and the duration clock, as written. The duration counts bars of the header chart.
- Closes act on the position at the bar's start (#430850); a short while long (when the distance rule allows it)
  reverses: REVERSAL INTENDED. The author's daily-bar notes do not override the 1-hour header: FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ibs_mean_reversion"`.

## Marks

`none`
