# #473395 基于OBV-SMA交叉和RSI过滤的多维度动量交易策略-OBV-SMA-Crossover-with-RSI-Filter-Multi-Dimensional-Momentum-Trading-Strategy -> `fmz_473395_obv_sma20_cross_rsi_2_4pct_bracket_reversal`

- FMZ source id: 473395 (lineage).
- Source: https://www.fmz.com/strategy/473395 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:31:19). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | OBV / SMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`obv_len` [20, 50] x `sl` [0.02, 0.03]: **4 trials**; RSI 14, TP 4 %.

## Ambiguities resolved

- Bracket at the signal close. Volume = broker tick volume (OBV). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "obv"`.

## Marks

`coarse_bar_stop`
