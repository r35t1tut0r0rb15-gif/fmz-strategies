# #430896 Dual Signal Trend Tracking Strategy -> `fmz_430896_combo_2_20_ema_ac`

- FMZ source id: 430896 (lineage).
- Source: https://www.fmz.com/strategy/430896 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 17:02:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA and oscillator states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430896. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `wma_len` [15, 5]: **4 trials**; AC 5 / 34 fixed.

## Ambiguities resolved

- WMA signal (the default). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
