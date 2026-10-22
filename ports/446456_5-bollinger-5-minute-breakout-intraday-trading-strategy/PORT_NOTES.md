# #446456 布林5分钟突破日内交易策略-Bollinger-5-Minute-Breakout-Intraday-Trading-Strategy -> `fmz_446456_sma100_3sd_break_1sd_exit_daily_long`

- FMZ source id: 446456 (lineage).
- Source: https://www.fmz.com/strategy/446456 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 17:43:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Wide-band breakout with a lower-band exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult_upper` [3.0, 2.0] x `mult_lower` [1.0, 2.0]: **4 trials**; the length 100 fixed.

## Ambiguities resolved

- Session exit never fires on daily bars (same rules as #446438). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
