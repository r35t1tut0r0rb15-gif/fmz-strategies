# #435100 EMA MACD Quantitative Strategy With Dual Track Running and Leading the Market Index -> `fmz_435100_ema_cross_macd_sign`

- FMZ source id: 435100 (lineage).
- Source: https://www.fmz.com/strategy/435100 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 12:13:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses and a MACD sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [25, 10] x `len2` [50, 100]: **4 trials**; MACD 12 / 26 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
