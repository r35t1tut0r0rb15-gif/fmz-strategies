# #434159 The Great Delight Multifactor Quantitative Strategy -> `fmz_434159_cloud_ema_macd_long`

- FMZ source id: 434159 (lineage).
- Source: https://www.fmz.com/strategy/434159 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-04 13:04:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cloud position, EMA and MACD sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50] x `conv` [9, 20]: **4 trials**; base 26, span 52, SMA 200 and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Shadowed "= false" lines change nothing, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
