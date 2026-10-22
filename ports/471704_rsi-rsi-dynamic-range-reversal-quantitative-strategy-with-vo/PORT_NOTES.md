# #471704 RSI动态区间反转量化策略与波动率优化模型-RSI-Dynamic-Range-Reversal-Quantitative-Strategy-with-Volatility-Optimization-Model -> `fmz_471704_rsi14_two_setup_crossings_id_exits_long`

- FMZ source id: 471704 (lineage).
- Source: https://www.fmz.com/strategy/471704 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:55:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI threshold crossings with id-specific exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sensitivity` [3.0, 0.0] x `rsi_len` [14, 7]: **4 trials**; the 80 / 30 levels fixed.

## Ambiguities resolved

- Exits by entry id (pyramiding 1). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
