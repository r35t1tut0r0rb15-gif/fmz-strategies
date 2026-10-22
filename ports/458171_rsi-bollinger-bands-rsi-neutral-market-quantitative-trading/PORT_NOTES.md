# #458171 布林带RSI中性市场量化交易策略Bollinger-Bands-RSI-Neutral-Market-Quantitative-Trading-Strategy -> `fmz_458171_bb20_band_cross_rsi_confirm_reversal`

- FMZ source id: 458171 (lineage).
- Source: https://www.fmz.com/strategy/458171 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 15:47:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band crossings with RSI confirmation; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [20, 50] x `bb_mult` [2.0, 1.5] x `rsi_len` [14, 7]: **8 trials**; the RSI levels fixed; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
