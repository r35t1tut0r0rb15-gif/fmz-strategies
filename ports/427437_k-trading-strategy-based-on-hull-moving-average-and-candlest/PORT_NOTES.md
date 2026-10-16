# #427437 Trading Strategy Based on Hull Moving Average and Candlestick -> `fmz_427437_hma_vs_daily_open`

- FMZ source id: 427437 (lineage).
- Source: https://www.fmz.com/strategy/427437 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 10:31:58). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the daily open only once the day ended (lookahead_off). |
| 2 | PASS | Comparisons of the instrument's own prices. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission, slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [50, 25, 100]: **3 trials**; default 50 (the source's). Resolution "D" and source `open` fixed.

## Ambiguities resolved

- The daily open seen by each 2-hour bar is the last broker day that ended by the bar's close (as #427267).
- Closes are tested before entries (script order); one-bar reversals (REVERSAL INTENDED). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
