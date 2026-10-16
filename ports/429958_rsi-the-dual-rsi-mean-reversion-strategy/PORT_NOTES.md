# #429958 双向RSI均线回复策略The-Dual-RSI-Mean-Reversion-Strategy -> `fmz_429958_rsi_extreme_ha_turn`

- FMZ source id: 429958 (lineage).
- Source: https://www.fmz.com/strategy/429958 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-23 15:46:33). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and candle colours only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 100 and the lot formula stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_limit` [30, 20] x `rsi_bars` [3, 5]: **4 trials**; RSI 14 and the 2-bar colour filter fixed.

## Ambiguities resolved

- Adds not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
