# #440298 基于Stoch-RSI和MFI的量化交易策略Quantitative-Trading-Strategy-Based-on-Stoch-RSI-and-MFI -> `fmz_440298_stoch_rsi11_and_volume_mfi_cross_reversal`

- FMZ source id: 440298 (lineage).
- Source: https://www.fmz.com/strategy/440298 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 10:11:14). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic-RSI and volume-MFI threshold crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [20.0, 30.0] x `overbought` [70.0, 80.0]: **4 trials**; RSI 11, windows 11 / 7, MFI 14.

## Ambiguities resolved

- Stochastic windows and the MFI of volume as written; later call wins. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_rsi"`.

## Marks

`none`
