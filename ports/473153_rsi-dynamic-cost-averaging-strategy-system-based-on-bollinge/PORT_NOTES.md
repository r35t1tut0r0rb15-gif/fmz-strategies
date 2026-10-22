# #473153 基于布林带和RSI的动态成本平均策略系统-Dynamic-Cost-Averaging-Strategy-System-Based-on-Bollinger-Bands-and-RSI -> `fmz_473153_bb20_2p5_rsi25_75_extremes_reversal`

- FMZ source id: 473153 (lineage).
- Source: https://www.fmz.com/strategy/473153 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:37:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band and RSI extremes; per-bar target described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The unused percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.5, 2.0]: **4 trials**; the RSI levels fixed; the per-bar target pending.

## Ambiguities resolved

- No accumulation (pyramiding 1); per-bar target pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
