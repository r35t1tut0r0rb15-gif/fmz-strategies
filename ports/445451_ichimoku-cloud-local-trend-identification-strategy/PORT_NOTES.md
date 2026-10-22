# #445451 Ichimoku Cloud Local Trend Identification Strategy -> `fmz_445451_lead_lines_17_39_order_reversal`

- FMZ source id: 445451 (lineage).
- Source: https://www.fmz.com/strategy/445451 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-19 15:10:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; no displacement in the rules |
| 2 | PASS | Leading-line order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ppl1` [17, 9] x `ppl2` [39, 26]: **4 trials**; the 9 / 26 / 52 lengths fixed.

## Ambiguities resolved

- Undisplaced leading lines. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
