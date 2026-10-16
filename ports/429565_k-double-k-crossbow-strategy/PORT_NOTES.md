# #429565 双K弹弓策略Double-K-Crossbow-Strategy -> `fmz_429565_combo_123_special_k`

- FMZ source id: 429565 (lineage).
- Source: https://www.fmz.com/strategy/429565 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-18 11:19:07). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and percentage rates of change. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `smooth` [10, 20]: **4 trials**; the Special K ROC table fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
