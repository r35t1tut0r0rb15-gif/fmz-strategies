# #448772 ZeroLag-MACD-多空策略-ZeroLag-MACD-Long-Short-Strategy -> `fmz_448772_zero_lag_macd_signal_cross_reversal`

- FMZ source id: 448772 (lineage).
- Source: https://www.fmz.com/strategy/448772 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-18 17:06:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Zero-lag MACD signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; the signal length fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
