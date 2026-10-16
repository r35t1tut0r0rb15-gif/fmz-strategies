# #428816 Momentum Reversal Trading Strategy -> `fmz_428816_combo_123_cmofilt`

- FMZ source id: 428816 (lineage).
- Source: https://www.fmz.com/strategy/428816 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-09 17:21:27). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The price-unit filter -> an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_cmo` [9, 14] x `filter_atr` [0.02, 0.1]: **4 trials**; 123 settings and the 70 / -70 bands fixed.

## Ambiguities resolved

- Filter as an ATR multiple. Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
