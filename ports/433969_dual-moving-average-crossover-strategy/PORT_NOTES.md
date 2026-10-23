# #433969 Dual Moving Average Crossover Strategy -> `fmz_433969_sma6_vwma7_high_cross_mrsi_cross_15m_reversal`

- FMZ source id: 433969 (lineage).
- Source: https://www.fmz.com/strategy/433969 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-01 18:18:16). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average and RSI-EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [6, 10] x `slow_len` [7, 14]: **4 trials**; RSI 50, EMA 2, 32.6 / 63.

## Ambiguities resolved

- Later call wins on a two-sided bar. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
