# #442839 The Dual Quant Trading System -> `fmz_442839_ema_trend_cci_rsi_cross_session`

- FMZ source id: 442839 (lineage).
- Source: https://www.fmz.com/strategy/442839 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 14:30:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit trail -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [9, 5] x `cci_len` [20, 14]: **4 trials**; the RSI lengths, the trail and the session fixed.

## Ambiguities resolved

- Price-unit trail as a fraction; session on the UTC bar open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
