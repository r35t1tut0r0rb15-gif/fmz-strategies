# #434677 基于kNN的趋势跟随策略kNN-based-Trend-Following-Strategy -> `fmz_434677_knn_rsi_feature_vote_sma40_atr_stop_reversal`

- FMZ source id: 434677 (lineage).
- Source: https://www.fmz.com/strategy/434677 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-08 11:33:31). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop from the fill |
| 2 | PASS | Nearest-neighbour style vote with an MA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 2 % / (2 x ATR 7), commission 0.2 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`base_k` [400, 100] x `ma_len` [40, 100]: **4 trials**; RSI 29 / 8, ATR 7 x 2.

## Ambiguities resolved

- Farthest-record "kNN" and the inverted label, as coded. ATR at the signal bar. Volume not used (RSI features). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "machine_learning_vote"`.

## Marks

`none`
