# #434434 Dual Moving Average Crossover Trend Strategy -> `fmz_434434_macd_cross_ema_sma_bracket`

- FMZ source id: 434434 (lineage).
- Source: https://www.fmz.com/strategy/434434 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-06 11:52:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent exits fixed at entry (approximation stated) |
| 2 | PASS | MACD crosses, average filters and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `tp_pct` [0.02, 0.04]: **4 trials**; MACD 12 / 26 / 9, SMA 100 and the 1 % stop fixed.

## Ambiguities resolved

- Close-sized exits fixed at the fill (trailing_stop_pending). Date window dropped. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
