# #433914 基于RSI和MA均线的量化交易策略RSI-and-Moving-Average-Based-Quantitative-Trading-Strategy -> `fmz_433914_rsi_ma_contrarian_cross`

- FMZ source id: 433914 (lineage).
- Source: https://www.fmz.com/strategy/433914 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-01 14:21:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An oscillator against its own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `ma_len` [9, 21]: **4 trials**.

## Ambiguities resolved

- Contrarian crosses as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
