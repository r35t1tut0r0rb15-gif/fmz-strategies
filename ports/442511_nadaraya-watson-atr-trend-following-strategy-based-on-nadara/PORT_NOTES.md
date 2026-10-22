# #442511 基于Nadaraya-Watson回归和ATR通道的趋势跟踪策略Trend-Following-Strategy-Based-on-Nadaraya-Watson-Regression-and-ATR-Channel -> `fmz_442511_nadaraya_watson_atr_envelope_reversal`

- FMZ source id: 442511 (lineage).
- Source: https://www.fmz.com/strategy/442511 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 15:15:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Kernel-regression ATR envelope; closes against the fill price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`coef` [2.7, 2.0] x `atr_len` [32, 14]: **4 trials**; the kernel settings and the stop bars fixed.

## Ambiguities resolved

- Stop rule against the fill price from the held bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
