# #442944 基于肯特纳通道和CCI指标的趋势过滤量化策略Trend-Filter-Quantitative-Strategy-Based-on-Keltner-Channels-and-CCI-Indicator -> `fmz_442944_keltner_cci5_rsi30_extremes_zero_exit_1h_reversal`

- FMZ source id: 442944 (lineage).
- Source: https://www.fmz.com/strategy/442944 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-27 15:47:20). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Keltner-band extremes confirmed by CCI and RSI, CCI zero-line exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kc_mult` [0.7, 1.5] x `cci_len` [5, 14]: **4 trials**; KC 30, RSI 30, levels 75 / 60.

## Ambiguities resolved

- Volume test reduces to volume > 0. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`none`
