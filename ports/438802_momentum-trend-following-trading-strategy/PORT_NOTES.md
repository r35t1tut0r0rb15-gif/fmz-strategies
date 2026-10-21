# #438802 Momentum Trend Following Trading Strategy -> `fmz_438802_ema50_200_cross_rsi_filter`

- FMZ source id: 438802 (lineage).
- Source: https://www.fmz.com/strategy/438802 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 14:27:09). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; RSI 14 at 55 / 45 fixed.

## Ambiguities resolved

- Zone inputs always true. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
