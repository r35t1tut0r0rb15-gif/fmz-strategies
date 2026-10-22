# #468302 RSI动量背离突破策略-RSI-Momentum-Divergence-Breakout-Strategy -> `fmz_468302_rsi_extreme_three_bar_divergence_reversal`

- FMZ source id: 468302 (lineage).
- Source: https://www.fmz.com/strategy/468302 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 14:37:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes with short divergences; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `window` [3, 5]: **4 trials**; the levels 30 / 70 fixed; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
