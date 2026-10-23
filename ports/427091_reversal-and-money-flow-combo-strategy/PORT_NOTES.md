# #427091 Reversal and Money Flow Combo Strategy -> `fmz_427091_combo_reversal123_volume_money_flow_reversal`

- FMZ source id: 427091 (lineage).
- Source: https://www.fmz.com/strategy/427091 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-17 22:58:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combo of a reversal pattern and a money-flow state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `slow` [10, 20]: **4 trials**; K 1, D 3, level 50, fast 3.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_reversal"`.

## Marks

`none`
