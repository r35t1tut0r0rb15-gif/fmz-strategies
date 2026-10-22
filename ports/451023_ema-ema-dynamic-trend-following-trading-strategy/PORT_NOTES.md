# #451023 EMA动态趋势追踪交易策略-EMA-Dynamic-Trend-Following-Trading-Strategy -> `fmz_451023_atr_envelope_channel_edge_cross_reversal`

- FMZ source id: 451023 (lineage).
- Source: https://www.fmz.com/strategy/451023 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 11:31:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the channel from the previous bar |
| 2 | PASS | ATR envelope crossings of the channel edges |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`f` [2.382, 1.5] x `highest_len` [60, 30]: **4 trials**; the far multiplier 5.618, the lowest 30 and the EMA lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
