# #452829 Ichimoku-Kumo交易策略Ichimoku-Kumo-Trading-Strategy -> `fmz_452829_kumo_setup_reentry_atr_trail_close_reversal`

- FMZ source id: 452829 (lineage).
- Source: https://www.fmz.com/strategy/452829 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 17:23:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the close-based trailing exit in a loop |
| 2 | PASS | Cloud re-entries after a set-up |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing, margin and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`setup_lookback` [50, 10] x `trail_atr` [3.0, 2.0]: **4 trials**; the Ichimoku lengths and ATR 5 fixed.

## Ambiguities resolved

- Close-based trail in a loop, reset on each signal. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
