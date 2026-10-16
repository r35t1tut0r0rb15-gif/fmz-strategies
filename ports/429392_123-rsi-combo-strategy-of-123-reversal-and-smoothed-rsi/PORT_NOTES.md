# #429392 结合123反转与平滑RSI的交易策略Combo-Strategy-of-123-Reversal-and-Smoothed-RSI -> `fmz_429392_combo_123_smoothed_rsi`

- FMZ source id: 429392 (lineage).
- Source: https://www.fmz.com/strategy/429392 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-16 16:27:32). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_rsi` [10, 20] x `top_band` [0.8, 0.7] (low band = 1 - top): **4 trials**; 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
