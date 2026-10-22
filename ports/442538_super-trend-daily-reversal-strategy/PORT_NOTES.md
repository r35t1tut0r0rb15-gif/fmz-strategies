# #442538 Super Trend Daily Reversal Strategy -> `fmz_442538_supertrend_flip_roc_filter_pct_stop`

- FMZ source id: 442538 (lineage).
- Source: https://www.fmz.com/strategy/442538 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 16:22:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed from the fill |
| 2 | PASS | SuperTrend flips with a rate-of-change filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.3, 3.0] x `sl_pct` [0.06, 0.03]: **4 trials**; the ATR period and the ROC settings fixed.

## Ambiguities resolved

- Fixed-percent stop from the fill bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
