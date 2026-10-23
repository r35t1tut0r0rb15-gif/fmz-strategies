# #471664 ADX-Average-Directional-Index-和交易量趋势动态跟踪策略-ADX-Average-Directional-Index-and-Volume-Dynamic-Trend-Tracking-Strategy -> `fmz_471664_adx21_di_volume_1_8x_1h_reversal`

- FMZ source id: 471664 (lineage).
- Source: https://www.fmz.com/strategy/471664 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 11:00:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX trend strength with DI direction on high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_len` [21, 14] x `adx_min` [26.0, 20.0]: **4 trials**; volume SMA 20 x 1.8.

## Ambiguities resolved

- Always in the market after the first signal. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_trend"`.

## Marks

`none`
