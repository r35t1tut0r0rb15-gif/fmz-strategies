# #439963 基于EMA均线和MACD指标的BTC交易策略EMA-and-MACD-Based-BTC-Trading-Strategy -> `fmz_439963_ema18_diff_turn_extreme_macd`

- FMZ source id: 439963 (lineage).
- Source: https://www.fmz.com/strategy/439963 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-25 12:54:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed from the fill |
| 2 | ADAPT | Price-unit thresholds -> fractions of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity amount stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`scale` [42000.0, 21000.0] x `ema_len` [18, 50]: **4 trials**; the five price-unit thresholds read at the scale.

## Ambiguities resolved

- Price-unit thresholds read as fractions at a BTC scale. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
