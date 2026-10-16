# #430840 Trend Line Trading Strategy -> `fmz_430840_trendline_breaks_reversed`

- FMZ source id: 430840 (lineage).
- Source: https://www.fmz.com/strategy/430840 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 14:14:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the shared-id bracket read as written (shorts only), levels from the signal bar. |
| 2 | PASS | Pivot trendlines, ATR multiples and a reward ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored; the stop options quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`leftbars` [100, 50] x `rightbars` [15, 10]: **4 trials**; ATR 14 x 4, 2 R fixed; reverse on as default.

## Ambiguities resolved

- Reverse trades (default): breaks entered against their direction. Shared exit id: shorts only bracketed.
- Stop levels from the signal bar (approximation). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`coarse_bar_stop`
