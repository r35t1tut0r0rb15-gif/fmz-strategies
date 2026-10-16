# #430039 均线穿越RSI金叉死叉交易策略SMA-Crossing-RSI-Golden-Cross-Death-Cross-Trading-Strategy -> `fmz_430039_rsi_recovery_below_sma200_long`

- FMZ source id: 430039 (lineage).
- Source: https://www.fmz.com/strategy/430039 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-24 14:33:51). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An RSI and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `sma_len` [200, 100]: **4 trials**; levels 30 / 70 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
