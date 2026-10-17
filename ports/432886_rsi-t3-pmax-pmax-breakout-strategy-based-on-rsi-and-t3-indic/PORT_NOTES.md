# #432886 基于RSI和T3指标的PMax自适应突破策略PMax-Breakout-Strategy-Based-on-RSI-and-T3-Indicators -> `fmz_432886_pmax_on_rsi_t3`

- FMZ source id: 432886 (lineage).
- Source: https://www.fmz.com/strategy/432886 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 15:03:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI-unit bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 1.5] x `t3_len` [8, 5]: **4 trials**; RSI 14, T3 factor 0.7 and the ATR-of-RSI 10 fixed.

## Ambiguities resolved

- Coded as written (zero-seeded Wilder averages). REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
