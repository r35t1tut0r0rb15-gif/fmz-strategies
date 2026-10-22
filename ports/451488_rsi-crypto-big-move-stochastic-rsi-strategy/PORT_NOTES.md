# #451488 加密货币大幅波动随机RSI策略-Crypto-Big-Move-Stochastic-RSI-Strategy -> `fmz_451488_big_move_stoch_rsi_extreme_reversal`

- FMZ source id: 451488 (lineage).
- Source: https://www.fmz.com/strategy/451488 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 10:27:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stoch RSI extremes after big moves |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [24, 12] x `move_pct` [2.5, 4.0]: **4 trials**; the RSI / stochastic lengths and the 3 / 97 levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
