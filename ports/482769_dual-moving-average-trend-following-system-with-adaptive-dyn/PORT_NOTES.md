# #482769 双均线趋势跟踪交易系统与自适应动态过滤策略-Dual-Moving-Average-Trend-Following-System-with-Adaptive-Dynamic-Filtering-Strategy -> `fmz_482769_sma100_200_upclose_wpr_quiet_bar_long`

- FMZ source id: 482769 (lineage).
- Source: https://www.fmz.com/strategy/482769 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | SMAs, Williams %R and a percentage range filter; the 1.8 %-of-price branch is inert and dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [100, 50] x `run_up` [0.5, 1.0]: **4 trials**; defaults 100 / 0.5 (the source's); the SMA 200 of it and
%R 14 fixed.

## Ambiguities resolved

- `a and b or c` is `(a and b) or c` in Pine. The `c` branch needs `close < previousdayclose * .018` (1.8 % of the
  daily close), never true: dropped as inert (as #492009), with the HMA, EMA-stack and daily request only it uses.
- `xEMA` is an SMA 200 of the SMA 100 (as written). Day high / low and %R lines only feed drawings.
- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- Long only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
