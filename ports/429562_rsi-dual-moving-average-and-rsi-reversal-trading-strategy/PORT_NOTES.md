# #429562 双移动均线与RSI反转交易策略Dual-Moving-Average-and-RSI-Reversal-Trading-Strategy -> `fmz_429562_rsi30_vwma30_200_trend_pullback_reversal`

- FMZ source id: 429562 (lineage).
- Source: https://www.fmz.com/strategy/429562 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-18 11:08:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI pullbacks in a VWMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_long` [53.0, 40.0] x `rsi_short` [60.0, 70.0]: **4 trials**; RSI 30, VWMA 30 / 200.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
