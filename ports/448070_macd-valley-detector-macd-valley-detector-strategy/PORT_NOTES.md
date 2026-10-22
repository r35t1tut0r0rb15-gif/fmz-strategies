# #448070 MACD-Valley-Detector-策略-MACD-Valley-Detector-Strategy -> `fmz_448070_macd_hist_zero_cross_long_high_target_reversal`

- FMZ source id: 448070 (lineage).
- Source: https://www.fmz.com/strategy/448070 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-12 17:01:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the long target fixed on the signal bar |
| 2 | PASS | MACD histogram zero crossings with a long target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The qty 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; the signal length and the 0.3 offset fixed.

## Ambiguities resolved

- Short has no exit (its exit names the long id). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
