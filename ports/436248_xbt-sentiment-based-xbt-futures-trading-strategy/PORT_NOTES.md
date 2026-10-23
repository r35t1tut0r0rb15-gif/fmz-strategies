# #436248 基于情绪的XBT期货交易策略Sentiment-Based-XBT-Futures-Trading-Strategy -> `fmz_436248_expected_range_sentiment_delta_peak_reversal`

- FMZ source id: 436248 (lineage).
- Source: https://www.fmz.com/strategy/436248 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-22 14:48:44). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop from the fill; run-up target in the signals |
| 2 | PASS | Expected-range sentiment delta peaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity / close x leverage (1), not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` [0.70, 0.50] x `tp` [53.0, 20.0]: **4 trials**; short level 0.68, SL 7 %.

## Ambiguities resolved

- Stop anchored on the fill price (script: fill-bar close). Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "sentiment_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
