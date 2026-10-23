# #430839 基于StochRSI和交易量的多空策略Stochastic-RSI-and-Volume-Based-Trading-Strategy -> `fmz_430839_stoch_rsi_kd_flip_volume_candle_reversal`

- FMZ source id: 430839 (lineage).
- Source: https://www.fmz.com/strategy/430839 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 14:12:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic-RSI cross with volume confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_rsi` [14, 21] x `vol_len` [7, 20]: **4 trials**; stochastic 14, K 3, D 3.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_rsi"`.

## Marks

`none`
