# #442519 Breakthrough Callback Long Strategy -> `fmz_442519_bearish_outside_bar_low_stop_long`

- FMZ source id: 442519 (lineage).
- Source: https://www.fmz.com/strategy/442519 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-22 15:41:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry from signal-bar data |
| 2 | PASS | Outside-bar pattern |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders (the take-profit input only plots): **1 trial**, the source as written.

## Ambiguities resolved

- Stop at the signal bar's low, re-based on the fill; a repeat signal's move not followed. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
