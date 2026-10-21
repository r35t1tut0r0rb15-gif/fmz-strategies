# #438773 Robust Trend Tracking Strategy -> `fmz_438773_reversal123_smart_money_index_combo`

- FMZ source id: 438773 (lineage).
- Source: https://www.fmz.com/strategy/438773 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 11:52:53). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed days |
| 2 | PASS | Close patterns, stochastic and a running bar-body index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_smi` [18, 36]: **4 trials**; K smoothing 1, D 3, level 50 fixed.

## Ambiguities resolved

- Daily values two broker days back; running index per bar as written. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
