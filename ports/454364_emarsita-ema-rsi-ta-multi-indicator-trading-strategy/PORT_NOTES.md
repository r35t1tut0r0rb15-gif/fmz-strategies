# #454364 EMARSITA多重指标交易策略-EMA-RSI-TA-Multi-Indicator-Trading-Strategy -> `fmz_454364_ema4_12_cross_ema48_rsi_filter_reversal`

- FMZ source id: 454364 (lineage).
- Source: https://www.fmz.com/strategy/454364 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-06-17 16:38:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with trend and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [4, 9] x `long_len` [12, 21] x `trend_len` [48, 200]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
