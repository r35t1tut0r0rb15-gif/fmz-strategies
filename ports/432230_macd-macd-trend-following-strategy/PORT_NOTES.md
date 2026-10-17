# #432230 MACD-趋势跟随策略MACD-Trend-Following-Strategy -> `fmz_432230_noro_macd_trend_long`

- FMZ source id: 432230 (lineage).
- Source: https://www.fmz.com/strategy/432230 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-15 17:08:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the qty-0 short stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 17]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- The qty-0 short only closes the long. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
