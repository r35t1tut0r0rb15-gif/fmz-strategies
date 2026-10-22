# #439899 双向EMA交叉量化交易策Bidirectional-EMA-Cross-Quant-Trading-Strategy -> `fmz_439899_investoz_ema21_371_cross_long`

- FMZ source id: 439899 (lineage).
- Source: https://www.fmz.com/strategy/439899 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 17:31:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1` [21, 50] x `ema7` [371, 200]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
