# #427385 Ichimoku and MACD Trend Reversal Trading Strategy -> `fmz_427385_impeccable_weekly_open_macd`

- FMZ source id: 427385 (lineage).
- Source: https://www.fmz.com/strategy/427385 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-20 15:44:13). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly open only once the week completed. |
| 2 | PASS | Price comparisons, MACD crosses. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | qty 1 per order stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 20] x `macd_fast` [3, 12] x `macd_slow` [10, 26]: **8 trials**; defaults 9 / 3 / 10 (the source's); MACD signal 9, weekends off fixed. (The Kijun / Senkou inputs are never used.)

## Ambiguities resolved

- `strategy.order` nets units: an opposite signal flattens, never reverses (no one-bar reversal at all).
- Weekly open: completed broker weeks only (house rule, as #427188), then `[3]` daily bars.
- Weekend filter by the broker-day date (Saturday / Sunday sessions); end-of-day and Friday exits act only on intraday charts; ProfitTarget / StopLoss / ExitAfterBars are unused inputs.
- FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
