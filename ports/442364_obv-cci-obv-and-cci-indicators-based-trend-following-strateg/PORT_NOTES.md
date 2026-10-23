# #442364 基于OBV和CCI指标的趋势追踪策略OBV-and-CCI-Indicators-Based-Trend-Following-Strategy -> `fmz_442364_obv_ema13_cross_cci_coded_reversal`

- FMZ source id: 442364 (lineage).
- Source: https://www.fmz.com/strategy/442364 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-21 14:05:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | OBV / EMA crossings coded by the CCI sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [20, 14] x `ema_len` [13, 26]: **4 trials**; CCI threshold 0.

## Ambiguities resolved

- CCI sign coding as written. Volume = broker tick volume (OBV). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "obv"`.

## Marks

`none`
