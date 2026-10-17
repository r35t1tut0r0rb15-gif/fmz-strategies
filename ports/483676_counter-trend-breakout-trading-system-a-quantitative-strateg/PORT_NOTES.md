# #483676 逆势突破交易系统基于多日价格模式与波动率过滤的量化策略-Counter-Trend-Breakout-Trading-System-A-Quantitative-Strategy-Based-on-Multi-Day-Price-Patterns-and-Volatility-Filtering -> `fmz_483676_three_red_days_atr_filter_long`

- FMZ source id: 483676 (lineage).
- Source: https://www.fmz.com/strategy/483676 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-25 10:49:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle colours and ATR relative to its own mean. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; initial capital quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_duration` [22, 11] x `use_green_exit` [True, False]: **4 trials**; defaults 22 / True (the source's); ATR 12 and
its 30-day mean fixed.

## Ambiguities resolved

- `atr_entry` is true while ATR or its mean is na (the warm-up), as written.
- The duration counts bars from the entry-signal bar (`entryBarIndex`); exits act at the next open; entries only from
  flat, again from the bar after an exit signal.
- Daily bars are broker days stamped with their first minute (as #430984). Long only: opposite entries cannot occur.
  FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
