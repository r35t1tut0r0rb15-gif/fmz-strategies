# #430850 RSI敢死队融合策略RSI-Daredevil-Squadron-Fusion-Strategy -> `fmz_430850_rsi_divergence_cloud_ema200`

- FMZ source id: 430850 (lineage).
- Source: https://www.fmz.com/strategy/430850 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 14:52:03). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed after their right bars. |
| 2 | PASS | RSI divergences, channel midpoints and an EMA. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lb` [5, 3] x `tp_long` [75, 70]: **4 trials**; left = right pivot bars; the short level 25 and the cloud / EMA fixed.

## Ambiguities resolved

- Short close on a cross up through 25, as written. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks

`none`
