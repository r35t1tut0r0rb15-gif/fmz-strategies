# #428071 Multivariate Indicator Fusion Strategy -> `fmz_428071_vortex_rsi_roc_fusion`

- FMZ source id: 428071 (lineage).
- Source: https://www.fmz.com/strategy/428071 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-28 12:01:57). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price-unit ROC leg -> ATR(14) units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vi_pm` [4, 7] x `roc_k` [0.001, 0.1]: **4 trials**; defaults 4 / 0.001 (0.001 ATR is about the source's 0.97 USD on daily BTC, judgement before any backtest); VI smoothing 3, RSI / ROC 2 / 2 fixed.

## Ambiguities resolved

- The ROC leg's threshold is in price units (tanh(x) > 0.75); ported in ATR units.
- year >= 2018 filter dropped. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`none`
