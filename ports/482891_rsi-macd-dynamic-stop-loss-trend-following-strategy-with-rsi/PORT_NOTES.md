# #482891 使用RSI和MACD双重过滤的动态止损趋势跟踪策略-Dynamic-Stop-Loss-Trend-Following-Strategy-with-RSI-and-MACD-Dual-Filtering -> `fmz_482891_macd_cross_rsi_close_stop_reversal`

- FMZ source id: 482891 (lineage).
- Source: https://www.fmz.com/strategy/482891 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:50:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the close-based stop is an exit signal. |
| 2 | PASS | MACD, RSI and a percentage stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [3.0, 1.5] x `rsi_ob` [59, 70]: **4 trials**; defaults 3 / 59 (the source's); RSI 14, the 40 level and
MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- The 3 % stop is checked on closes through `strategy.close`: an exit signal at the next open (rule 3, as #489638),
  measured from the latest signal close (`entry_price`), as written.
- REVERSAL INTENDED. State machine on the position held at each close. No stops module. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
