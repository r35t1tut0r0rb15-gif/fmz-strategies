# #432092 Dual confirmation Reversal Trading Strategy -> `fmz_432092_combo_123_stoch_rsi`

- FMZ source id: 432092 (lineage).
- Source: https://www.fmz.com/strategy/432092 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-14 13:42:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A stochastic and a stochastic RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `top_band` [80, 70]: **4 trials**; LowBand = 100 - TopBand; the other lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
