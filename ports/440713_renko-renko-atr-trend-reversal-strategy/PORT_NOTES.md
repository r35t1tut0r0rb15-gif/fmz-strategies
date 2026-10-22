# #440713 基于Renko平均真实波幅的趋势反转策略Renko-ATR-Trend-Reversal-Strategy -> `fmz_440713_atr_renko_reversal_bracket`

- FMZ source id: 440713 (lineage).
- Source: https://www.fmz.com/strategy/440713 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-01 14:30:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C139). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | ATR Renko levels from past prices |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital, quantity and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 20] x `sl_pct` [3.0, 1.5]: **4 trials**; target 20 % fixed.

## Ambiguities resolved

- Bricks from 0 as written; levels from the Renko open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "renko_bricks"`.

## Marks

`none`
