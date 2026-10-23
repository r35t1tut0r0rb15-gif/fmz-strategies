# #365902 72s Adaptive Hull Moving Average -> `fmz_365902_adaptive_hma172_233_slope17_volatility_reversal`

- FMZ source id: 365902 (lineage).
- Source: https://www.fmz.com/strategy/365902 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-26 17:17:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive-period Hull MA slope turns in high volatility |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`flat` [17, 10] x `min_length` [172, 100]: **4 trials**; maximum 233, adapt 3.141 %, ATR 14 / 46.

## Ambiguities resolved

- Volume not used (charger Volatility). REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
