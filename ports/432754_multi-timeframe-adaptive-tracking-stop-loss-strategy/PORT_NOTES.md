# #432754 Multi timeframe Adaptive Tracking Stop Loss Strategy -> `fmz_432754_eight_vote_score_flip_level_breakout_long`

- FMZ source id: 432754 (lineage).
- Source: https://www.fmz.com/strategy/432754 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-21 11:07:44). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Multi-indicator score with a breakout level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`macd_slow` [29, 26] x `level_pct` [0.005, 0.01]: **4 trials**; RSI 14, DMI 14, %R 14, flow 14, ATR 5 x 2.

## Ambiguities resolved

- Obfuscated helpers read as the indicators they compute; level na until the first sign change. Volume = broker tick volume.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "indicator_vote"`.

## Marks

`none`
