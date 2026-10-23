# #446435 AlphaTrend和布林带相结合的均值回归趋势跟踪策略AlphaTrend-and-Bollinger-Bands-Combined-Mean-Reversion-Trend-Following-Strategy -> `fmz_446435_alphatrend_turn_bollinger_breakout_reversal`

- FMZ source id: 446435 (lineage).
- Source: https://www.fmz.com/strategy/446435 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 16:32:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts on AlphaTrend turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ap` [14, 21] x `bb_mult` [2.0, 1.5]: **4 trials**; ATR SMA 20, BB 20.

## Ambiguities resolved

- Exits never act (wrong entry ids). Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
