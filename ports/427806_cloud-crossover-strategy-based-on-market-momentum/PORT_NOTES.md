# #427806 Cloud Crossover Strategy Based on Market Momentum -> `fmz_427806_chikou_base_line_cross`

- FMZ source id: 427806 (lineage).
- Source: https://www.fmz.com/strategy/427806 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-25 17:28:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.
- Near-duplicate group: **ND427806** (2 members, best partner #429786, Jaccard 0.658); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Channel lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427806. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`base_periods` [26, 52] x `lag` [26, 13]: **4 trials**; defaults 26 / 26 (the source's; the lag is hard-coded in the cross).

## Ambiguities resolved

- Conversion line and cloud drawn only; the displacement input does not reach the orders.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
