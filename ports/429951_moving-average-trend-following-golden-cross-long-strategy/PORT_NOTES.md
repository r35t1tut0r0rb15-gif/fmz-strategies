# #429951 Moving Average Trend Following Golden Cross Long Strategy -> `fmz_429951_macd_ema_sma_long`

- FMZ source id: 429951 (lineage).
- Source: https://www.fmz.com/strategy/429951 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-23 15:22:48). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A histogram sign and moving-average sides. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [200, 100] x `ema_len` [20, 50]: **4 trials**; MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
