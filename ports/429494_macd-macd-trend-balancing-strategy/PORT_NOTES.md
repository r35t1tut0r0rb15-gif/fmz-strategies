# #429494 MACD多空平衡跟踪策略MACD-Trend-Balancing-Strategy -> `fmz_429494_macd_hist_cross_stop`

- FMZ source id: 429494 (lineage).
- Source: https://www.fmz.com/strategy/429494 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-17 16:15:53). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry (arming approximation stated). |
| 2 | PASS | A sign cross and a percentage. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored; the stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`macd_length` [12, 9] x `sl_pct` [5.0, 2.5]: **4 trials**; MACD 12 / 26 fixed.

## Ambiguities resolved

- Stop arming approximated. REVERSAL INTENDED. Mark coarse_bar_stop. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
